"""Stage 05 step 4: the HCES gate on instruction files, scored by section.

  python -m hces.instr --key                       resolve evidence quotes to gold sections, audit
  python -m hces.instr --judge --yes --cap 0.5     JEV judges every section for every question
  python -m hces.instr --retrieval                 hybrid ranking (local), then every arm at 2000 and 6000 tokens
  python -m hces.instr --answer --yes --cap 4      Opus 5.5 answers from gated sections (6000) and from all files
  python -m hces.instr --grade --yes               blind grading
  python -m hces.instr --report                    instr-end-to-end.md

Cutoffs are the frozen book cutoffs from stage 04, unchanged: this measures whether they carry over.
Questions and evidence quotes live in output/instructions/questions.jsonl; code resolves each quote to
every section that contains it. alt_evidence quotes mark the same answer stated in other files: they count
as gold but are not required for "every quote".
"""

from __future__ import annotations

import argparse
import json
import random
import statistics
import time

from hces import sections as S
from hces.endtoend import FALLBACK_BETA, NOT_IN_DOCS, VERDICT_SCHEMA, cost, points, usage
from hces.exam import output_dir as exam_dir
from hces.rollup import Cutoffs, fill
from hces.rubric import for_question

ARM = "instr-judge"
VARIANT = "sections"
K = 50
BUDGETS = (2000, 6000)
ANSWER_BUDGET = 6000
MODEL = "claude-opus-5-5"
INSTRUCTIONS = (
    "You answer questions about a set of workspace instruction files using only the text you are given. "
    "Answer in one or two sentences, quoting values exactly as the files give them. "
    f"If the text does not state the answer, reply exactly: {NOT_IN_DOCS}. Do not guess or use outside knowledge."
)
GRADER = (
    "You grade one answer to a question about a set of workspace instruction files. You get the question, the "
    "reference answer, and the sections that hold it. Verdicts: correct (matches the reference in substance), "
    "partial (right in part, or right with a wrong extra claim), wrong (contradicts or misses the reference), "
    "abstained (says it is not in the documents or declines). For a question the files cannot answer, the "
    "reference says so: then abstained is the right answer and any specific claim is wrong."
)


def norm(s: str) -> str:
    return " ".join(s.split())


def questions() -> list[dict]:
    path = S.output_dir() / "questions.jsonl"
    return [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]


def key(units: list[dict] | None = None) -> list[dict]:
    """Questions with gold section ids per evidence quote. Fails if a quote matches nothing."""
    units = units or S.load()
    out = []
    for q in questions():
        per_quote = []
        for e in q["evidence"]:
            hits = {u["id"] for u in units if norm(e) in norm(u["text"])}
            if not hits:
                raise ValueError(f"{q['id']}: evidence quote matches no section: {e!r}")
            per_quote.append(hits)
        if q["answerable"] != bool(per_quote):
            raise ValueError(f"{q['id']}: answerable={q['answerable']} but {len(per_quote)} evidence quotes")
        alt = set()
        for e in q.get("alt_evidence", []):  # same answer stated elsewhere: counts as gold, not required
            hits = {u["id"] for u in units if norm(e) in norm(u["text"])}
            if not hits:
                raise ValueError(f"{q['id']}: alternative quote matches no section: {e!r}")
            alt |= hits
        out.append({**q, "gold_by_quote": per_quote, "gold": set().union(alt, *per_quote)})
    return out


def rubric(q: dict):
    return for_question(q["id"], q["question"], q["fact"], q["topic"])


def frozen() -> Cutoffs:
    return Cutoffs(**json.loads((exam_dir() / "cutoffs.json").read_text(encoding="utf-8"))["cutoffs"])


