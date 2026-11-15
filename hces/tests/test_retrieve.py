import hashlib
import math

import pytest

from hces.retrieve import Index, fts_query, rrf
from hces.units import Unit


class HashEmbedder:
    """Deterministic bag-of-words vectors, so tests run without the real model."""

    model_id = "test-hash"
    dim = 384

    def embed(self, texts):
        out = []
        for t in texts:
            v = [0.0] * self.dim
            for w in t.lower().split():
                v[int(hashlib.md5(w.encode()).hexdigest(), 16) % self.dim] += 1.0
            n = math.sqrt(sum(x * x for x in v)) or 1.0
            out.append([x / n for x in v])
        return out


UNITS = [
    Unit("p1", "the keeper climbs the lighthouse stairs at dusk"),
    Unit("p2", "fishing boats return to the harbor with herring"),
    Unit("p3", "a letter tells the keeper his mother is ill so he leaves the island"),
]


@pytest.fixture
def index(tmp_path):
    idx = Index(tmp_path / "toy.db", dim=384)
    idx.build(UNITS, HashEmbedder())
    return idx


def test_build_counts(index):
    assert index.count() == 3


def test_vector_and_keyword_find_the_right_passage(index):
    emb = HashEmbedder()
    assert index.vector_search(emb.embed(["why the keeper leaves the island"])[0], 1)[0][0] == "p3"
    assert index.keyword_search("herring harbor", 1)[0][0] == "p2"


def test_hybrid_merges_both(index):
    ranked = index.hybrid_search("keeper leaves island", HashEmbedder(), 3)
    assert ranked[0][0] == "p3"
    assert len(ranked) == 3


def test_rrf_rewards_agreement():
    ranked = rrf([["a", "b", "c"], ["b", "a"]])
    fused = dict(ranked)
    assert fused["a"] == pytest.approx(fused["b"])
    assert fused["a"] > fused["c"]
    assert [u for u, _ in ranked] == ["a", "b", "c"]  # tie goes to the vector list's order


def test_keyword_search_stems(index):
    assert index.keyword_search("climbing", 1)[0][0] == "p1"


def test_fts_query_is_safe():
    assert fts_query('the "keeper" AND (leaves)') == '"the" OR "keeper" OR "and" OR "leaves"'
    with pytest.raises(ValueError):
        fts_query("!!!")


def test_long_passage_refused(tmp_path):
    idx = Index(tmp_path / "x.db", dim=384)
    with pytest.raises(ValueError, match="capped"):
        idx.build([Unit("long", "word " * 1000)], HashEmbedder())


def test_dim_mismatch_refused(tmp_path):
    idx = Index(tmp_path / "x.db", dim=128)
    with pytest.raises(ValueError, match="dim"):
        idx.build(UNITS, HashEmbedder())


def test_numpy_scan_matches_sqlite_vec(index):
    emb = HashEmbedder()
    q = emb.embed(["keeper island harbor"])[0]
    from hces.retrieve import _blob

    native = index.db.execute(
        "SELECT u.unit_id, v.distance FROM vec v JOIN units u ON u.rid = v.rowid "
        "WHERE v.embedding MATCH ? AND k = 3 ORDER BY v.distance", (_blob(q),)).fetchall()
    ours = index.vector_search(q, 3)
    assert [u for u, _ in ours] == [r[0] for r in native]
    assert [d for _, d in ours] == pytest.approx([r[1] for r in native], abs=1e-5)


def test_rebuild_refreshes_the_matrix(index):
    emb = HashEmbedder()
    index.vector_search(emb.embed(["keeper"])[0], 1)
    index.build([Unit("p4", "a whale surfaces beside the herring fleet")], emb)
    assert index.vector_search(emb.embed(["whale surfaces"])[0], 1)[0][0] == "p4"
