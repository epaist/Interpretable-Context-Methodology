"""RAG-only arm: retrieve, keep top matches in rank order until the token budget is full.

  python -m hces.rag <slug>

Runs every answer-key question of the volume over both shapes, both retrieval variants (vector,
hybrid) and every candidate count in the sweep. Each run is one row in results.db (arm "rag")
with its decisions; a summary goes to stages/03-pipeline-v0/output/rag-only.json.
"""

from __future__ import annotations

import json
import statistics
import time
from pathlib import Path

from hces import build_index as B
from hces import passages as P
from hces.retrieve import Index
from hces.store import Store, new_run_id
from hces.timing import RunClock

SHAPES = ("chaptered", "plain")
VARIANTS = ("vector", "hybrid")


def output_dir() -> Path:
    from hces.config import ROOT

    return ROOT / "workspaces" / "hces-lab" / "stages" / "03-pipeline-v0" / "output"


def key_rows(slug: str) -> list[dict]:
    from hces.answer_key import stage_dir

    rows = [json.loads(l) for l in (stage_dir() / "answer-key.jsonl").read_text(encoding="utf-8").splitlines()]
    return [r for r in rows if r["volume"] == slug]


def fill_budget(ranked: list[str], tokens: dict[str, int], budget: int) -> list[str]:
    """Whole units in rank order; a unit that does not fit is skipped and later smaller ones may still fit."""
    kept, used = [], 0
    for uid in ranked:
        if used + tokens[uid] <= budget:
            kept.append(uid)
            used += tokens[uid]
    return kept


def run_one(idx: Index, embedder, question: dict, shape: str, variant: str, k: int, budget: int,
            tokens: dict[str, int]) -> tuple[dict, list[dict]]:
    with RunClock() as clock:
        with clock.span("access"):
            if variant == "vector":
                ranked = [u for u, _ in idx.vector_search(embedder.embed([question["question"]])[0], k)]
            else:
                ranked = [u for u, _ in idx.hybrid_search(question["question"], embedder, k)]
        with clock.span("analysis"):
            kept = fill_budget(ranked, tokens, budget)
        with clock.span("response"):
            kept_set = set(kept)
            decisions = [{"unit_id": u, "kept": u in kept_set, "rank": i, "final_score": None,
                          "reason": "within budget" if u in kept_set else "over budget"}
                         for i, u in enumerate(ranked, start=1)]
    gold = set(question["gold"][shape])
    decoys = set(question["decoy_gold"][shape])
    first_gold = next((i for i, u in enumerate(ranked, start=1) if u in gold), None)
    run = {"run_id": new_run_id(), "arm": "rag", "variant": f"{variant}/{shape}", "k": k,
           "question_id": question["id"], "budget": budget, "judge_model": None,
           "access_ms": round(clock.ms["access"], 2), "analysis_ms": round(clock.ms["analysis"], 3),
           "response_ms": round(clock.ms["response"], 3), "peak_rss_mb": clock.peak_rss_mb,
           "tokens_in": 0, "cost_usd": 0.0,
           "notes": {"answerable": question["answerable"], "gold": len(gold),
                     "gold_retrieved": len(gold & set(ranked)), "gold_kept": len(gold & kept_set),
                     "first_gold_rank": first_gold, "decoys_kept": len(decoys & kept_set),
                     "kept": len(kept), "tokens_used": sum(tokens[u] for u in kept),
                     "hard_case": question["hard_case"]}}
    return run, decisions


def summarize(runs: list[dict]) -> list[dict]:
    out = []
    groups: dict[tuple, list[dict]] = {}
    for r in runs:
        groups.setdefault((r["variant"], r["k"]), []).append(r)
    for (variant, k), rs in sorted(groups.items()):
        ans = [r for r in rs if r["notes"]["answerable"]]
        needles = [r for r in ans if "needle" in r["notes"]["hard_case"]]
        real = [r for r in ans if "needle" not in r["notes"]["hard_case"]]
        caught = lambda xs, f: round(sum(1 for r in xs if r["notes"][f] > 0) / len(xs), 3) if xs else None  # noqa: E731
        out.append({
            "variant": variant, "k": k, "questions": len(rs),
            "retrieved_any_gold": caught(ans, "gold_retrieved"), "kept_any_gold": caught(ans, "gold_kept"),
            "needles_retrieved": caught(needles, "gold_retrieved"), "needles_kept": caught(needles, "gold_kept"),
            "real_retrieved": caught(real, "gold_retrieved"), "real_kept": caught(real, "gold_kept"),
            "misses": [r["question_id"] for r in ans if r["notes"]["gold_retrieved"] == 0],
            "decoys_kept": sum(r["notes"]["decoys_kept"] for r in rs),
            "max_tokens_used": max(r["notes"]["tokens_used"] for r in rs),
            "median_access_ms": round(statistics.median(r["access_ms"] for r in rs), 1),
            "peak_rss_mb": max(r["peak_rss_mb"] for r in rs),
        })
    return out


def main(argv=None) -> int:
    import argparse

    from hces.config import load
    from hces.embed import FastEmbedder

    ap = argparse.ArgumentParser(prog="python -m hces.rag")
    ap.add_argument("slug")
    a = ap.parse_args(argv)
    cfg = load()
    embedder = FastEmbedder(cfg.embedder)
    store = Store(cfg.results_store)
    questions = key_rows(a.slug)
    runs = []
    t0 = time.perf_counter()
    for shape in SHAPES:
        tokens = {r["id"]: r["tokens"] for r in P.load_passages(a.slug, shape)}
        idx = Index(B.index_path(a.slug, shape), embedder.dim)
        for q in questions:
            for variant in VARIANTS:
                for k in cfg.top_k_sweep:
                    run, decisions = run_one(idx, embedder, q, shape, variant, k, cfg.token_budget, tokens)
                    if run["notes"]["tokens_used"] > cfg.token_budget:
                        raise RuntimeError(f"{run['run_id']} is over budget")
                    store.add_decisions(run["run_id"], decisions)
                    store.add_run(run)
                    runs.append(run)
        idx.close()
    summary = {"volume": a.slug, "runs": len(runs), "wall_s": round(time.perf_counter() - t0, 1),
               "budget": cfg.token_budget, "by_variant": summarize(runs)}
    out = output_dir() / f"rag-only-{a.slug}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(summary, indent=1), encoding="utf-8", newline="\n")
    print(json.dumps({k: v for k, v in summary.items() if k != "by_variant"}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
