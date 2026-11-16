"""Cut a Project Gutenberg book into passages with stable IDs.

  python -m hces.passages <slug> --title T --author A --url U

Reads kb/volumes/<slug>/source.txt and writes, beside it:
  plain.txt        the book text only (no Gutenberg header, licence or contents list)
  chaptered.txt    the same text with a marker line before each chapter
  chapters.jsonl   one record per chapter
  passages.jsonl   passages in two shapes: "chaptered" (inside chapters) and "plain" (ignoring them)
  README.md        title, author, source URL, counts

Passages are whole paragraphs packed up to a target size and never over 512 bge tokens.
Offsets point into plain.txt. IDs are written once; a changed source means a new hash.
"""

from __future__ import annotations

import argparse
import glob
import hashlib
import json
import os
import re
import tempfile
from dataclasses import asdict, dataclass
from pathlib import Path

from hces.units import MAX_PASSAGE_TOKENS

TARGET_TOKENS = 300
MIN_CHAPTER_CHARS = 300  # a heading followed by less text is a contents entry or a group title
ORDINALS = "FIRST|SECOND|THIRD|FOURTH|FIFTH|SIXTH|SEVENTH|EIGHTH|NINTH|TENTH"
HEADING = re.compile(
    rf"^(CHAPTER\s+[IVXLC\d]+\b.*|PROLOGUE\.?|EPILOGUE\.?|(?:{ORDINALS})\s+(?:PERIOD|NARRATIVE)\.?|[IVXLC]{{1,7}}\.?)$"
)


HEADING_CHAPTER = re.compile(r"^(CHAPTER\s|[IVXLC]{1,7}$)")


def volumes_dir() -> Path:
    from hces.config import ROOT

    return ROOT / "workspaces" / "hces-lab" / "kb" / "volumes"


class TokenCounter:
    """Counts tokens with bge-small's own tokenizer, special tokens included (what the 512 cap means)."""

    def __init__(self, path: str | None = None):
        from tokenizers import Tokenizer

        path = path or os.environ.get("HCES_TOKENIZER") or self._find()
        self.tok = Tokenizer.from_file(path)
        self.tok.no_truncation()
        self.tok.no_padding()

    @staticmethod
    def _find() -> str:
        pattern = os.path.join(tempfile.gettempdir(), "fastembed_cache", "*bge-small*", "**", "tokenizer.json")
        found = glob.glob(pattern, recursive=True)
        if not found:
            raise FileNotFoundError("bge-small tokenizer.json not found; run the embedder once or set HCES_TOKENIZER")
        return found[0]

    def __call__(self, text: str) -> int:
        return len(self.tok.encode(text).ids)


def strip_gutenberg(text: str) -> str:
    text = text.replace("\r\n", "\n").lstrip("﻿")
    start = re.search(r"^\*\*\* ?START OF TH(E|IS) PROJECT GUTENBERG.*$", text, re.M)
    end = re.search(r"^\*\*\* ?END OF TH(E|IS) PROJECT GUTENBERG.*$", text, re.M)
    if not start or not end:
        raise ValueError("Gutenberg START/END markers not found")
    return text[start.end() : end.start()]


@dataclass
class Chapter:
    id: str
    title: str
    start_char: int
    end_char: int


