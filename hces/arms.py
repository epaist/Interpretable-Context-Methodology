"""Build the RAG + JEV and JEV-on-everything arms from stored judgments, ask answerability,
write run rows, decisions and per-question manifests.

  python -m hces.arms <slug> --yes

Candidates for RAG + JEV come from the RAG-only runs (same retrieval, same k). Judgments come
from the judge pass (one per passage per question). Analysis time for an arm is the measured
fill and answerability time plus the judge pass time scaled to the arm's candidate count,
since the judge pass ran all passages through the same worker pool.
"""

from __future__ import annotations

import argparse
import json
import statistics
import time
from collections import defaultdict
from pathlib import Path

from hces import passages as P
from hces.judge_all import rubrics_for
from hces.rag import key_rows, output_dir
from hces.rollup import Scored, fill
from hces.store import Store, new_run_id
from hces.timing import RunClock
from hces.units import Unit

NOT_IN_DOCS_BELOW = 0.50


def judged(store: Store, qid: str, shape: str, arm: str = "judge") -> tuple[dict, dict]:
    run = store.db.execute("SELECT * FROM runs WHERE arm=? AND question_id=? AND variant=? "
                           "ORDER BY started_at DESC LIMIT 1", (arm, qid, shape)).fetchone()
    if run is None:
        raise SystemExit(f"No judge run for {qid} {shape}; run hces.judge_all first")
    out: dict[str, dict] = defaultdict(dict)
    for j in store.judgments(run["run_id"]):
        out[j["unit_id"]][j["question_key"]] = j
    return out, dict(run)


def rag_candidates(store: Store, qid: str, shape: str) -> dict[tuple[str, int], tuple[list[str], float]]:
    rows = store.db.execute("SELECT run_id, variant, k, access_ms FROM runs WHERE arm='rag' AND question_id=? "
                            "AND variant LIKE ? ORDER BY started_at", (qid, f"%/{shape}")).fetchall()
    out = {}
    for r in rows:
        ids = [d["unit_id"] for d in store.db.execute(
            "SELECT unit_id FROM decisions WHERE run_id=? ORDER BY rank", (r["run_id"],))]
        out[(r["variant"].split("/")[0], r["k"])] = (ids, r["access_ms"])
    return out


def relevance(j: dict, uid: str) -> float:
    rel = j.get(uid, {}).get("relevance")
    return 0.0 if rel is None or rel["value"] is None else float(rel["value"])


def ask_answerable(judge, question: str, rubric, kept: list[Unit], tries: int = 3) -> float:
    for attempt in range(tries):
        try:
            return judge.answerable(question, rubric, kept)
        except Exception:
            if attempt == tries - 1:
                raise
            time.sleep(2 ** attempt)
    raise AssertionError("unreachable")


def scored(units: dict[str, Unit], j: dict, rubric, ranked: list[str]) -> list[Scored]:
    out = []
    for rank, uid in enumerate(ranked, start=1):
        a = j.get(uid, {})
        rel, crit = a.get("relevance"), a.get("contains_fact")
        failed = rel is None or rel["value"] is None
        score = 0.0 if failed else rubric.unit_score({"relevance": rel["value"]})
        cp = 0.0 if crit is None or crit["value"] is None else crit["value"]
        out.append(Scored(uid, units[uid].tokens, score, cp, rank, failed))
    return out


def manifest_block(title: str, kept, cut, p: float | None, gold: set, decoys: set, show_cut: int | None) -> list[str]:
    mark = lambda uid: (" **gold**" if uid in gold else "") + (" *decoy*" if uid in decoys else "")  # noqa: E731
    lines = [f"### {title}", "", f"Answerability: {'not asked' if p is None else f'{p:.2f}'}"
             + ("" if p is None else (" (answers)" if p >= NOT_IN_DOCS_BELOW else " (says not in the documents)")),
             "", "| Kept | Unit | Score | Fact p | Rank | Why |", "|------|------|-------|--------|------|-----|"]
    for u, why in kept:
        lines.append(f"| yes | {u.unit_id}{mark(u.unit_id)} | {u.score:.2f} | {u.critical_p:.2f} | {u.rank} | {why} |")
    shown = cut if show_cut is None else [c for c in cut if c[0].score >= 0.25 or c[0].unit_id in gold | decoys][:show_cut]
    for u, why in shown:
        lines.append(f"| no | {u.unit_id}{mark(u.unit_id)} | {u.score:.2f} | {u.critical_p:.2f} | {u.rank} | {why} |")
    if len(shown) < len(cut):
        lines.append(f"| no | {len(cut) - len(shown)} more | below 0.25 | | | listed in results.db decisions |")
    return lines + [""]


