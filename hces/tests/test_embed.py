import math

import pytest


@pytest.mark.slow
def test_fastembed_bge_small_gives_unit_vectors():
    from hces.config import load
    from hces.embed import FastEmbedder

    emb = FastEmbedder(load().embedder)
    a, b, c = emb.embed(["the keeper leaves the island", "the lighthouse keeper departs", "herring prices fell"])
    assert len(a) == 384
    assert math.isclose(sum(x * x for x in a), 1.0, rel_tol=1e-3)
    cos = lambda x, y: sum(p * q for p, q in zip(x, y))  # noqa: E731
    assert cos(a, b) > cos(a, c)
