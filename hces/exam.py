"""Stage 04 exam: tune keep cutoffs on two volumes, test on the third, rotate, pool, freeze.

  python -m hces.exam                       rotation, pooled result, frozen cutoffs
  python -m hces.exam --noise <slug>        kept-set overlap between two judge passes
  python -m hces.exam --confirm             fresh questions, frozen cutoffs, answerability (JEV calls)
  python -m hces.exam --rubric2             kept-set overlap, first rubric vs second rubric

Works offline from stored judgments and RAG decisions; no JEV calls. The arm is RAG + JEV with the
retrieval chosen in stage 04 step 1 (hybrid, k 50), both shapes. Answerability is not tuned here:
its yes-probability depends on the kept set, so it is measured with real calls once cutoffs freeze.

Selection rule, fixed before any scoring:
  1. most answerable questions with at least one gold passage kept (recall first)
  2. then the highest mean share of kept tokens that are gold
  3. then the fewest lookalike or decoy passages kept
  4. then the fewest median kept tokens
"""

from __future__ import annotations

import argparse
import itertools
import json
import statistics
from dataclasses import asdict

from hces import passages as P
from hces.arms import judged, rag_candidates, scored
from hces.judge_all import rubrics_for
from hces.rag import key_rows
from hces.rollup import Cutoffs, fill
from hces.store import Store
from hces.units import Unit

VOLUMES = ("secret-adversary", "moonstone", "way-we-live-now")
VARIANT, K = "hybrid", 50
OFF = 1.01  # a threshold no score or probability reaches
GRID = [Cutoffs(c, u, p) for c, u, p in itertools.product(
    (0.5, 0.75, 1.0), (0.25, 0.5, 0.75, OFF), (0.3, 0.5, 0.7, 0.9, OFF)) if u <= c or u == OFF]


def output_dir():
    from hces.config import ROOT

    return ROOT / "workspaces" / "hces-lab" / "stages" / "04-exam" / "output"


def cases(store: Store, slug: str, arm: str = "judge", fresh: bool = False, only: set | None = None) -> list[dict]:
    """Exam cases for one volume. The fresh confirmation set is kept out unless fresh=True, and then only it."""
    rubrics = rubrics_for(slug)
    out = []
    for shape in ("chaptered", "plain"):
        units = {r["id"]: Unit(r["id"], "", tokens=r["tokens"]) for r in P.load_passages(slug, shape)}
        for q in key_rows(slug):
            if ("fresh" in q["hard_case"]) != fresh or (only is not None and q["id"] not in only):
                continue
            j, _ = judged(store, q["id"], shape, arm)
            ranked = rag_candidates(store, q["id"], shape)[(VARIANT, K)][0]
            out.append({"id": q["id"], "shape": shape, "answerable": q["answerable"],
                        "needle": "needle" in q["hard_case"], "gold": set(q["gold"][shape]),
                        "decoys": set(q["decoy_gold"][shape]), "units": scored(units, j, rubrics[q["id"]], ranked)})
    return out


def evaluate(cs: list[dict], c: Cutoffs, budget: int) -> dict:
    caught, needles, share, decoys, tokens = [], [], [], 0, []
    for x in cs:
        kept, _ = fill(x["units"], budget, c)
        ids = {u.unit_id for u, _ in kept}
        used = sum(u.tokens for u, _ in kept)
        tokens.append(used)
        decoys += len(ids & x["decoys"])
        if x["answerable"]:
            hit = bool(ids & x["gold"])
            caught.append(hit)
            if x["needle"]:
                needles.append(hit)
            share.append(sum(u.tokens for u, _ in kept if u.unit_id in x["gold"]) / used if used else 0.0)
    return {"gold_caught": sum(caught), "answerable": len(caught), "needles_caught": sum(needles),
            "needles": len(needles), "gold_share": statistics.mean(share) if share else 0.0,
            "decoys_kept": decoys, "median_tokens": statistics.median(tokens) if tokens else 0}


def rank_key(m: dict) -> tuple:
    return (-m["gold_caught"], -m["gold_share"], m["decoys_kept"], m["median_tokens"])


def best(cs: list[dict], budget: int) -> tuple[Cutoffs, dict]:
    scored_grid = [(c, evaluate(cs, c, budget)) for c in GRID]
    return min(scored_grid, key=lambda cm: rank_key(cm[1]))


def pct(a: int, b: int) -> str:
    return f"{100 * a / b:.0f}%" if b else "n/a"


def row(label: str, c: Cutoffs, m: dict) -> str:
    return (f"| {label} | {c.cutoff:g} | {c.unsure_low:g} | {c.critical_at:g} | {pct(m['gold_caught'], m['answerable'])} "
            f"| {pct(m['needles_caught'], m['needles'])} | {m['gold_share']:.2f} | {m['decoys_kept']} | {m['median_tokens']:.0f} |")