def find_chapters(body: str) -> tuple[str, list[Chapter]]:
    """Return (plain text from the first real heading on, chapters with offsets into it).

    A heading with less than MIN_CHAPTER_CHARS of text after it is either a contents entry or a
    group title (PROLOGUE, FIRST PERIOD, SECOND NARRATIVE). Group titles prefix the titles of the
    chapters under them and start with them; contents entries are dropped with everything before
    the first real chapter.
    """
    lines = body.split("\n")
    offsets, pos = [], 0
    for line in lines:
        offsets.append(pos)
        pos += len(line) + 1
    heads = [i for i, line in enumerate(lines) if HEADING.match(line.strip())]
    if not heads:
        raise ValueError("No chapter headings found")
    real: list[tuple[int, int, str]] = []  # (start line, heading line, title)
    pending: list[int] = []  # short headings since the last real chapter
    context: list[str] = []
    for n, i in enumerate(heads):
        nxt = heads[n + 1] if n + 1 < len(heads) else len(lines)
        long_enough = len("\n".join(l for l in lines[i + 1 : nxt] if l.strip())) >= MIN_CHAPTER_CHARS
        title = re.sub(r"\s+", " ", lines[i].strip().rstrip("."))
        if not long_enough:
            pending.append(i)
            if not HEADING_CHAPTER.match(title):  # group title
                context = [] if not ("NARRATIVE" in title and context) else context[:1]
                context.append(title)
            continue
        groups = [j for j in pending if not HEADING_CHAPTER.match(lines[j].strip())]
        if not real:  # before the first chapter: keep only group titles after the last contents entry
            last_entry = max([j for j in pending if HEADING_CHAPTER.match(lines[j].strip())], default=-1)
            groups = [j for j in groups if j > last_entry]
            context = [re.sub(r"\s+", " ", lines[j].strip().rstrip(".")) for j in groups]
        start = groups[0] if groups else i
        is_group = not HEADING_CHAPTER.match(title)
        prefix = context if not is_group else (context[:1] if "NARRATIVE" in title and context and "PERIOD" in context[0] else [])
        real.append((start, i, " / ".join(prefix + [title])))
        if is_group:  # PROLOGUE or FOURTH NARRATIVE with its own text: a chapter, not a context
            context = context[:1] if "NARRATIVE" in title else []
        pending = []
    if not real:
        raise ValueError("No chapter has enough text after its heading")
    base = offsets[real[0][0]]
    plain = body[base:].rstrip() + "\n"
    chapters = []
    for n, (start, _, title) in enumerate(real):
        s = offsets[start] - base
        e = (offsets[real[n + 1][0]] - base) if n + 1 < len(real) else len(plain)
        chapters.append(Chapter(f"c{n + 1:03d}", title, s, e))
    return plain, chapters


def paragraphs(text: str, start: int, end: int) -> list[tuple[int, int]]:
    """Paragraph spans (blank-line separated) inside [start, end)."""
    spans = []
    for m in re.finditer(r"\S(?:.*?\S)?(?=[ \t]*\n\s*\n|\s*\Z)", text[start:end], re.S):
        spans.append((start + m.start(), start + m.end()))
    return spans


def split_long(text: str, span: tuple[int, int], count) -> list[tuple[int, int]]:
    """Split one over-long paragraph at sentence ends, then at spaces if one sentence is still too long."""
    s, e = span
    cap = MAX_PASSAGE_TOKENS - 10
    ends = [s + m.end() for m in re.finditer(r"[.!?;:][\"'\u201d\u2019)]*\s+", text[s:e])] + [e]
    out, start, last_ok = [], s, s
    for b in ends:
        if count(text[start:b]) <= cap:
            last_ok = b
            continue
        if last_ok > start:
            out.append((start, last_ok))
            start = last_ok
        while count(text[start:b]) > cap:  # one huge sentence: cut at the last space that fits
            spaces = [start + m.start() for m in re.finditer(r"\s+", text[start:b])]
            fits = [w for w in spaces if w > start and count(text[start:w]) <= cap]
            if not fits:
                raise ValueError(f"cannot split text at {start}")
            out.append((start, fits[-1]))
            start = fits[-1]
        last_ok = b
    if start < e:
        out.append((start, e))
    return [(a, a + len(text[a:b].rstrip())) for a, b in out if text[a:b].strip()]  # drop trailing spaces


def pack(text: str, spans: list[tuple[int, int]], count, target: int = TARGET_TOKENS) -> list[tuple[int, int]]:
    """Pack whole paragraphs into passages near `target` tokens, never over the cap."""
    units: list[tuple[int, int]] = []
    for sp in spans:
        units.extend(split_long(text, sp, count) if count(text[sp[0]:sp[1]]) > MAX_PASSAGE_TOKENS - 10 else [sp])
    out: list[tuple[int, int]] = []
    cur: tuple[int, int] | None = None
    for sp in units:
        if cur is None:
            cur = sp
            continue
        joined = (cur[0], sp[1])
        if count(text[cur[0]:cur[1]]) < target and count(text[joined[0]:joined[1]]) <= MAX_PASSAGE_TOKENS:
            cur = joined
        else:
            out.append(cur)
            cur = sp
    if cur:
        out.append(cur)
    return out


def needles_file() -> Path:
    from hces.config import ROOT

    return ROOT / "workspaces" / "hces-lab" / "stages" / "02-test-material" / "output" / "needles.jsonl"


