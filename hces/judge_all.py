"""Judge every passage of a volume once per question, in both shapes (the JEV-on-everything pass).

  python -m hces.judge_all <slug> --yes [--cap 1.80] [--only q01] [--shape plain]

Every arm reuses these judgments: a passage's answers do not depend on k or on how it was
retrieved. One run row per (question, shape), arm "judge". Resumable: a (question, shape) that
already has a judge run is skipped. After each question the spend so far is projected over the
whole job; the run stops before the projection passes --cap.
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from hces import passages as P
from hces.rag import key_rows, output_dir
from hces.rubric import Rubric
from hces.store import Store, new_run_id
from hces.timing import RunClock
from hces.units import Unit

SHAPES = ("chaptered", "plain")
ANSWERABILITY_RESERVE = 0.30  # USD set aside for the answerability calls of the arms (stage 03 estimate)


def rubrics_for(slug: str, suffix: str = "") -> dict[str, Rubric]:
    path = output_dir() / "rubrics" / f"{slug}{suffix}.jsonl"
    rows = [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]
    out = {}
    for r in rows:
        rub = Rubric.from_dict(r)
        if r.get("hash") and r["hash"] != rub.hash:
            raise ValueError(f"{rub.rubric_id}: stored hash does not match its questions")
        out[rub.rubric_id] = rub
    return out


def done_pairs(store: Store, arm: str = "judge") -> set[tuple[str, str]]:
    rows = store.db.execute("SELECT question_id, variant FROM runs WHERE arm=?", (arm,)).fetchall()
    return {(r["question_id"], r["variant"]) for r in rows}


def billed_tokens(judgments) -> int:
    """tokens_in is repeated on every answer of a request; count it once per unit."""
    per_unit = {}
    for j in judgments:
        if j.tokens_in:
            per_unit[j.unit_id] = j.tokens_in
    return sum(per_unit.values())


def main(argv=None) -> int:
    from hces.config import load
    from hces.judge import JevJudge

    ap = argparse.ArgumentParser(prog="python -m hces.judge_all")
    ap.add_argument("slug")
    ap.add_argument("--yes", action="store_true", help="required: this spends JEV credit")
    ap.add_argument("--cap", type=float, default=1.80, help="stop if projected total spend passes this (USD)")
    ap.add_argument("--only", help="question suffix, e.g. q01")
    ap.add_argument("--shape", choices=SHAPES)
    ap.add_argument("--second-rubric", action="store_true",
                    help="judge only the questions in rubrics/<slug>-v2.jsonl with that rubric, as arm 'judge-rubric2'")
    ap.add_argument("--repeat", action="store_true",
                    help="judge again as arm 'judge-repeat' to measure run-to-run noise; arms keep using 'judge'")
    a = ap.parse_args(argv)
    if not a.yes:
        raise SystemExit("This spends JEV credit; pass --yes")
    cfg = load()
    if a.second_rubric and a.repeat:
        raise SystemExit("--second-rubric and --repeat are separate measurements; pass one")
    rubrics = rubrics_for(a.slug, "-v2" if a.second_rubric else "")
    questions = [q for q in key_rows(a.slug) if (not a.only or q["id"].endswith("/" + a.only))
                 and (not a.second_rubric or q["id"] in rubrics)]
    missing = [q["id"] for q in questions if q["id"] not in rubrics]
    if missing:
        raise SystemExit(f"No rubric for {missing}")
    shapes = [a.shape] if a.shape else list(SHAPES)
    units = {s: [Unit(r["id"], r["text"], parent_id=r["parent_id"], source=a.slug, tokens=r["tokens"])
                 for r in P.load_passages(a.slug, s)] for s in shapes}
    total_requests = sum(len(units[s]) for s in shapes) * len(questions)
    store = Store(cfg.results_store)
    arm = "judge-rubric2" if a.second_rubric else ("judge-repeat" if a.repeat else "judge")
    done = done_pairs(store, arm)
    judge = JevJudge(cfg.jev_model, cfg.judge_workers, cfg.price_per_million, cfg.state_cap_question)
    log = output_dir() / "judge-progress.log"
    spent, requests, errors = 0.0, 0, 0
    for q in questions:
        rub = rubrics[q["id"]]
        store.add_rubric(rub)
        for s in shapes:
            if (q["id"], s) in done:
                continue
            run_id = new_run_id()
            started = time.time()
            with RunClock() as clock:
                with clock.span("access"):
                    batch = units[s]
                with clock.span("analysis"):
                    judgments = judge.judge(q["question"], rub, batch)
                with clock.span("response"):
                    store.add_judgments(run_id, rub, judgments)
            tokens = billed_tokens(judgments)
            cost = tokens * cfg.price_per_million / 1e6
            failed = len({j.unit_id for j in judgments if j.failed})
            store.add_run({"run_id": run_id, "arm": arm, "variant": s, "k": len(batch), "question_id": q["id"],
                           "budget": cfg.token_budget, "judge_model": cfg.jev_model, "rubric_id": rub.rubric_id,
                           "rubric_version": rub.version, "access_ms": clock.ms["access"],
                           "analysis_ms": clock.ms["analysis"], "response_ms": clock.ms["response"],
                           "peak_rss_mb": clock.peak_rss_mb, "tokens_in": tokens, "cost_usd": cost,
                           "started_at": started, "notes": {"requests": len(batch), "failed_units": failed}})
            spent += cost
            requests += len(batch)
            errors += failed
            projected = spent / requests * total_requests + ANSWERABILITY_RESERVE
            line = {"at": time.strftime("%H:%M:%S"), "question": q["id"], "shape": s, "requests": len(batch),
                    "failed": failed, "tokens": tokens, "tokens_per_request": round(tokens / max(1, len(batch))),
                    "cost": round(cost, 4), "spent": round(spent, 4), "projected": round(projected, 3),
                    "analysis_s": round(clock.ms["analysis"] / 1000, 1), "peak_rss_mb": clock.peak_rss_mb}
            with open(log, "a", encoding="utf-8", newline="\n") as f:
                f.write(json.dumps(line) + "\n")
            print(json.dumps(line), flush=True)
            if failed > len(batch) // 10:
                raise SystemExit(f"{failed} of {len(batch)} requests failed on {q['id']} {s}; stopping")
            if projected > a.cap:
                raise SystemExit(f"Projected spend ${projected:.2f} passes the ${a.cap:.2f} cap; stopping")
    store.close()
    print(json.dumps({"done": True, "spent": round(spent, 4), "requests": requests, "failed": errors}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
