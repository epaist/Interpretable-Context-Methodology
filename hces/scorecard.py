"""Stage 04 scorecard: every arm on the exam questions of all three volumes, with the frozen cutoffs.

  python -m hces.scorecard --yes

RAG only uses its stored kept sets. RAG + JEV and JEV on everything are refilled from stored
judgments with the frozen cutoffs; answerability is asked once per distinct kept set (JEV calls,
a few cents). Timings and per-question cost come from the stored run rows. Writes
stages/04-exam/output/scorecard.md and scorecard.json.
"""

from __future__ import annotations

import argparse
import json
import statistics

from hces import passages as P
from hces.arms import NOT_IN_DOCS_BELOW, ask_answerable, judged, rag_candidates, relevance, scored
from hces.exam import K, VARIANT, VOLUMES, output_dir
from hces.judge_all import rubrics_for
from hces.rag import key_rows
from hces.report import latest_runs
from hces.rollup import Cutoffs, fill
from hces.store import Store
from hces.units import Unit

ARMS = ("rag", "rag+jev", "jev-all")
SHAPES = ("chaptered", "plain")


def p90(xs: list[float]) -> float:
    xs = sorted(xs)
    return xs[min(len(xs) - 1, int(round(0.9 * (len(xs) - 1))))] if xs else 0.0


def pct(a: int, b: int) -> str:
    return f"{100 * a / b:.0f}%" if b else "n/a"


def kept_sets(store: Store, slug: str, frozen: Cutoffs, budget: int) -> list[dict]:
    """One row per (question, shape, arm) with the kept unit ids."""
    rubrics = rubrics_for(slug)
    out = []
    for shape in SHAPES:
        units = {r["id"]: Unit(r["id"], "", tokens=r["tokens"]) for r in P.load_passages(slug, shape)}
        for q in key_rows(slug):
            if "fresh" in q["hard_case"]:
                continue
            j, _ = judged(store, q["id"], shape)
            ranked = rag_candidates(store, q["id"], shape)[(VARIANT, K)][0]
            rag_kept = [d["unit_id"] for d in store.db.execute(
                "SELECT d.unit_id FROM decisions d JOIN runs r ON r.run_id = d.run_id WHERE r.arm='rag' AND r.question_id=? "
                "AND r.variant=? AND r.k=? AND d.kept=1 AND r.started_at=(SELECT max(started_at) FROM runs WHERE arm='rag' "
                "AND question_id=? AND variant=? AND k=?)", (q["id"], f"{VARIANT}/{shape}", K, q["id"], f"{VARIANT}/{shape}", K))]
            everything = sorted(units, key=lambda u: -relevance(j, u))
            arms = {"rag": rag_kept,
                    "rag+jev": [u.unit_id for u, _ in fill(scored(units, j, rubrics[q["id"]], ranked), budget, frozen)[0]],
                    "jev-all": [u.unit_id for u, _ in fill(scored(units, j, rubrics[q["id"]], everything), budget, frozen)[0]]}
            for arm, kept in arms.items():
                out.append({"id": q["id"], "volume": slug, "shape": shape, "arm": arm, "kept": kept,
                            "tokens": sum(units[u].tokens for u in kept), "answerable": q["answerable"],
                            "needle": "needle" in q["hard_case"], "gold": set(q["gold"][shape]),
                            "decoys": set(q["decoy_gold"][shape])})
    return out