def judge(store, cfg, cap: float) -> int:
    from hces.judge import JevJudge
    from hces.judge_all import done_pairs
    from hces.store import new_run_id
    from hces.timing import RunClock
    from hces.units import Unit

    units = [Unit(u["id"], u["text"], source="instructions", tokens=u["tokens"]) for u in S.load()]
    qs = key()
    done = done_pairs(store, ARM)
    judge_ = JevJudge(cfg.jev_model, cfg.judge_workers, cfg.price_per_million, cfg.state_cap_question)
    spent = 0.0
    for i, q in enumerate(qs):
        if (q["id"], VARIANT) in done:
            continue
        rub = rubric(q)
        store.add_rubric(rub)
        run_id, started = new_run_id(), time.time()
        with RunClock() as clock:
            with clock.span("access"):
                batch = units
            with clock.span("analysis"):
                judgments = judge_.judge(q["question"], rub, batch)
            with clock.span("response"):
                store.add_judgments(run_id, rub, judgments)
        tokens = sum(j.tokens_in or 0 for j in {j.unit_id: j for j in judgments}.values())
        c = tokens * cfg.price_per_million / 1e6
        failed = len({j.unit_id for j in judgments if j.failed})
        store.add_run({"run_id": run_id, "arm": ARM, "variant": VARIANT, "k": len(batch), "question_id": q["id"],
                       "budget": cfg.token_budget, "judge_model": cfg.jev_model, "rubric_id": rub.rubric_id,
                       "rubric_version": rub.version, "access_ms": clock.ms["access"], "analysis_ms": clock.ms["analysis"],
                       "response_ms": clock.ms["response"], "peak_rss_mb": clock.peak_rss_mb, "tokens_in": tokens,
                       "cost_usd": c, "started_at": started, "notes": {"requests": len(batch), "failed_units": failed}})
        spent += c
        print(json.dumps({"question": q["id"], "failed": failed, "tokens": tokens, "cost": round(c, 4),
                          "spent": round(spent, 4), "analysis_s": round(clock.ms["analysis"] / 1000, 1)}), flush=True)
        if failed > len(batch) // 10:
            raise SystemExit(f"{failed} of {len(batch)} requests failed on {q['id']}; stopping")
        if spent / (i + 1) * len(qs) > cap:
            raise SystemExit(f"Projected spend passes the ${cap:.2f} cap; stopping")
    print(json.dumps({"done": True, "spent": round(spent, 4)}))
    return 0


def rankings(cfg) -> dict[str, list[str]]:
    """Hybrid top-K per question over a local index of the sections (built once, no JEV)."""
    from hces.embed import FastEmbedder
    from hces.retrieve import Index
    from hces.units import Unit

    path = S.output_dir() / "rankings.json"
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    embedder = FastEmbedder(cfg.embedder)
    idx_path = S.output_dir() / "index.sqlite"
    if idx_path.exists():
        raise FileExistsError(f"{idx_path} exists without rankings.json; remove it to rebuild")
    idx = Index(idx_path, embedder.dim)
    idx.build([Unit(u["id"], u["text"], tokens=u["tokens"]) for u in S.load()], embedder)
    out = {q["id"]: [u for u, _ in idx.hybrid_search(q["question"], embedder, K)] for q in questions()}
    idx.close()
    path.write_text(json.dumps(out, indent=0), encoding="utf-8", newline="\n")
    return out


def kept_sets(store, cfg) -> list[dict]:
    from hces.arms import judged, relevance, scored
    from hces.units import Unit

    units_raw = S.load()
    units = {u["id"]: Unit(u["id"], "", tokens=u["tokens"]) for u in units_raw}
    ranks, cut = rankings(cfg), frozen()
    rows = []
    for q in key(units_raw):
        j, _ = judged(store, q["id"], VARIANT, ARM)
        rub = rubric(q)
        ranked = ranks[q["id"]]
        everything = sorted(units, key=lambda u: -relevance(j, u))
        for budget in BUDGETS:
            used, rag = 0, []
            for uid in ranked:
                if used + units[uid].tokens <= budget:
                    rag.append(uid)
                    used += units[uid].tokens
            arms = {"rag": rag,
                    "rag+jev": [u.unit_id for u, _ in fill(scored(units, j, rub, ranked), budget, cut)[0]],
                    "jev-all": [u.unit_id for u, _ in fill(scored(units, j, rub, everything), budget, cut)[0]]}
            for arm, kept in arms.items():
                rows.append({"id": q["id"], "arm": arm, "budget": budget, "kept": kept,
                             "tokens": sum(units[u].tokens for u in kept), "answerable": q["answerable"],
                             "gold": q["gold"], "gold_by_quote": q["gold_by_quote"]})
    return rows