def overlap(a: set, b: set) -> float:
    return len(a & b) / len(a | b) if a | b else 1.0


def compare(first: list[dict], second: list[dict], c: Cutoffs, budget: int) -> dict:
    """Kept-set agreement between two judge passes over the same cases (repeat run or second rubric)."""
    by_key = {(x["id"], x["shape"]): x for x in second}
    jac, same_gold = [], []
    for x in first:
        y = by_key[(x["id"], x["shape"])]
        a = {u.unit_id for u, _ in fill(x["units"], budget, c)[0]}
        b = {u.unit_id for u, _ in fill(y["units"], budget, c)[0]}
        jac.append(overlap(a, b))
        if x["answerable"]:
            same_gold.append(bool(a & x["gold"]) == bool(b & y["gold"]))
    return {"cases": len(jac), "mean_overlap": statistics.mean(jac), "min_overlap": min(jac),
            "identical": sum(j == 1.0 for j in jac), "same_gold_outcome": sum(same_gold), "answerable": len(same_gold)}


def noise(store: Store, slug: str, budget: int) -> int:
    frozen = Cutoffs(**json.loads((output_dir() / "cutoffs.json").read_text(encoding="utf-8"))["cutoffs"])
    m = compare(cases(store, slug), cases(store, slug, "judge-repeat"), frozen, budget)
    lines = ["# Stage 04 Run-to-Run Noise", "", f"{slug}, every passage judged twice with the same rubric, "
             f"kept sets compared with the frozen cutoffs ({frozen.cutoff:g}, {frozen.unsure_low:g}, {frozen.critical_at:g}).", "",
             "| Cases | Mean kept-set overlap | Lowest | Identical kept sets | Same gold outcome |",
             "|-------|-----------------------|--------|---------------------|-------------------|",
             f"| {m['cases']} | {m['mean_overlap']:.3f} | {m['min_overlap']:.3f} | {m['identical']} of {m['cases']} "
             f"| {m['same_gold_outcome']} of {m['answerable']} |"]
    (output_dir() / "noise.md").write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print("\n".join(lines))
    return 0


def confirm(store: Store, cfg) -> int:
    """Fresh questions, frozen cutoffs, real answerability calls."""
    from hces.arms import NOT_IN_DOCS_BELOW, ask_answerable
    from hces.judge import JevJudge

    frozen = Cutoffs(**json.loads((output_dir() / "cutoffs.json").read_text(encoding="utf-8"))["cutoffs"])
    judge = JevJudge(cfg.jev_model, cfg.judge_workers, cfg.price_per_million, cfg.state_cap_question)
    lines = ["# Stage 04 Confirmation on Fresh Questions", "",
             f"Frozen cutoffs ({frozen.cutoff:g}, {frozen.unsure_low:g}, {frozen.critical_at:g}), RAG + JEV, {VARIANT}, k {K}. "
             "Questions written after the cutoffs froze.", "",
             "| Question | Shape | Answerable | Gold kept | Kept tokens | Answer p | Says not in docs | Right |",
             "|----------|-------|------------|-----------|-------------|----------|------------------|-------|"]
    right, total, tokens = 0, 0, 0
    for slug in VOLUMES:
        rubrics = rubrics_for(slug)
        qs = {q["id"]: q for q in key_rows(slug)}
        for x in cases(store, slug, fresh=True):
            texts = {r["id"]: r["text"] for r in P.load_passages(slug, x["shape"])}
            kept = [u for u, _ in fill(x["units"], cfg.token_budget, frozen)[0]]
            p = ask_answerable(judge, qs[x["id"]]["question"], rubrics[x["id"]],
                               [Unit(u.unit_id, texts[u.unit_id], tokens=u.tokens) for u in kept])
            tokens += judge.last_tokens
            gold = bool({u.unit_id for u in kept} & x["gold"])
            nid = p < NOT_IN_DOCS_BELOW
            ok = (gold and not nid) if x["answerable"] else nid
            right += ok
            total += 1
            lines.append(f"| {x['id'].split('/')[1]} {slug} | {x['shape']} | {'yes' if x['answerable'] else 'no'} "
                         f"| {'yes' if gold else ('n/a' if not x['answerable'] else 'no')} | {sum(u.tokens for u in kept)} "
                         f"| {p:.2f} | {'yes' if nid else 'no'} | {'yes' if ok else 'NO'} |")
    lines += ["", f"Right: {right} of {total}. Answerability tokens billed: {tokens:,} (${tokens * cfg.price_per_million / 1e6:.4f})."]
    (output_dir() / "confirm.md").write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print("\n".join(lines))
    return 0