def main(argv=None) -> int:
    from hces.config import load
    from hces.judge import JevJudge

    ap = argparse.ArgumentParser(prog="python -m hces.scorecard")
    ap.add_argument("--yes", action="store_true", help="required: answerability calls spend JEV credit")
    a = ap.parse_args(argv)
    if not a.yes:
        raise SystemExit("Answerability calls spend JEV credit; pass --yes")
    cfg = load()
    frozen = Cutoffs(**json.loads((output_dir() / "cutoffs.json").read_text(encoding="utf-8"))["cutoffs"])
    store = Store(cfg.results_store)
    judge = JevJudge(cfg.jev_model, cfg.judge_workers, cfg.price_per_million, cfg.state_cap_question)
    rows, billed = [], 0
    for slug in VOLUMES:
        rubrics = rubrics_for(slug)
        qtext = {q["id"]: q["question"] for q in key_rows(slug)}
        texts = {s: {r["id"]: r["text"] for r in P.load_passages(slug, s)} for s in SHAPES}
        cache: dict[tuple, float] = {}
        for r in kept_sets(store, slug, frozen, cfg.token_budget):
            if r["arm"] != "rag":
                key = (r["id"], frozenset(r["kept"]))
                if key not in cache:
                    cache[key] = ask_answerable(judge, qtext[r["id"]], rubrics[r["id"]],
                                                [Unit(u, texts[r["shape"]][u]) for u in r["kept"]])
                    billed += judge.last_tokens
                r["answer_p"] = cache[key]
            rows.append(r)
    runs = latest_runs(store, {r["id"] for r in rows})
    timing = {}
    for run in runs:
        if (run["arm"] == "jev-all") or (run["variant"].startswith(VARIANT + "/") and run["k"] == K):
            timing.setdefault((run["arm"], run["question_id"].split("/")[0]), []).append(run)
    lines = ["# Stage 04 Scorecard", "",
             f"Exam questions only (fresh set is in confirm.md). Both shapes, budget {cfg.token_budget}, frozen cutoffs "
             f"({frozen.cutoff:g}, {frozen.unsure_low:g}, {frozen.critical_at:g}), retrieval {VARIANT} k {K}, judge {cfg.jev_model}. "
             "Gold caught = at least one gold passage kept. Lookalikes kept counts real lookalikes and needle decoys. "
             "Timings are per question per shape: access + analysis + response, analysis including the judge time "
             "scaled to the arm's candidates.", "",
             "| Volume | Arm | Gold caught | Needles | Misses | Lookalikes kept | Gold share | Unanswerable flagged "
             "| Wrongly flagged | Median tokens | Max tokens | Median ms | Slowest 10% ms | Cost per question |",
             "|--------|-----|-------------|---------|--------|-----------------|------------|----------------------"
             "|-----------------|---------------|------------|-----------|----------------|-------------------|"]
    summary = {}
    for slug in VOLUMES + ("all",):
        for arm in ARMS:
            rs = [r for r in rows if r["arm"] == arm and (slug == "all" or r["volume"] == slug)]
            ans = [r for r in rs if r["answerable"]]
            un = [r for r in rs if not r["answerable"]]
            hit = [bool(set(r["kept"]) & r["gold"]) for r in ans]
            needles = [h for h, r in zip(hit, ans) if r["needle"]]
            share = [sum(1 for u in r["kept"] if u in r["gold"]) / len(r["kept"]) if r["kept"] else 0.0 for r in ans]
            flag = arm != "rag"
            nid_un = sum(r["answer_p"] < NOT_IN_DOCS_BELOW for r in un) if flag else None
            nid_ans = sum(r["answer_p"] < NOT_IN_DOCS_BELOW for r in ans) if flag else None
            tr = [t for v in (VOLUMES if slug == "all" else (slug,)) for t in timing.get((arm, v), [])]
            ms = [t["access_ms"] + t["analysis_ms"] + t["response_ms"] for t in tr]
            cost = statistics.mean(t["cost_usd"] for t in tr) if tr else 0.0
            m = {"gold": sum(hit), "answerable": len(ans), "needles": sum(needles), "needle_n": len(needles),
                 "misses": len(ans) - sum(hit), "lookalikes": sum(len(set(r["kept"]) & r["decoys"]) for r in rs),
                 "gold_share": statistics.mean(share) if share else 0.0, "flagged": nid_un, "unanswerable": len(un),
                 "wrongly": nid_ans, "median_tokens": statistics.median(r["tokens"] for r in rs),
                 "max_tokens": max(r["tokens"] for r in rs), "median_ms": statistics.median(ms) if ms else 0.0,
                 "p90_ms": p90(ms), "cost": cost}
            summary[f"{slug}/{arm}"] = m
            lines.append(f"| {slug} | {arm} | {pct(m['gold'], m['answerable'])} | {pct(m['needles'], m['needle_n'])} | {m['misses']} "
                         f"| {m['lookalikes']} | {m['gold_share']:.2f} "
                         f"| {pct(nid_un, len(un)) if flag else 'n/a'} | {pct(nid_ans, len(ans)) if flag else 'n/a'} "
                         f"| {m['median_tokens']:.0f} | {m['max_tokens']} | {m['median_ms']:.0f} | {m['p90_ms']:.0f} | ${cost:.4f} |")
    lines += ["", f"Answerability calls for this scorecard: {billed:,} tokens billed (${billed * cfg.price_per_million / 1e6:.4f})."]
    out = output_dir()
    (out / "scorecard.md").write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    (out / "scorecard.json").write_text(json.dumps(summary, indent=1), encoding="utf-8", newline="\n")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
