"""The one needle planter.

A needle is a short invented paragraph inserted between two real paragraphs of a volume, so that
it lands in a passage like any other text. Needle definitions live in stage 02 output
(`needles.jsonl`), never only in the text. Each definition has:

  id        stable key, e.g. "moonstone/n03" (never written into the volume)
  volume    slug
  at        position in the book as a fraction, 0.0 to 1.0
  text      the paragraph to insert
  question  the question only this needle answers
  answer    the short answer

Planting is deterministic: the same plain text and definitions give the same output.
"""

from __future__ import annotations

import json
import re
from dataclasses import replace
from pathlib import Path


def boundaries(plain: str, chapters) -> list[int]:
    """Offsets where a paragraph may be inserted: after a blank line, inside a chapter body,
    not right after a heading line and not before the next chapter."""
    starts = {c.start_char for c in chapters}
    out = []
    for m in re.finditer(r"\n[ \t]*\n(?=[ \t]*\S)", plain):
        pos = m.end()
        line = plain[pos : plain.find("\n", pos) if "\n" in plain[pos:] else len(plain)].strip()
        prev = plain[plain.rfind("\n", 0, m.start()) + 1 : m.start()].strip()
        if pos in starts or not line or len(line) < 40 or len(prev) < 40:
            continue  # skip headings, short lines and chapter starts
        if any(c.start_char < pos < c.start_char + 200 for c in chapters):
            continue
        out.append(pos)
    return out


def plant(plain: str, chapters, needles: list[dict]) -> tuple[str, list, dict[str, tuple[int, int]]]:
    """Insert needle paragraphs. Returns (new plain, chapters with shifted offsets, needle id -> span)."""
    if not needles:
        return plain, chapters, {}
    ids = [n["id"] for n in needles]
    if len(set(ids)) != len(ids):
        raise ValueError("duplicate needle ids")
    spots = boundaries(plain, chapters)
    if not spots:
        raise ValueError("no place to plant needles")
    chosen: dict[int, list[dict]] = {}
    for n in needles:
        if not 0.0 <= float(n["at"]) <= 1.0:
            raise ValueError(f"{n['id']}: at must be in 0..1")
        target = float(n["at"]) * len(plain)
        pos = min(spots, key=lambda p: (abs(p - target), p))
        chosen.setdefault(pos, []).append(n)
    pieces, spans, shift_at, cur, added = [], {}, [], 0, 0
    for pos in sorted(chosen):
        pieces.append(plain[cur:pos])
        for n in chosen[pos]:
            text = re.sub(r"\s+", " ", n["text"]).strip()
            start = pos + added
            pieces.append(text + "\n\n")
            spans[n["id"]] = (start, start + len(text))
            added += len(text) + 2
        shift_at.append((pos, added))
        cur = pos
    pieces.append(plain[cur:])

    def moved(x: int) -> int:  # needles never sit at a chapter start, so x > pos is unambiguous
        return x + max([total for pos, total in shift_at if x > pos], default=0)

    new_chapters = [replace(c, start_char=moved(c.start_char), end_char=moved(c.end_char)) for c in chapters]
    new_chapters[-1] = replace(new_chapters[-1], end_char=len(plain) + added)
    return "".join(pieces), new_chapters, spans


def load(path: Path, volume: str) -> list[dict]:
    if not path.exists():
        return []
    rows = [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]
    return [r for r in rows if r["volume"] == volume]
