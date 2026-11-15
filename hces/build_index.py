"""Build the vector and keyword index for one volume and shape.

  python -m hces.build_index <slug> [--shape chaptered|plain|both] [--rebuild]

Writes workspaces/hces-lab/kb/index/<slug>-<shape>.db and appends one line per build to
stages/03-pipeline-v0/output/index-builds.jsonl with index_build time and peak memory.
Index files are rebuildable; results never live in them.
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from hces import passages as P
from hces.retrieve import Index
from hces.timing import RunClock
from hces.units import Unit


def index_path(slug: str, shape: str, root: Path | None = None) -> Path:
    from hces.config import ROOT

    return (root or ROOT / "workspaces" / "hces-lab" / "kb" / "index") / f"{slug}-{shape}.db"


def log_path() -> Path:
    from hces.config import ROOT

    return ROOT / "workspaces" / "hces-lab" / "stages" / "03-pipeline-v0" / "output" / "index-builds.jsonl"


def units_for(slug: str, shape: str, volumes_root: Path | None = None) -> list[Unit]:
    return [Unit(id=r["id"], text=r["text"], parent_id=r["parent_id"], source=slug, tokens=r["tokens"])
            for r in P.load_passages(slug, shape, volumes_root)]


def build(slug: str, shape: str, embedder, rebuild: bool = False, index_root: Path | None = None,
          volumes_root: Path | None = None, log: Path | None = None) -> dict:
    path = index_path(slug, shape, index_root)
    if path.exists():
        if not rebuild:
            raise FileExistsError(f"{path} exists; pass --rebuild to replace it")
        path.unlink()
    units = units_for(slug, shape, volumes_root)
    with RunClock() as clock:
        with clock.span("index_build"):
            idx = Index(path, embedder.dim)
            idx.build(units, embedder)
            n = idx.count()
            idx.close()
    row = {"at": time.strftime("%Y-%m-%dT%H:%M:%S"), "volume": slug, "shape": shape, "passages": n,
           "tokens": sum(u.tokens for u in units), "embedder": embedder.model_id,
           "index_build_ms": round(clock.ms["index_build"], 1), "peak_rss_mb": clock.peak_rss_mb,
           "passages_per_s": round(n / (clock.ms["index_build"] / 1000), 1),
           "file_mb": round(path.stat().st_size / 2**20, 2)}
    log = log or log_path()
    log.parent.mkdir(parents=True, exist_ok=True)
    with open(log, "a", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(row) + "\n")
    return row


def main(argv=None) -> int:
    from hces.config import load
    from hces.embed import FastEmbedder

    ap = argparse.ArgumentParser(prog="python -m hces.build_index")
    ap.add_argument("slug")
    ap.add_argument("--shape", choices=["chaptered", "plain", "both"], default="both")
    ap.add_argument("--rebuild", action="store_true")
    a = ap.parse_args(argv)
    cfg = load()
    with RunClock() as load_clock:
        with load_clock.span("access"):
            embedder = FastEmbedder(cfg.embedder)
    print(json.dumps({"embedder_load_ms": round(load_clock.ms["access"], 1), "peak_rss_mb": load_clock.peak_rss_mb}))
    for shape in (["chaptered", "plain"] if a.shape == "both" else [a.shape]):
        print(json.dumps(build(a.slug, shape, embedder, a.rebuild)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