def main(argv=None) -> int:
    from hces.config import load
    from hces.judge import JevJudge

    ap = argparse.ArgumentParser(prog="python -m hces.arms")
    ap.add_argument("slug")
    ap.add_argument("--yes", action="store_true", help="required: answerability calls spend JEV credit")
    a = ap.parse_args(argv)
    if not a.yes:
        raise SystemExit("Answerability calls spend JEV credit; pass --yes")
    cfg = load()
    rubrics = rubrics_for(a.slug)
    store = Store(cfg.results_store)
    judge = JevJudge(cfg.jev_model, cfg.judge_workers, cfg.price_per_million, cfg.state_cap_question)
    mdir = output_dir() / "manifests" / a.slug
    mdir.mkdir(parents=True, exist_ok=True)
    cache: dict[frozenset, tuple[float, int, float]] = {}
    rows = []
    for q in key_rows(a.slug):
        rub = rubrics[q["id"]]
        md = [f"# {q['id']}", "", f"**Question:** {q['question']}", "",
              f"**Answer key:** {q['answer']} ({'answerable' if q['answerable'] else 'unanswerable'})", ""]
        for shape in ("chaptered", "plain"):
            units = {r["id"]: Unit(r["id"], r["text"], tokens=r["tokens"]) for r in P.load_passages(a.slug, shape)}
            j, jrun = judged(store, q["id"], shape)
            per_unit_ms = jrun["analysis_ms"] / max(1, jrun["k"])
            per_unit_tokens = jrun["tokens_in"] / max(1, jrun["k"])
            gold, decoys = set(q["gold"][shape]), set(q["decoy_gold"][shape])
            arms = [("rag+jev", v, k, ids, acc) for (v, k), (ids, acc) in sorted(rag_candidates(store, q["id"], shape).items())]
            everything = sorted(units, key=lambda u: -relevance(j, u))
            arms.append(("jev-all", "all", len(units), everything, 0.0))
            md += [f"## Shape: {shape}", ""]
            for arm, variant, k, ranked, access_ms in arms:
                run_id = new_run_id()
                with RunClock() as clock:
                    with clock.span("access"):
                        cands = scored(units, j, rub, ranked)
                    with clock.span("analysis"):
                        kept, cut = fill(cands, cfg.token_budget)
                        key = frozenset(u.unit_id for u, _ in kept)
                        if key not in cache:
                            t0 = time.perf_counter()
                            p = ask_answerable(judge, q["question"], rub, [units[u.unit_id] for u, _ in kept])
                            cache[key] = (p, judge.last_tokens,
                                          (time.perf_counter() - t0) * 1000)
                        p, ans_tokens, ans_ms = cache[key]
                    with clock.span("response"):
                        decisions = [{"unit_id": u.unit_id, "kept": True, "final_score": u.score, "rank": u.rank, "reason": why}
                                     for u, why in kept] + [{"unit_id": u.unit_id, "kept": False, "final_score": u.score,
                                                             "rank": u.rank, "reason": why} for u, why in cut]
                        store.add_decisions(run_id, decisions)
                kept_ids = {u.unit_id for u, _ in kept}
                tokens_in = round(per_unit_tokens * len(ranked)) + ans_tokens
                analysis = clock.ms["analysis"] + per_unit_ms * len(ranked)
                notes = {"answerable": q["answerable"], "answer_p": round(p, 4), "says_not_in_docs": p < NOT_IN_DOCS_BELOW,
                         "gold": len(gold), "gold_retrieved": len(gold & set(ranked)), "gold_kept": len(gold & kept_ids),
                         "decoys_kept": len(decoys & kept_ids), "kept": len(kept), "candidates": len(ranked),
                         "tokens_used": sum(u.tokens for u, _ in kept), "hard_case": q["hard_case"],
                         "judge_ms_scaled": round(per_unit_ms * len(ranked), 1), "answerability_ms": round(ans_ms, 1)}
                if notes["tokens_used"] > cfg.token_budget:
                    raise RuntimeError(f"{run_id} over budget")
                row = {"run_id": run_id, "arm": arm, "variant": f"{variant}/{shape}", "k": k, "question_id": q["id"],
                       "budget": cfg.token_budget, "judge_model": cfg.jev_model, "rubric_id": rub.rubric_id,
                       "rubric_version": rub.version, "access_ms": access_ms + clock.ms["access"],
                       "analysis_ms": analysis, "response_ms": clock.ms["response"], "peak_rss_mb": clock.peak_rss_mb,
                       "tokens_in": tokens_in, "cost_usd": tokens_in * cfg.price_per_million / 1e6, "notes": notes}
                store.add_run(row)
                rows.append(row)
                if (variant, k) in (("hybrid", 50), ("vector", 50), ("all", len(units))):
                    md += manifest_block(f"{arm}, {variant}, k {k}", kept, cut, p, gold, decoys,
                                         None if arm == "rag+jev" else 15)
        (mdir / f"{q['id'].split('/')[1]}.md").write_text("\n".join(md) + "\n", encoding="utf-8", newline="\n")
        print(json.dumps({"question": q["id"], "runs": len(rows), "answerability_calls": len(cache)}), flush=True)
    store.close()
    (output_dir() / f"jev-arms-{a.slug}.json").write_text(json.dumps({"runs": len(rows), "answerability_calls": len(cache)}),
                                                 encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
