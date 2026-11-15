"""Per-volume index (sqlite-vec vectors plus an FTS5 keyword table) and search.

One file per volume. Index files can be rebuilt at any time; results never live here.
sqlite-vec is the store; vector search scans an in-RAM numpy copy of it, loaded on the first
search (same results, about 27x faster than the sqlite-vec scan at 210k passages).
"""

from __future__ import annotations

import re
import sqlite3
import struct
from pathlib import Path
from typing import Sequence

import numpy as np
import sqlite_vec

from hces.embed import Embedder
from hces.units import MAX_PASSAGE_TOKENS, Unit

RRF_K = 60


def _blob(vec: Sequence[float]) -> bytes:
    return struct.pack(f"{len(vec)}f", *vec)


def fts_query(text: str) -> str:
    """Turn free text into a safe FTS5 query: quoted words joined by OR."""
    words = re.findall(r"[A-Za-z0-9']+", text.lower())
    if not words:
        raise ValueError("Keyword query has no searchable words")
    return " OR ".join(f'"{w}"' for w in dict.fromkeys(words))


class Index:
    def __init__(self, path: Path | str, dim: int):
        self.dim = dim
        self._matrix: np.ndarray | None = None
        self._ids: list[str] = []
        if str(path) != ":memory:":
            Path(path).parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(str(path))
        self.db.enable_load_extension(True)
        sqlite_vec.load(self.db)
        self.db.enable_load_extension(False)
        self.db.executescript(
            f"""
            CREATE TABLE IF NOT EXISTS units (rid INTEGER PRIMARY KEY, unit_id TEXT UNIQUE NOT NULL, text TEXT NOT NULL);
            CREATE VIRTUAL TABLE IF NOT EXISTS vec USING vec0(embedding float[{dim}] distance_metric=cosine);
            CREATE VIRTUAL TABLE IF NOT EXISTS fts USING fts5(text, content='units', content_rowid='rid', tokenize='porter unicode61');
            """
        )

    def close(self) -> None:
        self.db.close()

    def count(self) -> int:
        return self.db.execute("SELECT count(*) FROM units").fetchone()[0]

    def build(self, units: Sequence[Unit], embedder: Embedder, batch: int = 64) -> None:
        if embedder.dim != self.dim:
            raise ValueError(f"Embedder dim {embedder.dim} does not match index dim {self.dim}")
        for u in units:
            if u.token_count > MAX_PASSAGE_TOKENS:
                raise ValueError(f"Unit {u.id} has {u.token_count} tokens; passages are capped at {MAX_PASSAGE_TOKENS}")
        with self.db:
            for i in range(0, len(units), batch):
                chunk = units[i : i + batch]
                vectors = embedder.embed([u.text for u in chunk])
                for u, v in zip(chunk, vectors):
                    cur = self.db.execute("INSERT INTO units (unit_id, text) VALUES (?, ?)", (u.id, u.text))
                    rid = cur.lastrowid
                    self.db.execute("INSERT INTO vec (rowid, embedding) VALUES (?, ?)", (rid, _blob(v)))
                    self.db.execute("INSERT INTO fts (rowid, text) VALUES (?, ?)", (rid, u.text))
        self._matrix = None

    def _load_matrix(self) -> None:
        rows = self.db.execute(
            "SELECT u.unit_id, v.embedding FROM vec v JOIN units u ON u.rid = v.rowid ORDER BY u.rid"
        ).fetchall()
        if not rows:
            raise ValueError("Index is empty; build it before searching")
        m = np.frombuffer(b"".join(r[1] for r in rows), dtype=np.float32).reshape(len(rows), self.dim)
        norms = np.linalg.norm(m, axis=1, keepdims=True)
        if np.any(norms == 0):
            raise ValueError("Index holds a zero vector; cosine search is undefined for it")
        self._matrix = (m / norms).astype(np.float32)
        self._ids = [r[0] for r in rows]

    def vector_search(self, qvec: Sequence[float], k: int) -> list[tuple[str, float]]:
        """Top k (unit_id, cosine distance), nearest first; ties go to the earlier unit."""
        if self._matrix is None:
            self._load_matrix()
        q = np.asarray(qvec, dtype=np.float32)
        if q.shape != (self.dim,):
            raise ValueError(f"Query has shape {q.shape}, index dim is {self.dim}")
        qn = np.linalg.norm(q)
        if qn == 0:
            raise ValueError("Query vector is zero")
        dist = 1.0 - self._matrix @ (q / qn)
        k = min(k, len(dist))
        top = np.argpartition(dist, k - 1)[:k] if k < len(dist) else np.arange(len(dist))
        top = top[np.lexsort((top, dist[top]))]
        return [(self._ids[i], float(dist[i])) for i in top]

    def keyword_search(self, query: str, k: int) -> list[tuple[str, float]]:
        rows = self.db.execute(
            "SELECT u.unit_id, bm25(fts) AS s FROM fts JOIN units u ON u.rid = fts.rowid "
            "WHERE fts MATCH ? ORDER BY s LIMIT ?",
            (fts_query(query), k),
        ).fetchall()
        return [(r[0], float(r[1])) for r in rows]

    def hybrid_search(self, query: str, embedder: Embedder, k: int) -> list[tuple[str, float]]:
        """Reciprocal rank fusion of vector and keyword results; returns (unit_id, fused score)."""
        vec = self.vector_search(embedder.embed([query])[0], k)
        kw = self.keyword_search(query, k)
        return rrf([[u for u, _ in vec], [u for u, _ in kw]])[:k]


def rrf(rankings: Sequence[Sequence[str]], k: int = RRF_K) -> list[tuple[str, float]]:
    """Fuse ranked lists. Ties go to the unit ranked higher in the first list (the vector search)."""
    scores: dict[str, float] = {}
    first = {u: r for r, u in enumerate(rankings[0], start=1)} if rankings else {}
    for ranking in rankings:
        for rank, unit_id in enumerate(ranking, start=1):
            scores[unit_id] = scores.get(unit_id, 0.0) + 1.0 / (k + rank)
    return sorted(scores.items(), key=lambda kv: (-kv[1], first.get(kv[0], len(first) + 1), kv[0]))
