"""Stage 01 smoke test on a 3-passage toy volume.

  python -m hces.smoke index      build the toy index with the real embedder (no JEV)
  python -m hces.smoke estimate   print the cost of the one JEV call (no JEV)
  python -m hces.smoke jev --yes  make the one JEV call and store it with timings
"""

from __future__ import annotations

import argparse
import json
import sys
import time

from hces import config
from hces.rubric import Question, Rubric
from hces.units import Unit

TOY = [
    Unit("toy/p1", "The keeper climbed the lighthouse stairs at dusk and trimmed the wick, as he had every night for eleven years.", source="toy"),
    Unit("toy/p2", "Fishing boats came back to the harbor heavy with herring, and the prices at the quay fell by evening.", source="toy"),
    Unit("toy/p3", "A letter from the mainland said his mother was gravely ill, so the keeper handed the light to his assistant and left the island on the morning boat.", source="toy"),
]
TASK = "Why does the lighthouse keeper leave the island?"
RUBRIC = Rubric(
    rubric_id="smoke-relevance",
    version=1,
    task=TASK,
    questions=(
        Question("relevance", "score", "How directly does this passage help answer the task?",
                 ["Unrelated to the task", "Mentions the topic only", "Partly answers the task", "Directly answers the task"]),
    ),
    answerability=Question("enough", "noul", "Is the evidence enough to answer the task?"),
)


def toy_index_path(cfg: config.Config):
    return config.ROOT / "workspaces" / "hces-lab" / "kb" / "index" / "toy.db"


def cmd_index(cfg: config.Config) -> dict:
    from hces.embed import FastEmbedder
    from hces.retrieve import Index
    from hces.timing import RunClock

    path = toy_index_path(cfg)
    if path.exists():
        path.unlink()  # index files are rebuildable; results never live here
    with RunClock() as clock:
        with clock.span("index_build"):
            emb = FastEmbedder(cfg.embedder)
            idx = Index(path, emb.dim)
            idx.build(TOY, emb)
    hits = idx.hybrid_search(TASK, emb, 3)
    idx.close()
    return {"index": str(path), "embedder": cfg.embedder, "passages": len(TOY),
            "index_build_ms": round(clock.ms["index_build"], 1), "peak_rss_mb": clock.peak_rss_mb,
            "hybrid_top3": hits}


def judge_for(cfg: config.Config):
    from hces.judge import JevJudge

    return JevJudge(cfg.jev_model, cfg.judge_workers, cfg.price_per_million, cfg.state_cap_question)


def cmd_estimate(cfg: config.Config) -> dict:
    from hces.judge import JevJudge

    est = JevJudge(cfg.jev_model, 1, cfg.price_per_million, cfg.state_cap_question, client_factory=lambda: None)
    tokens = est.request_tokens(TASK, RUBRIC, TOY[2:3])
    return {"calls": 1, "approx_input_tokens": tokens, "price_per_million": cfg.price_per_million,
            "approx_cost_usd": tokens * cfg.price_per_million / 1e6}


def cmd_jev(cfg: config.Config) -> dict:
    from hces.embed import FastEmbedder
    from hces.retrieve import Index
    from hces.store import Store, new_run_id
    from hces.timing import RunClock

    run_id = new_run_id()
    started = time.time()
    store = Store(cfg.results_store)
    store.add_rubric(RUBRIC)
    with RunClock() as clock:
        with clock.span("access"):
            emb = FastEmbedder(cfg.embedder)
            idx = Index(toy_index_path(cfg), emb.dim)
            top_id = idx.hybrid_search(TASK, emb, 1)[0][0]
            idx.close()
            unit = next(u for u in TOY if u.id == top_id)
        with clock.span("analysis"):
            judge = judge_for(cfg)
            judgments = judge.judge(TASK, RUBRIC, [unit])
        with clock.span("response"):
            j = judgments[0]
            if j.failed:
                raise SystemExit(f"JEV call failed: {j.error}")
            score = RUBRIC.unit_score({"relevance": j.value})
            store.add_judgments(run_id, RUBRIC, judgments)
            store.add_decisions(run_id, [{"unit_id": unit.id, "kept": True, "final_score": score, "rank": 1,
                                          "reason": "smoke test: single candidate"}])
    clock.require("access", "analysis", "response")
    cost = (j.tokens_in or 0) * cfg.price_per_million / 1e6
    store.add_run({"run_id": run_id, "arm": "smoke", "variant": "hybrid", "k": 1, "question_id": "smoke-q1",
                   "budget": cfg.token_budget, "judge_model": j.model, "rubric_id": RUBRIC.rubric_id,
                   "rubric_version": RUBRIC.version, "access_ms": clock.ms["access"],
                   "analysis_ms": clock.ms["analysis"], "response_ms": clock.ms["response"],
                   "peak_rss_mb": clock.peak_rss_mb, "tokens_in": j.tokens_in or 0, "cost_usd": cost,
                   "started_at": started})
    store.close()
    return {"run_id": run_id, "unit": unit.id, "model_requested": cfg.jev_model, "model_answered": j.model,
            "relevance_expected_level": j.value, "relevance_confidence": j.confidence, "unit_score": score,
            "tokens_in": j.tokens_in, "cost_usd": cost,
            "timings_ms": {k: round(v, 1) for k, v in clock.ms.items()}, "peak_rss_mb": clock.peak_rss_mb,
            "results_store": str(cfg.results_store)}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="python -m hces.smoke")
    ap.add_argument("command", choices=["index", "estimate", "jev"])
    ap.add_argument("--yes", action="store_true", help="confirm the paid JEV call")
    args = ap.parse_args(argv)
    cfg = config.load()
    if args.command == "jev" and not args.yes:
        print("Refusing to call JEV without --yes. Run 'estimate' first.", file=sys.stderr)
        return 2
    out = {"index": cmd_index, "estimate": cmd_estimate, "jev": cmd_jev}[args.command](cfg)
    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