def retrieval(store, cfg) -> int:
    rows = kept_sets(store, cfg)
    total = sum(u["tokens"] for u in S.load())
    lines = ["# Instruction Files: Retrieval", "",
             f"{len(S.load())} sections from {len({u['file'] for u in S.load()})} files, {total:,} tokens. Frozen book cutoffs "
             f"({frozen().cutoff:g}, {frozen().unsure_low:g}, {frozen().critical_at:g}), unchanged. Hybrid k {K}. "
             "Gold caught = at least one gold section kept. Every quote = a section kept for each evidence quote. "
             f"Loading every file costs {total:,} tokens and catches all gold by definition.", "",
             "| Arm | Budget | Gold caught | Every quote | Misses | Unanswerable kept nothing | Answerable kept nothing "
             "| Median tokens | Max tokens |",
             "|-----|--------|-------------|-------------|--------|---------------------------|-------------------------"
             "|---------------|------------|"]
    for budget in BUDGETS:
        for arm in ("rag", "rag+jev", "jev-all"):
            rs = [r for r in rows if r["arm"] == arm and r["budget"] == budget]
            ans = [r for r in rs if r["answerable"]]
            un = [r for r in rs if not r["answerable"]]
            hit = [bool(set(r["kept"]) & r["gold"]) for r in ans]
            every = [all(set(r["kept"]) & g for g in r["gold_by_quote"]) for r in ans]
            lines.append(f"| {arm} | {budget} | {sum(hit)} of {len(ans)} | {sum(every)} of {len(ans)} | "
                         f"{', '.join(r['id'].split('/')[1] for r, h in zip(ans, hit) if not h) or 'none'} | "
                         f"{sum(not r['kept'] for r in un)} of {len(un)} | {sum(not r['kept'] for r in ans)} of {len(ans)} | "
                         f"{statistics.median(r['tokens'] for r in rs):.0f} | {max(r['tokens'] for r in rs)} |")
    (S.output_dir() / "retrieval.md").write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    (S.output_dir() / "kept.json").write_text(json.dumps(
        [{k: (sorted(v) if isinstance(v, set) else v) for k, v in r.items() if k != "gold_by_quote"} for r in rows]),
        encoding="utf-8", newline="\n")
    print("\n".join(lines))
    return 0


def corpus_text() -> str:
    base = S.root()
    return "\n\n".join(f"<file path=\"{f.relative_to(base).as_posix()}\">\n{f.read_text(encoding='utf-8')}\n</file>"
                       for f in S.files())


