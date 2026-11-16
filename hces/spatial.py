"""Spatial vector layer: passages placed by meaning, searched by neighbourhood.

The vector space is cut into cells (spherical k-means on the passage vectors). Every passage is
stored inside its cell, cells laid out back to back, as int8 codes with one scale per passage.
A query scores the cell centres, opens only the `nprobe` nearest cells, scans their codes, and
re-scores the best few hundred with the full float32 vectors read from a memory-mapped file.

Why cells by meaning, not by document: the Britannica summary-first run (voice stage 07) routed
by article summary and lost 8 of 40 questions, because a detail question lands in an article
whose summary does not mention it. Here a passage sits next to passages that say similar things,
wherever they came from, so routing never depends on a summary.

Files, for one corpus at <base>:
  <base>.spatial.npz   cell centres, offsets, int8 codes, scales, unit ids (in cell order)
  <base>.f32.npy       float32 vectors in cell order, memory-mapped for the re-score step

Rebuildable at any time from the vectors; results never live here (same rule as retrieve.Index).

  python -m hces.spatial build <vectors.npy> <ids.json> <base> [--cells N]
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Sequence

import numpy as np

DEFAULT_NPROBE = 32
RESCORE_MIN = 200


def _unit(x: np.ndarray) -> np.ndarray:
    n = np.linalg.norm(x, axis=-1, keepdims=True)
    if np.any(n == 0):
        raise ValueError("Zero vector: every passage and centre must have a direction")
    return (x / n).astype(np.float32)


def default_cells(n: int) -> int:
    """About 4 x sqrt(n), so a cell holds a few hundred passages at Britannica scale."""
    return max(1, min(n, int(4 * math.sqrt(n))))


def kmeans(vectors: np.ndarray, cells: int, iters: int = 12, sample: int = 100_000, seed: int = 0) -> np.ndarray:
    """Spherical k-means on a sample; returns unit-length centres. Empty cells are reseeded."""
    rng = np.random.default_rng(seed)
    n = len(vectors)
    train = vectors[rng.choice(n, size=min(n, sample), replace=False)]
    centres = train[rng.choice(len(train), size=cells, replace=False)].copy()
    for _ in range(iters):
        assign = np.argmax(train @ centres.T, axis=1)
        sums = np.zeros_like(centres)
        np.add.at(sums, assign, train)
        counts = np.bincount(assign, minlength=cells)
        empty = counts == 0
        sums[empty] = train[rng.choice(len(train), size=int(empty.sum()), replace=False)]
        centres = _unit(sums)
    return centres


def assign_cells(vectors: np.ndarray, centres: np.ndarray, batch: int = 65_536) -> np.ndarray:
    out = np.empty(len(vectors), dtype=np.int32)
    for i in range(0, len(vectors), batch):
        out[i : i + batch] = np.argmax(vectors[i : i + batch] @ centres.T, axis=1)
    return out


def quantize(vectors: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Symmetric int8 per vector: code = round(x / scale), scale = max|x| / 127."""
    scales = np.abs(vectors).max(axis=1) / 127.0
    codes = np.round(vectors / scales[:, None]).astype(np.int8)
    return codes, scales.astype(np.float32)


class SpatialIndex:
    def __init__(self, ids: list[str], centres: np.ndarray, offsets: np.ndarray, codes: np.ndarray,
                 scales: np.ndarray, full: np.ndarray):
        if not (len(ids) == len(codes) == len(scales) == len(full)):
            raise ValueError("ids, codes, scales and vectors must have one row per passage")
        if offsets[0] != 0 or offsets[-1] != len(ids) or len(offsets) != len(centres) + 1:
            raise ValueError("Cell offsets do not cover the passages")
        self.ids, self.centres, self.offsets = ids, centres, offsets
        self.codes, self.scales, self.full = codes, scales, full
        self.dim = centres.shape[1]

    @classmethod
    def build(cls, ids: Sequence[str], vectors: np.ndarray, cells: int | None = None, seed: int = 0) -> "SpatialIndex":
        if len(ids) != len(vectors):
            raise ValueError(f"{len(ids)} ids for {len(vectors)} vectors")
        v = _unit(np.asarray(vectors, dtype=np.float32))
        centres = kmeans(v, cells or default_cells(len(v)), seed=seed)
        cell = assign_cells(v, centres)
        order = np.argsort(cell, kind="stable")
        offsets = np.concatenate([[0], np.cumsum(np.bincount(cell, minlength=len(centres)))]).astype(np.int64)
        v = v[order]
        codes, scales = quantize(v)
        return cls([ids[i] for i in order], centres, offsets, codes, scales, v)

    def save(self, base: Path | str) -> None:
        base = Path(base)
        base.parent.mkdir(parents=True, exist_ok=True)
        np.savez(f"{base}.spatial.npz", centres=self.centres, offsets=self.offsets, codes=self.codes,
                 scales=self.scales, ids=np.array(json.dumps(self.ids)))
        np.save(f"{base}.f32.npy", np.asarray(self.full, dtype=np.float32))

    @classmethod
    def load(cls, base: Path | str) -> "SpatialIndex":
        z = np.load(f"{base}.spatial.npz")
        full = np.load(f"{base}.f32.npy", mmap_mode="r")
        return cls(json.loads(str(z["ids"])), z["centres"], z["offsets"], z["codes"], z["scales"], full)

    def __len__(self) -> int:
        return len(self.ids)

    def search(self, qvec: Sequence[float], k: int, nprobe: int = DEFAULT_NPROBE) -> list[tuple[str, float]]:
        """Top k (unit_id, cosine) from the nprobe nearest cells. nprobe >= cells is exact search."""
        q = _unit(np.asarray(qvec, dtype=np.float32)[None, :])[0]
        if q.shape[0] != self.dim:
            raise ValueError(f"Query has {q.shape[0]} dimensions, index has {self.dim}")
        nprobe = min(nprobe, len(self.centres))
        near = np.argpartition(-(self.centres @ q), nprobe - 1)[:nprobe]
        rows = np.concatenate([np.arange(self.offsets[c], self.offsets[c + 1]) for c in near])
        if len(rows) == 0:
            return []
        rough = (self.codes[rows].astype(np.float32) @ q) * self.scales[rows]
        keep = min(len(rows), max(RESCORE_MIN, 4 * k))
        short = rows[np.argpartition(-rough, keep - 1)[:keep]] if keep < len(rows) else rows
        short = np.sort(short)  # sequential reads from the memory-mapped file
        exact = np.asarray(self.full[short]) @ q
        top = np.argsort(-exact)[:k]
        return [(self.ids[short[i]], float(exact[i])) for i in top]

    def stats(self) -> dict:
        sizes = np.diff(self.offsets)
        return {"passages": len(self), "cells": len(self.centres), "cell_median": int(np.median(sizes)),
                "cell_max": int(sizes.max()), "codes_mb": round(self.codes.nbytes / 2**20, 1),
                "full_mb": round(len(self) * self.dim * 4 / 2**20, 1)}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="python -m hces.spatial")
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build")
    b.add_argument("vectors")
    b.add_argument("ids")
    b.add_argument("base")
    b.add_argument("--cells", type=int)
    a = ap.parse_args(argv)
    ids = json.loads(Path(a.ids).read_text(encoding="utf-8"))
    idx = SpatialIndex.build(ids, np.load(a.vectors, mmap_mode="r"), a.cells)
    idx.save(a.base)
    print(json.dumps(idx.stats()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
