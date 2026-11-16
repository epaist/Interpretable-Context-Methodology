"""Scorecard for one volume from results.db: every arm, variant and k side by side.

  python -m hces.report <slug>

Writes stages/03-pipeline-v0/output/run-report-<slug>.md (tables only; the reading goes in by hand).
"""

from __future__ import annotations

import argparse
import json
import statistics
from collections import defaultdict

from hces.rag import key_rows, output_dir
from hces.store import Store

ARM_ORDER = {"rag": 0, "rag+jev": 1, "jev-all": 2}


def pct(xs: list[bool]) -> str:
    return f"{100 * sum(xs) / len(xs):.0f}%" if xs else "n/a"


def latest_runs(store: Store, qids: set[str]) -> list[dict]:
    """One row per (arm, variant, k, question): the most recent, so reruns replace nothing but are not double counted."""
    rows = store.db.execute("SELECT * FROM runs WHERE arm IN ('rag','rag+jev','jev-all') ORDER BY started_at").fetchall()
    last = {}
    for r in rows:
        if r["question_id"] in qids:
            last[(r["arm"], r["variant"], r["k"] if r["arm"] != "jev-all" else 0, r["question_id"])] = dict(r)
    for r in last.values():
        r["notes"] = json.loads(r["notes"])
    return list(last.values())


def rescore(store: Store, runs: list[dict], key: dict[str, dict]) -> None:
    """Score gold and decoys from the stored decisions against the current answer key, not the run notes,
    so a key revision rescores old runs without new JEV calls."""
    for r in runs:
        q = key[r["question_id"]]
        shape = r["variant"].split("/")[-1]
        kept = {row[0] for row in store.db.execute("SELECT unit_id FROM decisions WHERE run_id=? AND kept=1",
                                                   (r["run_id"],))}
        r["notes"]["gold_kept"] = len(kept & set(q["gold"][shape]))
        r["notes"]["decoys_kept"] = len(kept & set(q["decoy_gold"][shape]))


def table(runs: list[dict]) -> list[str]:
    groups = defaultdict(list)
    for r in runs:
        groups[(r["arm"], r["variant"], r["k"] if r["arm"] != "jev-all" else "all")].append(r)
    head = ["| Arm | Variant | k | Gold kept | Needles kept | Real kept | Low overlap kept | Decoys kept "
            "| Unanswerable flagged | Wrongly flagged | Median tokens | Median analysis ms | Cost USD |",
            "|-----|---------|---|-----------|--------------|-----------|------------------|-------------|"
            "-----------------------|-----------------|---------------|--------------------|----------|"]
    out = []
    for (arm, variant, k), rs in sorted(groups.items(), key=lambda kv: (ARM_ORDER[kv[0][0]], kv[0][1], str(kv[0][2]).zfill(4))):
        ans = [r for r in rs if r["notes"]["answerable"]]
        un = [r for r in rs if not r["notes"]["answerable"]]
        kept = lambda xs: [r["notes"]["gold_kept"] > 0 for r in xs]  # noqa: E731
        needles = [r for r in ans if "needle" in r["notes"]["hard_case"]]
        real = [r for r in ans if "needle" not in r["notes"]["hard_case"]]
        low = [r for r in ans if "low-overlap" in r["notes"]["hard_case"]]
        flag = "says_not_in_docs" in rs[0]["notes"]
        out.append(
            f"| {arm} | {variant} | {k} | {pct(kept(ans))} | {pct(kept(needles))} | {pct(kept(real))} | {pct(kept(low))} "
            f"| {sum(r['notes']['decoys_kept'] for r in rs)} "
            f"| {pct([r['notes']['says_not_in_docs'] for r in un]) if flag else 'n/a'} "
            f"| {pct([r['notes']['says_not_in_docs'] for r in ans]) if flag else 'n/a'} "
            f"| {statistics.median(r['notes']['tokens_used'] for r in rs):.0f} "
            f"| {statistics.median(r['analysis_ms'] for r in rs):.0f} | {sum(r['cost_usd'] for r in rs):.4f} |")
    return head + out


def main(argv=None) -> int:
    from hces.config import load

    ap = argparse.ArgumentParser(prog="python -m hces.report")
    ap.add_argument("slug")
    a = ap.parse_args(argv)
    cfg = load()
    qs = key_rows(a.slug)
    store = Store(cfg.results_store)
    runs = latest_runs(store, {q["id"] for q in qs})
    rescore(store, runs, {q["id"]: q for q in qs})
    judge = store.db.execute("SELECT count(*) n, sum(cost_usd) c, sum(tokens_in) t, max(peak_rss_mb) m, "
                             "sum(analysis_ms) ms FROM runs WHERE arm='judge' AND question_id LIKE ?",
                             (a.slug + "/%",)).fetchone()
    misses = defaultdict(set)
    for r in runs:
        if r["notes"]["answerable"] and r["notes"]["gold_kept"] == 0:
            misses[r["question_id"]].add(f"{r['arm']} {r['variant']} k{r['k']}")
    lines = [f"# Stage 03 Run Report: {a.slug}", "",
             f"{len(qs)} questions ({sum(q['answerable'] for q in qs)} answerable), token budget {cfg.token_budget}, "
             f"judge {cfg.jev_model}. Gold kept = at least one gold passage in the final context, "
             f"scored from stored decisions against the current answer key.", "",
             f"Judge pass: {judge['n']} runs, {judge['t']:,} tokens billed, ${judge['c']:.4f}, "
             f"{judge['ms'] / 1000:.0f} s of judging, peak {judge['m']} MB.", "", "## Scorecard", ""] + table(runs)
    lines += ["", "## Questions never kept by some runs", "", "| Question | Runs that missed |", "|----------|------------------|"]
    for qid in sorted(misses):
        lines.append(f"| {qid.split('/')[1]} | {len(misses[qid])} of {sum(1 for r in runs if r['question_id'] == qid)} |")
    (output_dir() / f"run-report-{a.slug}.md").write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
