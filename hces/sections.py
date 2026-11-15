"""Instruction files cut into sections by heading: the second test set (stage 05 step 4).

  python -m hces.sections          writes stages/05-end-to-end/output/instructions/sections.jsonl

A section is one heading (levels 1 to 3) with its body, up to the next heading of level 3 or above.
Headings inside code fences do not count. Text before the first heading joins the first section.
A section over the passage cap is split at blank lines into parts. Each unit's text starts with its
file path and heading trail, so the judge knows where it sits.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

from hces.units import MAX_PASSAGE_TOKENS

SOURCES = ("CLAUDE.md", "_core", "workspaces/workspace-builder", "workspaces/hces-lab")
SKIP_PARTS = {"output", "kb", "__pycache__"}
HEADING = re.compile(r"^(#{1,3})\s+(.+?)\s*#*\s*$")


def root() -> Path:
    from hces.config import ROOT

    return ROOT


def output_dir() -> Path:
    return root() / "workspaces" / "hces-lab" / "stages" / "05-end-to-end" / "output" / "instructions"


def files(base: Path | None = None) -> list[Path]:
    base = base or root()
    out = []
    for s in SOURCES:
        p = base / s
        if p.is_file():
            out.append(p)
        else:
            out.extend(f for f in sorted(p.rglob("*.md")) if not SKIP_PARTS & set(f.relative_to(base).parts))
    if not out:
        raise FileNotFoundError(f"No instruction files under {base}")
    return out


def split_sections(text: str) -> list[tuple[list[str], str]]:
    """[(heading trail, body including its heading line)] in file order."""
    trail: list[str] = []
    out: list[tuple[list[str], list[str]]] = []
    fence = False
    for line in text.splitlines():
        if line.lstrip().startswith("```"):
            fence = not fence
        m = None if fence else HEADING.match(line)
        if m:
            level = len(m.group(1))
            trail = trail[: level - 1] + [""] * max(0, level - 1 - len(trail)) + [m.group(2)]
            out.append(([t for t in trail if t], [line]))
        elif out:
            out[-1][1].append(line)
        else:
            out.append(([], [line]))
    if len(out) > 1 and not out[0][0]:  # preamble joins the first headed section
        out[1] = (out[1][0], out[0][1] + out[1][1])
        out = out[1:]
    return [(t, "\n".join(b).strip()) for t, b in out if "\n".join(b).strip()]


def parts(body: str, header: str, count, cap: int = MAX_PASSAGE_TOKENS - 10) -> list[str]:
    """Split at blank lines, then at line breaks for a block still over the cap; greedy packing."""
    if count(header + body) <= cap:
        return [body]
    pieces = []
    for para in body.split("\n\n"):
        if count(header + para) <= cap:
            pieces.append(para)
            continue
        for line in para.split("\n"):
            if count(header + line) > cap:
                raise ValueError(f"One line over {cap} tokens under {header.strip()}; cut the file or raise the cap")
            pieces.append(line)
    chunks, cur = [], ""
    for piece in pieces:
        sep = "\n\n" if piece in body.split("\n\n") else "\n"
        joined = f"{cur}{sep}{piece}" if cur else piece
        if count(header + joined) <= cap:
            cur = joined
        else:
            chunks.append(cur)
            cur = piece
    return chunks + [cur]


def build(count, base: Path | None = None, paths: list[Path] | None = None) -> list[dict]:
    """Units for every instruction file, or for the given files only (paths relative to base in the ids)."""
    base = base or root()
    units = []
    for f in paths if paths is not None else files(base):
        rel = f.relative_to(base).as_posix()
        for n, (trail, body) in enumerate(split_sections(f.read_text(encoding="utf-8")), start=1):
            header = f"File: {rel}\nSection: {' > '.join(trail) or '(top)'}\n\n"
            ps = parts(body, header, count)
            for i, p in enumerate(ps, start=1):
                uid = f"{rel}#s{n:02d}" + (f"-{i}" if len(ps) > 1 else "")
                text = header + p
                units.append({"id": uid, "file": rel, "trail": trail, "text": text, "tokens": count(text)})
    return units


def load(path: Path | None = None) -> list[dict]:
    path = path or output_dir() / "sections.jsonl"
    return [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]


def main(argv=None) -> int:
    from hces.passages import TokenCounter

    units = build(TokenCounter())
    out = output_dir()
    out.mkdir(parents=True, exist_ok=True)
    body = "".join(json.dumps(u, ensure_ascii=False) + "\n" for u in units)
    (out / "sections.jsonl").write_text(body, encoding="utf-8", newline="\n")
    print(json.dumps({"files": len({u['file'] for u in units}), "sections": len(units),
                      "tokens": sum(u["tokens"] for u in units), "max_tokens": max(u["tokens"] for u in units),
                      "hash": hashlib.sha256(body.encode()).hexdigest()[:12]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
