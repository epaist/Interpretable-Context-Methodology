"""Time retrieve.Index.vector_search (numpy scan) against the native sqlite-vec MATCH on the PC's Britannica index."""
import json, statistics, time
from pathlib import Path
import numpy as np
from hces.retrieve import Index, _blob

here = Path(__file__).resolve().parent
root = here.parents[3]
ids = json.loads((here / "query_ids.json").read_text())
Q = np.load(here / "query_vectors.npy")
qs = [q for i, q in zip(ids, Q) if i.startswith("eb1911/")]
idx = Index(root / "workspaces/voice-chat/stage07/index/eb1911.db", 384)
t = time.perf_counter(); idx._load_matrix(); load = time.perf_counter() - t
nat, new, same = [], [], 0
for q in qs:
    t = time.perf_counter()
    a = [r[0] for r in idx.db.execute("SELECT u.unit_id FROM vec v JOIN units u ON u.rid=v.rowid WHERE v.embedding MATCH ? AND k=150 ORDER BY v.distance", (_blob(q),))]
    nat.append((time.perf_counter() - t) * 1000)
    t = time.perf_counter(); b = [u for u, _ in idx.vector_search(q, 150)]; new.append((time.perf_counter() - t) * 1000)
    same += set(a) == set(b)
print(json.dumps({"queries": len(qs), "matrix_load_s": round(load, 1), "sqlite_vec_ms": round(statistics.median(nat), 1),
                  "numpy_ms": round(statistics.median(new), 1), "same_top150_set": same}))
