import json

import pytest

from hces import build_index as B
from hces import passages as P
from hces.retrieve import Index
from hces.tests.test_passages import BOOK, words
from hces.tests.test_retrieve import HashEmbedder


@pytest.fixture
def setup(tmp_path):
    vols = tmp_path / "vols"
    (vols / "test").mkdir(parents=True)
    (vols / "test" / "source.txt").write_text(BOOK, encoding="utf-8")
    P.build("test", "T", "A", "U", count=words, root=vols, needles=[])
    return vols, tmp_path / "index", tmp_path / "log.jsonl"


def test_build_indexes_every_passage_and_logs(setup):
    vols, idx_root, log = setup
    row = B.build("test", "plain", HashEmbedder(), index_root=idx_root, volumes_root=vols, log=log)
    n = len(P.load_passages("test", "plain", vols))
    assert row["passages"] == n and row["index_build_ms"] > 0 and row["peak_rss_mb"] > 0
    assert json.loads(log.read_text().splitlines()[0])["shape"] == "plain"
    idx = Index(B.index_path("test", "plain", idx_root), HashEmbedder().dim)
    assert idx.count() == n
    idx.close()


def test_refuses_to_overwrite_without_rebuild(setup):
    vols, idx_root, log = setup
    B.build("test", "chaptered", HashEmbedder(), index_root=idx_root, volumes_root=vols, log=log)
    with pytest.raises(FileExistsError):
        B.build("test", "chaptered", HashEmbedder(), index_root=idx_root, volumes_root=vols, log=log)
    B.build("test", "chaptered", HashEmbedder(), rebuild=True, index_root=idx_root, volumes_root=vols, log=log)
    assert len(log.read_text().splitlines()) == 2
