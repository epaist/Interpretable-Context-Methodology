"""Embed the benchmark questions with the HCES embedder (fastembed, config.embedder). Writes query_vectors.npy + query_ids.json next to this file."""
import json
import sys
from pathlib import Path

import numpy as np

here = Path(__file__).resolve().parent
sys.path.insert(0, str(here.parents[2]))
from hces.config import load
from hces.embed import FastEmbedder

qs = json.loads((here / "queries.json").read_text(encoding="utf-8"))
emb = FastEmbedder(load().embedder)
vecs = np.array(emb.embed([q["text"] for q in qs]), dtype=np.float32)
np.save(here / "query_vectors.npy", vecs)
(here / "query_ids.json").write_text(json.dumps([q["id"] for q in qs]), encoding="utf-8")
print(emb.model_id, vecs.shape)
