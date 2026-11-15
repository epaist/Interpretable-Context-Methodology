import numpy as np
import pytest

from hces.spatial import SpatialIndex


def _data(n=600, dim=16, seed=1):
    rng = np.random.default_rng(seed)
    v = rng.normal(size=(n, dim)).astype(np.float32)
    return [f"u{i}" for i in range(n)], v / np.linalg.norm(v, axis=1, keepdims=True)


def test_full_probe_matches_exact_search(tmp_path):
    ids, v = _data()
    idx = SpatialIndex.build(ids, v, cells=20)
    idx.save(tmp_path / "x")
    idx = SpatialIndex.load(tmp_path / "x")
    q = v[7] + 0.1 * v[8]
    exact = [ids[i] for i in np.argsort(-(v @ (q / np.linalg.norm(q))))[:10]]
    assert [u for u, _ in idx.search(q, 10, nprobe=20)] == exact


def test_every_passage_lands_in_one_cell():
    ids, v = _data()
    idx = SpatialIndex.build(ids, v, cells=20)
    assert sorted(idx.ids) == sorted(ids)
    assert idx.offsets[-1] == len(ids)


def test_wrong_query_dimension_fails():
    ids, v = _data()
    idx = SpatialIndex.build(ids, v, cells=5)
    with pytest.raises(ValueError):
        idx.search(np.ones(8), 3)