def answer(client, cap: float) -> int:
    kept = {r["id"]: r["kept"] for r in json.loads((S.output_dir() / "kept.json").read_text(encoding="utf-8"))
            if r["arm"] == "rag+jev" and r["budget"] == ANSWER_BUDGET}
    texts = {u["id"]: u["text"] for u in S.load()}
    out = S.output_dir() / "answers.jsonl"
    rows = [json.loads(l) for l in out.read_text(encoding="utf-8").splitlines()] if out.exists() else []
    done, spent = {(r["id"], r["arm"]) for r in rows}, sum(r["cost"] for r in rows)
    corpus = corpus_text()

    def call(q: dict, arm: str) -> dict:
        if arm == "gated":
            if not kept[q["id"]]:
                return {"id": q["id"], "arm": arm, "answer": NOT_IN_DOCS, "cost": 0.0, "ms": 0.0, "usage": None, "kept": 0}
            body = "\n\n".join(f"<section id=\"{u}\">\n{texts[u]}\n</section>" for u in kept[q["id"]])
            system = [{"type": "text", "text": INSTRUCTIONS}]
            content = f"{body}\n\nQuestion: {q['question']}"
        else:
            system = [{"type": "text", "text": INSTRUCTIONS},
                      {"type": "text", "text": corpus, "cache_control": {"type": "ephemeral"}}]
            content = q["question"]
        t0 = time.perf_counter()
        resp = client.beta.messages.create(model=MODEL, max_tokens=4000, output_config={"effort": "low"}, system=system,
                                           messages=[{"role": "user", "content": content}], betas=[FALLBACK_BETA],
                                           fallbacks="default")
        if resp.stop_reason == "refusal":
            raise RuntimeError(f"{q['id']} {arm}: refused even after fallback")
        u = usage(resp)
        return {"id": q["id"], "arm": arm, "answer": "".join(b.text for b in resp.content if b.type == "text").strip(),
                "cost": cost(MODEL, u), "ms": (time.perf_counter() - t0) * 1000, "usage": u,
                "kept": len(kept[q["id"]]) if arm == "gated" else None}

    for arm in ("gated", "all-files"):  # all-files runs in order, so the first call writes the cache
        for q in questions():
            if (q["id"], arm) in done:
                continue
            row = call(q, arm)
            spent += row["cost"]
            with open(out, "a", encoding="utf-8", newline="\n") as f:
                f.write(json.dumps(row) + "\n")
            print(q["id"], arm, f"{row['ms']:.0f} ms total ${spent:.2f} |", row["answer"][:80], flush=True)
            if spent > cap:
                raise SystemExit(f"Spend ${spent:.2f} passed the cap ${cap:.2f}; stopped")
    return 0