def rubric2(store: Store, budget: int) -> int:
    """Kept-set overlap between the frozen rubric and a second rubric written from the same prompt."""
    frozen = Cutoffs(**json.loads((output_dir() / "cutoffs.json").read_text(encoding="utf-8"))["cutoffs"])
    first, second = [], []
    for slug in VOLUMES:
        ids = set(rubrics_for(slug, "-v2"))
        first += cases(store, slug, only=ids)
        second += cases(store, slug, "judge-rubric2", only=ids)
    m = compare(first, second, frozen, budget)
    lines = ["# Stage 04 Second Rubric", "", f"{m['cases'] // 2} questions, both shapes, kept sets compared with the frozen "
             f"cutoffs ({frozen.cutoff:g}, {frozen.unsure_low:g}, {frozen.critical_at:g}). Compare with noise.md.", "",
             "| Cases | Mean kept-set overlap | Lowest | Identical kept sets | Same gold outcome |",
             "|-------|-----------------------|--------|---------------------|-------------------|",
             f"| {m['cases']} | {m['mean_overlap']:.3f} | {m['min_overlap']:.3f} | {m['identical']} of {m['cases']} "
             f"| {m['same_gold_outcome']} of {m['answerable']} |"]
    (output_dir() / "rubric2.md").write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print("\n".join(lines))
    return 0


def main(argv=None) -> int:
    from hces.config import load

    ap = argparse.ArgumentParser(prog="python -m hces.exam")
    ap.add_argument("--noise", metavar="SLUG", help="compare the judge and judge-repeat passes for one volume")
    ap.add_argument("--confirm", action="store_true", help="fresh questions with frozen cutoffs; spends JEV credit")
    ap.add_argument("--rubric2", action="store_true", help="compare the first and second rubric kept sets")
    a = ap.parse_args(argv)
    cfg = load()
    store = Store(cfg.results_store)
    if a.noise:
        return noise(store, a.noise, cfg.token_budget)
    if a.confirm:
        return confirm(store, cfg)
    if a.rubric2:
        return rubric2(store, cfg.token_budget)
    by_vol = {v: cases(store, v) for v in VOLUMES}
    head = ["| Set | Cutoff | Unsure low | Critical at | Gold caught | Needles | Gold share | Decoys kept | Median tokens |",
            "|-----|--------|------------|-------------|-------------|---------|------------|-------------|---------------|"]
    lines = ["# Stage 04 Cutoff Rotation", "", f"Arm: RAG + JEV, {VARIANT}, k {K}, both shapes, budget {cfg.token_budget}. "
             f"{len(GRID)} cutoff settings searched. Cutoffs are 1.01 when switched off.", "", "## Rotation", ""] + head
    pooled = {"gold_caught": 0, "answerable": 0, "needles_caught": 0, "needles": 0, "decoys_kept": 0}
    shares, rotations = [], []
    for test in VOLUMES:
        tune = [x for v in VOLUMES if v != test for x in by_vol[v]]
        c, m_tune = best(tune, cfg.token_budget)
        m_test = evaluate(by_vol[test], c, cfg.token_budget)
        lines += [row(f"tune without {test}", c, m_tune), row(f"test on {test}", c, m_test)]
        for k in pooled:
            pooled[k] += m_test[k]
        shares.append((m_test["gold_share"], m_test["answerable"]))
        rotations.append({"test": test, "cutoffs": asdict(c), "tune": m_tune, "test_result": m_test})
    pooled["gold_share"] = sum(s * n for s, n in shares) / max(1, sum(n for _, n in shares))
    frozen, m_all = best([x for v in VOLUMES for x in by_vol[v]], cfg.token_budget)
    lines += ["", "## Pooled test result", "",
              f"Gold caught {pct(pooled['gold_caught'], pooled['answerable'])} ({pooled['gold_caught']} of {pooled['answerable']}), "
              f"needles {pct(pooled['needles_caught'], pooled['needles'])}, mean gold share {pooled['gold_share']:.2f}, "
              f"decoys kept {pooled['decoys_kept']}.", "", "## Frozen cutoffs (chosen by the same rule on all three volumes)", ""]
    lines += head + [row("all volumes", frozen, m_all)]
    out = output_dir()
    out.mkdir(parents=True, exist_ok=True)
    (out / "rotation.md").write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    (out / "cutoffs.json").write_text(json.dumps({
        "cutoffs": asdict(frozen), "rubric_version": 1, "jev_model": cfg.jev_model, "variant": VARIANT, "k": K,
        "budget": cfg.token_budget, "rule": __doc__.split("Selection rule, fixed before any scoring:")[1].strip(),
        "rotations": rotations, "pooled_test": pooled}, indent=1), encoding="utf-8", newline="\n")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
