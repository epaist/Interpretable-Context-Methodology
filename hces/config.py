"""Reads the constants table in workspaces/hces-lab/shared/constants.md.

That file is the only home of these values. Nothing here has a default: a missing or
unfilled value stops the program with a message naming the row to fix.
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONSTANTS = ROOT / "workspaces" / "hces-lab" / "shared" / "constants.md"


class ConfigError(RuntimeError):
    pass


@dataclass(frozen=True)
class Config:
    jev_model: str
    vector_store: str
    embedder: str
    token_budget: int
    top_k_sweep: tuple[int, ...]
    python: str
    judge_workers: int
    results_store: Path
    state_cap_question: int
    state_cap_request: int
    price_per_million: float
    source: Path


def read_table(path: Path) -> dict[str, str]:
    """Return {Name: Value} from the first markdown table whose header is Name | Value | Why."""
    rows: dict[str, str] = {}
    in_table = False
    for line in path.read_text(encoding="utf-8").splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")] if line.strip().startswith("|") else None
        if cells is None:
            if in_table:
                break
            continue
        if not in_table:
            in_table = cells[:2] == ["Name", "Value"]
            continue
        if set(cells[0]) <= {"-", ":"}:
            continue
        rows[cells[0]] = cells[1].strip("`").strip()
    if not rows:
        raise ConfigError(f"No 'Name | Value | Why' table found in {path}")
    return rows


def _need(rows: dict[str, str], name: str, path: Path) -> str:
    value = rows.get(name)
    if not value:
        raise ConfigError(f"Row '{name}' is missing or empty in {path}")
    if "{{" in value:
        raise ConfigError(f"Row '{name}' is still a placeholder ({value}) in {path}; run setup first")
    return value


def _int(text: str, name: str) -> int:
    match = re.search(r"\d[\d,]*", text)
    if not match:
        raise ConfigError(f"Row '{name}' needs a number, got '{text}'")
    return int(match.group().replace(",", ""))


def _thousands(text: str, name: str) -> list[int]:
    found = [int(n) * 1000 for n in re.findall(r"(\d+)k", text)]
    if len(found) != 2:
        raise ConfigError(f"Row '{name}' needs two 'Nk' values (per question, per request), got '{text}'")
    return found


def load(path: Path | None = None) -> Config:
    path = Path(path or os.environ.get("HCES_CONSTANTS") or DEFAULT_CONSTANTS)
    if not path.is_file():
        raise ConfigError(f"Constants file not found: {path}")
    rows = read_table(path)
    embedder = _need(rows, "Embedder", path).split()[0]
    if "/" not in embedder:
        embedder = f"BAAI/{embedder}"
    sweep = tuple(int(n) for n in re.findall(r"\d+", _need(rows, "Candidate sweep", path)))
    if not sweep:
        raise ConfigError(f"Row 'Candidate sweep' has no numbers in {path}")
    per_q, per_req = _thousands(_need(rows, "JEV state cap", path), "JEV state cap")
    price = re.search(r"\d+(\.\d+)?", _need(rows, "JEV price", path))
    store = Path(_need(rows, "Results store", path))
    return Config(
        jev_model=_need(rows, "JEV model", path),
        vector_store=_need(rows, "Vector store", path),
        embedder=embedder,
        token_budget=_int(_need(rows, "Token budget", path), "Token budget"),
        top_k_sweep=sweep,
        python=_need(rows, "Python", path),
        judge_workers=_int(_need(rows, "Judge workers", path), "Judge workers"),
        results_store=store if store.is_absolute() else ROOT / store,
        state_cap_question=per_q,
        state_cap_request=per_req,
        price_per_million=float(price.group()) if price else 0.0,
        source=path,
    )