def grade(client) -> int:
    answers = [json.loads(l) for l in (S.output_dir() / "answers.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
    out = S.output_dir() / "grades.jsonl"
    done = {r["uid"] for r in map(json.loads, out.read_text(encoding="utf-8").splitlines())} if out.exists() else set()
    qs = {q["id"]: q for q in key()}
    texts = {u["id"]: u["text"] for u in S.load()}
    random.Random(7).shuffle(answers)
    for a in answers:
        uid = f"{a['id']}#{a['arm']}"
        if uid in done:
            continue
        q = qs[a["id"]]
        ref = q["answer"] if q["answerable"] else "The files do not contain this. The right answer says it is not in the documents."
        ev = "\n\n".join(texts[g] for g in sorted(q["gold"])) if q["answerable"] else "(none)"
        prompt = f"Question: {q['question']}\n\nReference answer: {ref}\n\nSections holding the answer:\n{ev}\n\nAnswer to grade:\n{a['answer']}"
        if uid in prompt:
            raise RuntimeError(f"{uid}: grader prompt carries the arm label")
        resp = client.messages.create(model=MODEL, max_tokens=2000, system=GRADER,
                                      output_config={"effort": "low", "format": {"type": "json_schema", "schema": VERDICT_SCHEMA}},
                                      messages=[{"role": "user", "content": prompt}])
        if resp.stop_reason == "refusal":
            raise RuntimeError(f"{uid}: grader refused")
        v = json.loads(next(b.text for b in resp.content if b.type == "text"))
        with open(out, "a", encoding="utf-8", newline="\n") as f:
            f.write(json.dumps({"uid": uid, "verdict": v["verdict"], "reason": v["reason"], "cost": cost(MODEL, usage(resp))}) + "\n")
        print(uid, v["verdict"], flush=True)
    return 0


def report() -> int:
    answers = {f"{r['id']}#{r['arm']}": r for r in map(json.loads, (S.output_dir() / "answers.jsonl").read_text(encoding="utf-8").splitlines())}
    grades = {r["uid"]: r for r in map(json.loads, (S.output_dir() / "grades.jsonl").read_text(encoding="utf-8").splitlines())}
    if set(answers) - set(grades):
        raise SystemExit(f"{len(set(answers) - set(grades))} answers have no grade")
    qs = {q["id"]: q for q in questions()}
    lines = ["# Instruction Files: End to End", "",
             f"Opus 5.5 answers from the gated sections (RAG + JEV, frozen cutoffs, {ANSWER_BUDGET} tokens) and from all files. "
             "Blind grading as in end-to-end.md.", "",
             "| Arm | Answerable score | Correct | Partial | Wrong | Abstained on answerable | Unanswerable abstained "
             "| Median ms | Slowest 10% ms | Median input tokens | Cost |",
             "|-----|------------------|---------|---------|-------|-------------------------|------------------------"
             "|-----------|----------------|---------------------|------|"]
    for arm in ("gated", "all-files"):
        rs = [(answers[u], grades[u], qs[answers[u]["id"]]) for u in answers if answers[u]["arm"] == arm]
        ans = [g for _, g, q in rs if q["answerable"]]
        un = [g for _, g, q in rs if not q["answerable"]]
        ms = sorted(a["ms"] for a, _, _ in rs)
        toks = [sum(a["usage"][k] for k in ("input", "cache_write", "cache_read")) if a["usage"] else 0 for a, _, _ in rs]
        c = lambda v, xs: sum(g["verdict"] == v for g in xs)  # noqa: E731
        score = sum(points(g["verdict"], True) for g in ans)
        lines.append(f"| {arm} | {score:g} of {len(ans)} ({100 * score / len(ans):.0f}%) | {c('correct', ans)} | {c('partial', ans)} "
                     f"| {c('wrong', ans)} | {c('abstained', ans)} | {c('abstained', un)} of {len(un)} | {statistics.median(ms):.0f} "
                     f"| {ms[min(len(ms) - 1, int(round(0.9 * (len(ms) - 1))))]:.0f} | {statistics.median(toks):.0f} "
                     f"| ${sum(a['cost'] for a, _, _ in rs):.2f} |")
    lines += ["", "## Where the arms disagree", "", "| Question | Gated | All files | Gated answer | All-files answer |",
              "|----------|-------|-----------|--------------|------------------|"]
    clean = lambda s: " ".join(s.split()).replace("|", "/")[:150]  # noqa: E731
    for qid, q in qs.items():
        g, f = grades[f"{qid}#gated"], grades[f"{qid}#all-files"]
        if points(g["verdict"], q["answerable"]) != points(f["verdict"], q["answerable"]):
            lines.append(f"| {qid} | {g['verdict']} | {f['verdict']} | {clean(answers[qid + '#gated']['answer'])} "
                         f"| {clean(answers[qid + '#all-files']['answer'])} |")
    lines += ["", f"Answering ${sum(a['cost'] for a in answers.values()):.2f}, grading ${sum(g['cost'] for g in grades.values()):.2f}."]
    (S.output_dir() / "end-to-end.md").write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print("\n".join(lines))
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="python -m hces.instr")
    mode = ap.add_mutually_exclusive_group(required=True)
    for m in ("key", "judge", "retrieval", "answer", "grade", "report"):
        mode.add_argument(f"--{m}", action="store_true")
    ap.add_argument("--yes", action="store_true")
    ap.add_argument("--cap", type=float, default=4.0)
    a = ap.parse_args(argv)
    if a.key:
        for q in key():
            print(q["id"], "answerable" if q["answerable"] else "unanswerable", len(q["gold"]), "gold", sorted(q["gold"])[:4])
        return 0
    if a.report:
        return report()
    if (a.judge or a.answer or a.grade) and not a.yes:
        raise SystemExit("This spends credit; pass --yes")
    from hces.config import load
    from hces.store import Store

    cfg = load()
    if a.judge:
        return judge(Store(cfg.results_store), cfg, a.cap)
    if a.retrieval:
        return retrieval(Store(cfg.results_store), cfg)
    import anthropic

    client = anthropic.Anthropic()
    return answer(client, a.cap) if a.answer else grade(client)


if __name__ == "__main__":
    raise SystemExit(main())