def build(slug: str, title: str, author: str, url: str, count=None, root: Path | None = None,
          needles: list[dict] | None = None) -> dict:
    from hces import planter

    count = count or TokenCounter()
    vdir = (root or volumes_dir()) / slug
    body = strip_gutenberg((vdir / "source.txt").read_text(encoding="utf-8"))
    plain, chapters = find_chapters(body)
    needles = planter.load(needles_file(), slug) if needles is None else needles
    plain, chapters, needle_spans = planter.plant(plain, chapters, needles)
    source_hash = hashlib.sha256(plain.encode("utf-8")).hexdigest()
    records = []
    for ch in chapters:
        for n, (s, e) in enumerate(pack(plain, paragraphs(plain, ch.start_char, ch.end_char), count), start=1):
            records.append({"id": f"{slug}/{ch.id}/p{n:04d}", "volume": slug, "shape": "chaptered", "chapter": ch.id,
                            "start_char": s, "end_char": e, "tokens": count(plain[s:e]), "source_hash": source_hash,
                            "parent_id": f"{slug}/{ch.id}"})
    for n, (s, e) in enumerate(pack(plain, paragraphs(plain, 0, len(plain)), count), start=1):
        records.append({"id": f"{slug}/plain/p{n:05d}", "volume": slug, "shape": "plain", "chapter": None,
                        "start_char": s, "end_char": e, "tokens": count(plain[s:e]), "source_hash": source_hash,
                        "parent_id": slug})
    over = [r["id"] for r in records if r["tokens"] > MAX_PASSAGE_TOKENS]
    if over:
        raise ValueError(f"{len(over)} passages over {MAX_PASSAGE_TOKENS} tokens, first {over[0]}")
    (vdir / "plain.txt").write_text(plain, encoding="utf-8", newline="\n")
    chaptered = "".join(f"\n=== {ch.id} | {ch.title} ===\n" + plain[ch.start_char : ch.end_char] for ch in chapters)
    (vdir / "chaptered.txt").write_text(chaptered.lstrip("\n"), encoding="utf-8", newline="\n")
    with open(vdir / "chapters.jsonl", "w", encoding="utf-8", newline="\n") as f:
        for ch in chapters:
            f.write(json.dumps({**asdict(ch), "volume": slug, "tokens": count(plain[ch.start_char:ch.end_char])}, ensure_ascii=False) + "\n")
    with open(vdir / "passages.jsonl", "w", encoding="utf-8", newline="\n") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    shapes = {s: [r for r in records if r["shape"] == s] for s in ("chaptered", "plain")}
    stats = {
        "slug": slug, "title": title, "author": author, "url": url, "source_hash": source_hash,
        "book_tokens": sum(r["tokens"] for r in shapes["plain"]),
        "chapters": len(chapters),
        "planted": len(needle_spans),
        **{f"{s}_passages": len(v) for s, v in shapes.items()},
        **{f"{s}_median_tokens": sorted(r["tokens"] for r in v)[len(v) // 2] for s, v in shapes.items()},
        "max_tokens": max(r["tokens"] for r in records),
    }
    (vdir / "README.md").write_text(
        f"# {title}\n\n{author}. Public domain, from Project Gutenberg: {url}\n\n"
        "`plain.txt` holds planted needles; `source.txt` is the untouched download.\n\n"
        "| Item | Value |\n|------|-------|\n"
        + "".join(f"| {k} | {v} |\n" for k, v in stats.items() if k not in ("title", "author", "url")),
        encoding="utf-8", newline="\n",
    )
    return stats


def load_passages(slug: str, shape: str, root: Path | None = None) -> list[dict]:
    """Passage records of one shape with their text attached from plain.txt."""
    vdir = (root or volumes_dir()) / slug
    plain = (vdir / "plain.txt").read_text(encoding="utf-8")
    out = []
    with open(vdir / "passages.jsonl", encoding="utf-8") as f:
        for line in f:
            r = json.loads(line)
            if r["shape"] == shape:
                r["text"] = plain[r["start_char"] : r["end_char"]]
                out.append(r)
    return out


def locate(slug: str, start: int, end: int, root: Path | None = None) -> dict[str, list[str]]:
    """Passage IDs, per shape, that overlap the span [start, end) of plain.txt."""
    vdir = (root or volumes_dir()) / slug
    out: dict[str, list[str]] = {"chaptered": [], "plain": []}
    with open(vdir / "passages.jsonl", encoding="utf-8") as f:
        for line in f:
            r = json.loads(line)
            if r["start_char"] < end and start < r["end_char"]:
                out[r["shape"]].append(r["id"])
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="python -m hces.passages")
    ap.add_argument("slug")
    ap.add_argument("--title", required=True)
    ap.add_argument("--author", required=True)
    ap.add_argument("--url", required=True)
    a = ap.parse_args(argv)
    print(json.dumps(build(a.slug, a.title, a.author, a.url), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
