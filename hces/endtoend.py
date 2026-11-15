"""Stage 05: Claude answers each question from the gated context and from the whole book; a blind grader scores both.

  python -m hces.endtoend --estimate                  token counts and cost, no spend
  python -m hces.endtoend --answer --yes --cap 22     both arms, every question, plain shape
  python -m hces.endtoend --grade --yes               blind grading of every stored answer
  python -m hces.endtoend --report                    writes output/end-to-end.md

Gated arm: RAG + JEV with the frozen cutoffs (judge arm, hybrid k 50, budget 6000). When nothing is
kept, code answers "not in the documents" and Claude is not called. Full arm: the whole plain.txt
(needles included), cached once per book. Both arms get the same instructions. The grader sees the
question, the reference answer and the gold passages, and one answer at a time in shuffled order; it
never sees which arm wrote it. Needs ANTHROPIC_API_KEY.
"""

from __future__ import annotations

import argparse
import json
import random
import statistics
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from hces import passages as P
from hces.exam import VOLUMES, cases
from hces.exam import output_dir as exam_dir
from hces.rag import key_rows
from hces.rollup import Cutoffs, fill

SHAPE = "plain"
ARMS = ("gated", "full")
NOT_IN_DOCS = "not in the documents"
FALLBACK_BETA = "server-side-fallback-2026-07-01"
# USD per million tokens: input, output, cache write (5 min), cache read
PRICES = {"claude-opus-5-5": (4.00, 20.00, 5.00, 0.20), "claude-sonnet-5-5": (2.00, 10.00, 2.50, 0.20)}
INSTRUCTIONS = (
    "You answer questions about a novel using only the text you are given. "
    "Answer in one or two sentences. Quote names and details exactly as the text gives them. "
    f"If the text does not state the answer, reply exactly: {NOT_IN_DOCS}. Do not guess or use outside knowledge."
)
GRADER = (
    "You grade one answer to a question about a novel. You get the question, the reference answer, and the "
    "passages that hold it. Verdicts: correct (matches the reference in substance), partial (right in part, or "
    "right but with a wrong extra claim), wrong (contradicts or misses the reference), abstained (says the "
    "answer is not in the documents or declines). For a question the documents cannot answer, the reference "
    "says so: then abstained is the right answer and any specific claim is wrong."
)
VERDICT_SCHEMA = {"type": "object", "additionalProperties": False, "required": ["verdict", "reason"],
                  "properties": {"verdict": {"type": "string", "enum": ["correct", "partial", "wrong", "abstained"]},
                                 "reason": {"type": "string"}}}


def output_dir() -> Path:
    from hces.config import ROOT

    return ROOT / "workspaces" / "hces-lab" / "stages" / "05-end-to-end" / "output"


def book(slug: str) -> str:
    return (P.volumes_dir() / slug / "plain.txt").read_text(encoding="utf-8")


def cost(model: str, u: dict) -> float:
    i, o, w, r = PRICES[model]
    return (u["input"] * i + u["output"] * o + u["cache_write"] * w + u["cache_read"] * r) / 1e6


def usage(resp) -> dict:
    u = resp.usage
    return {"input": u.input_tokens, "output": u.output_tokens,
            "cache_write": u.cache_creation_input_tokens or 0, "cache_read": u.cache_read_input_tokens or 0}


def gated_sets(store, cfg) -> dict[str, list[dict]]:
    """Kept passages per question, plain shape, frozen cutoffs; text attached."""
    frozen = Cutoffs(**json.loads((exam_dir() / "cutoffs.json").read_text(encoding="utf-8"))["cutoffs"])
    out = {}
    for slug in VOLUMES:
        texts = {r["id"]: r["text"] for r in P.load_passages(slug, SHAPE)}
        for x in cases(store, slug) + cases(store, slug, fresh=True):
            if x["shape"] != SHAPE:
                continue
            kept = [u for u, _ in fill(x["units"], cfg.token_budget, frozen)[0]]
            out[x["id"]] = [{"id": u.unit_id, "tokens": u.tokens, "text": texts[u.unit_id]} for u in kept]
    return out


