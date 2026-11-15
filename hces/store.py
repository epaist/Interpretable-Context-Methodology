"""Insert-only SQLite results store.

The database itself refuses UPDATE and DELETE on every results table, so a run can only
ever add rows. A rerun gets a new run_id.
"""

from __future__ import annotations

import json
import sqlite3
import time
import uuid
from pathlib import Path
from typing import Iterable

from hces.rubric import Rubric

TABLES = ("rubrics", "runs", "judgments", "decisions")

SCHEMA = """
CREATE TABLE IF NOT EXISTS rubrics (
  rubric_id TEXT NOT NULL, version INTEGER NOT NULL, hash TEXT NOT NULL,
  body TEXT NOT NULL, created_at REAL NOT NULL,
  PRIMARY KEY (rubric_id, version)
);
CREATE TABLE IF NOT EXISTS runs (
  run_id TEXT PRIMARY KEY, arm TEXT NOT NULL, variant TEXT, k INTEGER,
  question_id TEXT, budget INTEGER, judge_model TEXT,
  rubric_id TEXT, rubric_version INTEGER,
  access_ms REAL NOT NULL, analysis_ms REAL NOT NULL, response_ms REAL NOT NULL,
  peak_rss_mb REAL NOT NULL, tokens_in INTEGER NOT NULL, cost_usd REAL NOT NULL,
  started_at REAL NOT NULL, notes TEXT
);
CREATE TABLE IF NOT EXISTS judgments (
  run_id TEXT NOT NULL, unit_id TEXT NOT NULL, rubric_id TEXT NOT NULL,
  rubric_version INTEGER NOT NULL, question_key TEXT NOT NULL, qtype TEXT NOT NULL,
  value REAL, label TEXT, confidence REAL, model TEXT, tokens_in INTEGER,
  error TEXT, created_at REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS decisions (
  run_id TEXT NOT NULL, unit_id TEXT NOT NULL, kept INTEGER NOT NULL,
  final_score REAL, rank INTEGER, reason TEXT NOT NULL, created_at REAL NOT NULL
);
CREATE INDEX IF NOT EXISTS judgments_run ON judgments(run_id);
CREATE INDEX IF NOT EXISTS decisions_run ON decisions(run_id);
"""


def _guards() -> str:
    out = []
    for t in TABLES:
        for op in ("UPDATE", "DELETE"):
            out.append(
                f"CREATE TRIGGER IF NOT EXISTS {t}_no_{op.lower()} BEFORE {op} ON {t} "
                f"BEGIN SELECT RAISE(ABORT, 'insert-only: {op} on {t} is not allowed'); END;"
            )
    return "\n".join(out)


def new_run_id() -> str:
    return time.strftime("%Y%m%d-%H%M%S-") + uuid.uuid4().hex[:8]


class Store:
    def __init__(self, path: Path | str):
        self.path = Path(path) if str(path) != ":memory:" else path
        if isinstance(self.path, Path):
            self.path.parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(str(path), check_same_thread=False)
        self.db.row_factory = sqlite3.Row
        self.db.executescript(SCHEMA + _guards())

    def close(self) -> None:
        self.db.close()

    def add_rubric(self, rubric: Rubric) -> None:
        row = self.db.execute(
            "SELECT hash FROM rubrics WHERE rubric_id=? AND version=?", (rubric.rubric_id, rubric.version)
        ).fetchone()
        if row:
            if row["hash"] != rubric.hash:
                raise ValueError(
                    f"Rubric {rubric.rubric_id} v{rubric.version} already stored with different questions; bump the version"
                )
            return
        with self.db:
            self.db.execute(
                "INSERT INTO rubrics VALUES (?,?,?,?,?)",
                (rubric.rubric_id, rubric.version, rubric.hash, rubric.canonical(), time.time()),
            )

    def add_judgments(self, run_id: str, rubric: Rubric, judgments: Iterable) -> int:
        rows = [
            (run_id, j.unit_id, rubric.rubric_id, rubric.version, j.question_key, j.qtype, j.value, j.label,
             j.confidence, j.model, j.tokens_in, j.error, time.time())
            for j in judgments
        ]
        with self.db:
            self.db.executemany("INSERT INTO judgments VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)", rows)
        return len(rows)

    def add_decisions(self, run_id: str, decisions: Iterable[dict]) -> int:
        rows = [
            (run_id, d["unit_id"], int(bool(d["kept"])), d.get("final_score"), d.get("rank"), d["reason"], time.time())
            for d in decisions
        ]
        with self.db:
            self.db.executemany("INSERT INTO decisions VALUES (?,?,?,?,?,?,?)", rows)
        return len(rows)

    def add_run(self, run: dict) -> None:
        """Written once, when the run is finished, with all three timings and peak memory."""
        for need in ("run_id", "arm", "access_ms", "analysis_ms", "response_ms", "peak_rss_mb", "tokens_in", "cost_usd"):
            if run.get(need) is None:
                raise ValueError(f"Run row is missing '{need}'")
        cols = ("run_id", "arm", "variant", "k", "question_id", "budget", "judge_model", "rubric_id",
                "rubric_version", "access_ms", "analysis_ms", "response_ms", "peak_rss_mb", "tokens_in",
                "cost_usd", "started_at", "notes")
        values = [run.get(c) for c in cols]
        values[cols.index("started_at")] = run.get("started_at") or time.time()
        if isinstance(values[-1], (dict, list)):
            values[-1] = json.dumps(values[-1])
        with self.db:
            self.db.execute(f"INSERT INTO runs ({','.join(cols)}) VALUES ({','.join('?' * len(cols))})", values)

    def run(self, run_id: str) -> sqlite3.Row | None:
        return self.db.execute("SELECT * FROM runs WHERE run_id=?", (run_id,)).fetchone()

    def judgments(self, run_id: str) -> list[sqlite3.Row]:
        return self.db.execute("SELECT * FROM judgments WHERE run_id=? ORDER BY rowid", (run_id,)).fetchall()
