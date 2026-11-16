"""Build and audit the stage 02 answer key.

  python -m hces.answer_key

Inputs, in stages/02-test-material/output/:
  questions.jsonl  real-text questions: evidence quotes for answerable ones, absent terms for the rest
  needles.jsonl    planted needles (with their questions) and lookalike decoys

For each volume it rebuilds the passages with the needles planted, turns every evidence quote into
gold passage IDs for both shapes, checks each needle is the only place its answer appears, and
writes answer-key.jsonl, volumes.md and audit.md. Any failed check stops the run.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from hces import passages as P

VOLUMES = {  # slug: (title, author, Gutenberg id, target tokens)
    "secret-adversary": ("The Secret Adversary", "Agatha Christie", 1155, 100_000),
    "moonstone": ("The Moonstone", "Wilkie Collins", 155, 250_000),
    "way-we-live-now": ("The Way We Live Now", "Anthony Trollope", 5231, 500_000),
}
SIZE_TOLERANCE = 0.20


def stage_dir() -> Path:
    from hces.config import ROOT

    return ROOT / "workspaces" / "hces-lab" / "stages" / "02-test-material" / "output"


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]


def quote_pattern(quote: str) -> re.Pattern:
    """Match a quote whatever the line breaks and runs of spaces in the book."""
    return re.compile(r"\s+".join(re.escape(w) for w in quote.split()))


def url(gid: int) -> str:
    return f"https://www.gutenberg.org/cache/epub/{gid}/pg{gid}.txt"


def build_all(out: Path | None = None, volumes_root: Path | None = None, count=None) -> dict:
    out = out or stage_dir()
    questions = read_jsonl(out / "questions.jsonl")
    needles = read_jsonl(out / "needles.jsonl")
    count = count or P.TokenCounter()
    failures: list[str] = []
    key: list[dict] = []
    stats: dict[str, dict] = {}
    for slug, (title, author, gid, target) in VOLUMES.items():
        vn = [n for n in needles if n["volume"] == slug]
        st = P.build(slug, title, author, url(gid), count=count, root=volumes_root, needles=vn)
        stats[slug] = {**st, "target": target}
        if abs(st["book_tokens"] - target) > SIZE_TOLERANCE * target:
            failures.append(f"{slug}: {st['book_tokens']} tokens is not within 20% of {target}")
        plain = ((volumes_root or P.volumes_dir()) / slug / "plain.txt").read_text(encoding="utf-8")
        spans = {}
        for n in vn:
            text = re.sub(r"\s+", " ", n["text"]).strip()
            k = plain.find(text)
            if k < 0 or plain.find(text, k + 1) >= 0:
                failures.append(f"{n['id']}: planted text not found exactly once")
                continue
            spans[n["id"]] = (k, k + len(text))
        decoys = {}
        for n in vn:
            if n["role"] == "decoy":
                decoys.setdefault(n["decoy_of"], []).append(n["id"])
        for n in (n for n in vn if n["role"] == "needle" and n["id"] in spans):
            hits = [m.start() for m in re.finditer(re.escape(n["unique"]), plain, re.I)]
            s, e = spans[n["id"]]
            if len(hits) != 1 or not s <= hits[0] < e:
                failures.append(f"{n['id']}: '{n['unique']}' appears {len(hits)} times, must be once, inside the needle")
            for d in decoys.get(n["id"], []):
                ds, de = spans.get(d, (0, 0))
                if n["unique"].lower() in plain[ds:de].lower():
                    failures.append(f"{d}: decoy contains the answer")
            ids = P.locate(slug, s, e, volumes_root)
            key.append({"id": n["id"], "volume": slug, "question": n["question"], "answer": n["answer"],
                        "answerable": True, "gold": ids, "needle_id": n["id"],
                        "decoy_ids": decoys.get(n["id"], []),
                        "decoy_gold": {sh: sorted({i for d in decoys.get(n["id"], []) if d in spans
                                                   for i in P.locate(slug, *spans[d], volumes_root)[sh]})
                                       for sh in ("chaptered", "plain")},
                        "hard_case": ["needle"] + (["lookalike"] if decoys.get(n["id"]) else [])})
        for q in (q for q in questions if q["volume"] == slug):
            gold = {"chaptered": set(), "plain": set()}
            if q["answerable"]:
                if not q.get("evidence"):
                    failures.append(f"{q['id']}: answerable with no evidence")
                for quote in q.get("evidence", []):
                    ms = list(quote_pattern(quote).finditer(plain))
                    if not ms:
                        failures.append(f"{q['id']}: evidence not found: {quote[:60]}")
                    for m in ms:
                        for sh, ids in P.locate(slug, m.start(), m.end(), volumes_root).items():
                            gold[sh].update(ids)
            else:
                for term in q.get("absent", []):
                    if re.search(re.escape(term), plain, re.I):
                        failures.append(f"{q['id']}: unanswerable but '{term}' is in the text")
            lookalike = {"chaptered": set(), "plain": set()}
            for quote in q.get("decoy_evidence", []):  # real passages that look like an answer but are wrong
                ms = list(quote_pattern(quote).finditer(plain))
                if not ms:
                    failures.append(f"{q['id']}: decoy evidence not found: {quote[:60]}")
                for m in ms:
                    for sh, ids in P.locate(slug, m.start(), m.end(), volumes_root).items():
                        lookalike[sh].update(ids)
            for sh in gold:  # a passage holding both the answer and a lookalike still answers: gold wins
                lookalike[sh] -= gold[sh]
            if q.get("decoy_evidence") and not lookalike["chaptered"]:
                failures.append(f"{q['id']}: every decoy passage is also gold in chaptered")
            key.append({"id": q["id"], "volume": slug, "question": q["question"], "answer": q["answer"],
                        "answerable": q["answerable"], "gold": {k: sorted(v) for k, v in gold.items()},
                        "needle_id": None, "decoy_ids": [], "decoy_gold": {k: sorted(v) for k, v in lookalike.items()},
                        "hard_case": q.get("tags", [])})
    known = set()
    for slug in VOLUMES:
        with open((volumes_root or P.volumes_dir()) / slug / "passages.jsonl", encoding="utf-8") as f:
            known.update(json.loads(l)["id"] for l in f)
    for row in key:
        for ids in list(row["gold"].values()) + list(row["decoy_gold"].values()):
            failures.extend(f"{row['id']}: unknown passage {i}" for i in ids if i not in known)
        if row["answerable"] and not all(row["gold"].values()):
            failures.append(f"{row['id']}: answerable with no gold passage in a shape")
    report = audit_report(key, stats, failures)
    (out / "audit.md").write_text(report, encoding="utf-8", newline="\n")
    if failures:
        raise SystemExit("Audit failed:\n" + "\n".join(failures))
    with open(out / "answer-key.jsonl", "w", encoding="utf-8", newline="\n") as f:
        for row in key:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    (out / "volumes.md").write_text(volumes_md(stats), encoding="utf-8", newline="\n")
    return {"rows": len(key), "stats": stats}


def volumes_md(stats: dict) -> str:
    rows = "".join(
        f"| {s['title']} | {s['author']} | {s['url']} | {s['book_tokens']:,} | {s['target']:,} | {s['chapters']} "
        f"| {s['chaptered_passages']} | {s['plain_passages']} | {s['planted']} |\n" for s in stats.values())
    return ("# Volumes\n\nTokens are bge-small tokens over all plain-shape passages, needles included.\n\n"
            "| Title | Author | Source | Tokens | Target | Chapters | Chaptered passages | Plain passages | Planted |\n"
            "|-------|--------|--------|--------|--------|----------|--------------------|----------------|---------|\n"
            + rows)


def audit_report(key: list[dict], stats: dict, failures: list[str]) -> str:
    lines = ["# Stage 02 Audit", "", "| Check | Result |", "|-------|--------|"]
    for slug, s in stats.items():
        lines.append(f"| Size {slug} | {s['book_tokens']:,} vs {s['target']:,} ({(s['book_tokens'] / s['target'] - 1):+.0%}) |")
    for slug in stats:
        rows = [r for r in key if r["volume"] == slug]
        real = [r for r in rows if not r["needle_id"]]
        lines.append(f"| Questions {slug} | {len(real)} real ({sum(not r['answerable'] for r in real)} unanswerable), "
                     f"{len(rows) - len(real)} needle |")
    golds = [len(r["gold"]["plain"]) for r in key if r["answerable"]] or [0]
    lines.append(f"| Gold per answerable question | min {min(golds)}, max {max(golds)} (plain shape) |")
    lines.append(f"| Failures | {len(failures)} |")
    lines += [""] + [f"- {f}" for f in failures]
    return "\n".join(lines) + "\n"


def main() -> int:
    print(json.dumps(build_all()["rows"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
