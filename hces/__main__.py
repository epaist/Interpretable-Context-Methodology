"""One command for HCES v1. Run from the home root as `python -m hces <command>`.

  python -m hces gate STAGE_DIR --task "..." --yes
      The ICM gate (Pattern 16): judges every reference section a stage's Inputs table names against the task,
      keeps what passes the frozen cutoffs, writes the manifest. JEV only (pennies).

  python -m hces remember --store memory.sqlite --file note.md [--date 2026-11-15] [--kind note] --yes
      One dated record into a memory store: facts extracted (local model by default), keyed, linked by JEV.

  python -m hces recall --store memory.sqlite "What is the refund window?" [--as-of 2026-11-15]
      The current value of the facts nearest the question, as of a date, with their history, and a one-line answer.

The local model is llama-server on 127.0.0.1:11435 (alias qwen9b) and costs nothing; --claude uses the Claude API
instead and needs ANTHROPIC_API_KEY. Every command that spends credit needs --yes.
"""

from __future__ import annotations

import argparse
import hashlib
import sys
from datetime import date
from pathlib import Path


def client_for(a):
    if a.claude:
        if not a.yes:
            raise SystemExit("--claude spends Claude credit; pass --yes")
        import anthropic

        return anthropic.Anthropic()
    from hces.local_llm import LocalClient, models

    try:
        have = models()
    except OSError as e:
        raise SystemExit(f"No local model at 127.0.0.1:11435 ({e}). Start llama-server, or pass --claude.")
    if a.model not in have:
        raise SystemExit(f"Local server has {have}, not {a.model!r}")
    return LocalClient(a.model)


def tools():
    from hces.config import load as load_cfg
    from hces.embed import FastEmbedder
    from hces.judge import JevJudge

    cfg = load_cfg()
    return cfg, FastEmbedder(cfg.embedder), JevJudge(cfg.jev_model, cfg.judge_workers, cfg.price_per_million, cfg.state_cap_question)


def record(path: Path, day: str | None, kind: str, rid: str | None) -> dict:
    text = path.read_text(encoding="utf-8").strip()
    if not text:
        raise SystemExit(f"{path} is empty")
    day = day or date.today().isoformat()
    date.fromisoformat(day)  # fails on a malformed date
    return {"id": rid or f"{path.stem}-{hashlib.sha1(text.encode()).hexdigest()[:8]}", "date": day, "kind": kind, "text": text}


def remember(a) -> int:
    from hces import memory as M

    if not a.yes:
        raise SystemExit("remember spends JEV credit (and Claude credit with --claude); pass --yes")
    rec = record(a.file, a.date, a.kind, a.id)
    mem = M.Memory(a.store)
    if rec["id"] in mem.done_records():
        raise SystemExit(f"{rec['id']} is already in {a.store}; memory is insert-only")
    client = client_for(a)
    cfg, embedder, judge = tools()
    facts = M.ingest(client, mem, rec, embedder, judge, cfg, keyed=True)
    for f in facts:
        print(f"- {f['key']}: {f['subject']}, {f['attribute']}: {f['value']}" + (f" (from {f['effective_date']})" if f["effective_date"] else ""))
    print(f"{rec['id']} ({rec['date']}): {len(facts)} facts; store spend ${mem.spent():.4f}")
    return 0


def recall(a) -> int:
    import time

    from hces import memory as M

    if not Path(a.store).exists():
        raise SystemExit(f"No memory store at {a.store}")
    mem = M.Memory(a.store)
    as_of = a.as_of or date.today().isoformat()
    date.fromisoformat(as_of)
    _, embedder, _ = tools()
    q = {"id": f"recall-{time.time_ns()}", "as_of": as_of, "question": a.question}
    M.ask(client_for(a), mem, q, embedder)
    row = mem.db.execute("SELECT notes, answer FROM answers WHERE question_id = ?", (q["id"],)).fetchone()
    print(row["answer"])
    if a.notes:
        print("\nNotes:\n" + (row["notes"] or "(none)"))
    return 0


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if argv[:1] == ["gate"]:
        from hces import gate

        return gate.main(argv[1:])
    ap = argparse.ArgumentParser(prog="python -m hces", description="HCES v1: gate, remember, recall")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("gate", help="the ICM gate; see python -m hces gate --help")
    for name in ("remember", "recall"):
        p = sub.add_parser(name)
        p.add_argument("--store", required=True, type=Path, help="memory store, a .sqlite file")
        p.add_argument("--model", default="qwen9b", help="local model alias (default qwen9b)")
        p.add_argument("--claude", action="store_true", help="use the Claude API instead of the local model")
    r = sub.choices["remember"]
    r.add_argument("--file", required=True, type=Path, help="the record: a text or markdown file")
    r.add_argument("--date", help="the record's date, YYYY-MM-DD (default today)")
    r.add_argument("--kind", default="note", help="what the record is: note, ticket, SOP, meeting notes")
    r.add_argument("--id", help="record id (default: file name plus a content hash); ids starting sop- or gov- rank as official")
    r.add_argument("--yes", action="store_true")
    c = sub.choices["recall"]
    c.add_argument("question")
    c.add_argument("--as-of", help="answer as of this date, YYYY-MM-DD (default today)")
    c.add_argument("--notes", action="store_true", help="also print the memory notes the answer used")
    c.add_argument("--yes", action="store_true", help="needed with --claude")
    a = ap.parse_args(argv)
    return remember(a) if a.cmd == "remember" else recall(a)


if __name__ == "__main__":
    raise SystemExit(main())