def full_request(model: str, slug: str, text: str, question: str) -> dict:
    return {"model": model, "max_tokens": 4000, "output_config": {"effort": "low"},
            "system": [{"type": "text", "text": INSTRUCTIONS},
                       {"type": "text", "text": f"<novel>\n{text}\n</novel>", "cache_control": {"type": "ephemeral"}}],
            "messages": [{"role": "user", "content": question}]}


def gated_request(model: str, kept: list[dict], question: str) -> dict:
    body = "\n\n".join(f"<passage id=\"{k['id']}\">\n{k['text']}\n</passage>" for k in kept)
    return {"model": model, "max_tokens": 4000, "output_config": {"effort": "low"},
            "system": [{"type": "text", "text": INSTRUCTIONS}],
            "messages": [{"role": "user", "content": f"{body}\n\nQuestion: {question}"}]}


def ask(client, req: dict) -> tuple[str, dict, float, str, str]:
    t0 = time.perf_counter()
    resp = client.beta.messages.create(**req, betas=[FALLBACK_BETA], fallbacks="default")
    ms = (time.perf_counter() - t0) * 1000
    text = "".join(b.text for b in resp.content if b.type == "text").strip()
    return text, usage(resp), ms, resp.stop_reason, resp.model


def estimate(client, model: str, gated: dict) -> int:
    total = 0.0
    lines = []
    for slug in VOLUMES:
        qs = key_rows(slug)
        n = client.messages.count_tokens(**{k: v for k, v in full_request(model, slug, book(slug), "?").items()
                                            if k in ("model", "system", "messages")}).input_tokens
        g = sum(sum(k["tokens"] for k in gated[q["id"]]) for q in qs)
        calls = sum(1 for q in qs if gated[q["id"]])
        i, o, w, r = PRICES[model]
        full = (n * w + (len(qs) - 1) * n * r + len(qs) * 600 * o) / 1e6
        gate = (g * 1.3 * i + calls * 600 * o) / 1e6
        grade = (2 * len(qs) * 2500 * i + 2 * len(qs) * 300 * o) / 1e6
        total += full + gate + grade
        lines.append(f"{slug}: {len(qs)} questions, book {n:,} tokens, full ${full:.2f}, gated ${gate:.2f}, grading ${grade:.2f}")
    print("\n".join(lines) + f"\nmodel {model}, estimated total ${total:.2f} (600 output tokens per answer assumed)")
    return 0


def answer(client, model: str, gated: dict, cap: float) -> int:
    out = output_dir() / "answers.jsonl"
    out.parent.mkdir(parents=True, exist_ok=True)
    done = {(r["id"], r["arm"]) for r in map(json.loads, out.read_text(encoding="utf-8").splitlines())} if out.exists() else set()
    spent = sum(r["cost"] for r in map(json.loads, out.read_text(encoding="utf-8").splitlines())) if out.exists() else 0.0

    def record(row: dict) -> None:
        nonlocal spent
        spent += row["cost"]
        with open(out, "a", encoding="utf-8", newline="\n") as f:
            f.write(json.dumps(row) + "\n")
        print(row["id"], row["arm"], f"{row['ms']:.0f} ms ${row['cost']:.4f} total ${spent:.2f} |", row["answer"][:80], flush=True)
        if spent > cap:
            raise SystemExit(f"Spend ${spent:.2f} passed the cap ${cap:.2f}; stopped")

    def run(q: dict, arm: str, req: dict | None) -> dict:
        if req is None:
            return {"id": q["id"], "arm": arm, "answer": NOT_IN_DOCS, "usage": None, "ms": 0.0, "cost": 0.0,
                    "stop": "no_call", "model": None, "kept": 0}
        text, u, ms, stop, served = ask(client, req)
        if stop == "refusal":
            raise RuntimeError(f"{q['id']} {arm}: refused even after fallback")
        return {"id": q["id"], "arm": arm, "answer": text, "usage": u, "ms": ms, "cost": cost(model, u),
                "stop": stop, "model": served, "kept": len(gated[q["id"]]) if arm == "gated" else None}

    for slug in VOLUMES:
        qs = key_rows(slug)
        for q in qs:
            if (q["id"], "gated") not in done:
                kept = gated[q["id"]]
                record(run(q, "gated", gated_request(model, kept, q["question"]) if kept else None))
        text = book(slug)
        todo = [q for q in qs if (q["id"], "full") not in done]
        if not todo:
            continue
        record(run(todo[0], "full", full_request(model, slug, text, todo[0]["question"])))  # writes the cache
        with ThreadPoolExecutor(max_workers=4) as pool:  # the rest read it within the 5 minute window
            for row in pool.map(lambda q: run(q, "full", full_request(model, slug, text, q["question"])), todo[1:]):
                record(row)
    print(f"done, spent ${spent:.2f}")
    return 0


def gold_text(q: dict) -> str:
    texts = {r["id"]: r["text"] for r in P.load_passages(q["volume"], SHAPE)}
    return "\n\n".join(texts[g] for g in q["gold"][SHAPE])


def grade(client, model: str) -> int:
    answers = [json.loads(l) for l in (output_dir() / "answers.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
    out = output_dir() / "grades.jsonl"
    done = {r["uid"] for r in map(json.loads, out.read_text(encoding="utf-8").splitlines())} if out.exists() else set()
    keys = {q["id"]: q for slug in VOLUMES for q in key_rows(slug)}
    rng = random.Random(5)
    for a in answers:
        a["uid"] = f"{a['id']}#{a['arm']}"
    rng.shuffle(answers)
    spent = 0.0
    for a in answers:
        if a["uid"] in done:
            continue
        q = keys[a["id"]]
        ref = q["answer"] if q["answerable"] else "The documents do not contain this. The right answer says it is not in the documents."
        evidence = gold_text(q) if q["answerable"] else "(none)"
        prompt = (f"Question: {q['question']}\n\nReference answer: {ref}\n\nPassages holding the answer:\n{evidence}"
                  f"\n\nAnswer to grade:\n{a['answer']}")
        if a["uid"] in prompt or f"arm: {a['arm']}" in prompt:  # built only from key fields and the answer text
            raise RuntimeError(f"{a['uid']}: grader prompt carries the arm label")
        t0 = time.perf_counter()
        resp = client.messages.create(model=model, max_tokens=2000, output_config={
            "effort": "low", "format": {"type": "json_schema", "schema": VERDICT_SCHEMA}},
            system=GRADER, messages=[{"role": "user", "content": prompt}])
        if resp.stop_reason == "refusal":
            raise RuntimeError(f"{a['uid']}: grader refused")
        v = json.loads(next(b.text for b in resp.content if b.type == "text"))
        u = usage(resp)
        spent += cost(model, u)
        row = {"uid": a["uid"], "verdict": v["verdict"], "reason": v["reason"], "cost": cost(model, u),
               "ms": (time.perf_counter() - t0) * 1000}
        with open(out, "a", encoding="utf-8", newline="\n") as f:
            f.write(json.dumps(row) + "\n")
        print(a["uid"], v["verdict"], f"total ${spent:.2f}", flush=True)
    return 0


def points(verdict: str, answerable: bool) -> float:
    if not answerable:
        return 1.0 if verdict == "abstained" else 0.0
    return {"correct": 1.0, "partial": 0.5}.get(verdict, 0.0)


def report() -> int:
    answers = {f"{r['id']}#{r['arm']}": r for r in map(json.loads, (output_dir() / "answers.jsonl").read_text(encoding="utf-8").splitlines())}
    grades = {r["uid"]: r for r in map(json.loads, (output_dir() / "grades.jsonl").read_text(encoding="utf-8").splitlines())}
    keys = {q["id"]: q for slug in VOLUMES for q in key_rows(slug)}
    missing = sorted(set(answers) - set(grades))
    if missing:
        raise SystemExit(f"{len(missing)} answers have no grade, e.g. {missing[:3]}")
    lines = ["# Stage 05 End to End", "",
             "Plain shape, every question. Gated: frozen RAG + JEV kept set (6000 budget). Full: the whole book. "
             "Same instructions for both. Blind grading, one answer at a time in shuffled order. "
             "Points: correct 1, partial 0.5; on unanswerable questions only an abstention scores.", "",
             "| Volume | Arm | Answerable score | Correct | Partial | Wrong | Abstained on answerable | Unanswerable abstained "
             "| Median ms | Slowest 10% ms | Cost |",
             "|--------|-----|------------------|---------|---------|-------|-------------------------|------------------------"
             "|-----------|----------------|------|"]
    for slug in VOLUMES + ("all",):
        for arm in ARMS:
            rs = [(answers[u], grades[u], keys[answers[u]["id"]]) for u in answers
                  if answers[u]["arm"] == arm and (slug == "all" or keys[answers[u]["id"]]["volume"] == slug)]
            ans = [(a, g) for a, g, q in rs if q["answerable"]]
            un = [(a, g) for a, g, q in rs if not q["answerable"]]
            score = sum(points(g["verdict"], True) for _, g in ans)
            count = lambda v, xs: sum(g["verdict"] == v for _, g in xs)  # noqa: E731
            ms = sorted(a["ms"] for a, _, _ in rs)
            p90 = ms[min(len(ms) - 1, int(round(0.9 * (len(ms) - 1))))] if ms else 0.0
            lines.append(f"| {slug} | {arm} | {score:g} of {len(ans)} ({100 * score / len(ans):.0f}%) | {count('correct', ans)} "
                         f"| {count('partial', ans)} | {count('wrong', ans)} | {count('abstained', ans)} "
                         f"| {count('abstained', un)} of {len(un)} | {statistics.median(ms):.0f} | {p90:.0f} "
                         f"| ${sum(a['cost'] for a, _, _ in rs):.2f} |")
    lines += ["", "## Where the arms disagree", "", "| Question | Gated | Full | Gated answer | Full answer |",
              "|----------|-------|------|--------------|-------------|"]
    for qid, q in keys.items():
        g, f = grades.get(f"{qid}#gated"), grades.get(f"{qid}#full")
        if g and f and points(g["verdict"], q["answerable"]) != points(f["verdict"], q["answerable"]):
            clean = lambda s: " ".join(s.split()).replace("|", "/")[:160]  # noqa: E731
            lines.append(f"| {qid} | {g['verdict']} | {f['verdict']} | {clean(answers[qid + '#gated']['answer'])} "
                         f"| {clean(answers[qid + '#full']['answer'])} |")
    grade_cost = sum(g["cost"] for g in grades.values())
    lines += ["", f"Grading cost ${grade_cost:.2f}. Answering cost ${sum(a['cost'] for a in answers.values()):.2f}."]
    (output_dir() / "end-to-end.md").write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print("\n".join(lines))
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="python -m hces.endtoend")
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument("--estimate", action="store_true")
    mode.add_argument("--answer", action="store_true")
    mode.add_argument("--grade", action="store_true")
    mode.add_argument("--report", action="store_true")
    ap.add_argument("--model", default="claude-opus-5-5", choices=sorted(PRICES))
    ap.add_argument("--yes", action="store_true", help="required for --answer and --grade: they spend API credit")
    ap.add_argument("--cap", type=float, default=22.0, help="stop answering once spend passes this (USD)")
    a = ap.parse_args(argv)
    if a.report:
        return report()
    if (a.answer or a.grade) and not a.yes:
        raise SystemExit("This spends Claude API credit; pass --yes")
    import anthropic

    from hces.config import load
    from hces.store import Store

    client = anthropic.Anthropic()
    if a.grade:
        return grade(client, a.model)
    cfg = load()
    gated = gated_sets(Store(cfg.results_store), cfg)
    return estimate(client, a.model, gated) if a.estimate else answer(client, a.model, gated, a.cap)


if __name__ == "__main__":
    raise SystemExit(main())
