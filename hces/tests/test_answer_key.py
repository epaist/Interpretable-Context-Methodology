import json

import pytest

from hces import answer_key as A
from hces.tests.test_passages import BOOK, words


def setup(tmp_path, questions, needles):
    vols, out = tmp_path / "vols", tmp_path / "out"
    (vols / "test").mkdir(parents=True)
    out.mkdir()
    (vols / "test" / "source.txt").write_text(BOOK, encoding="utf-8")
    (out / "questions.jsonl").write_text("".join(json.dumps(q) + "\n" for q in questions), encoding="utf-8")
    (out / "needles.jsonl").write_text("".join(json.dumps(n) + "\n" for n in needles), encoding="utf-8")
    return vols, out


@pytest.fixture(autouse=True)
def one_volume(monkeypatch):
    monkeypatch.setattr(A, "VOLUMES", {"test": ("Test", "Nobody", 1, 1000)})
    monkeypatch.setattr(A, "SIZE_TOLERANCE", 10.0)


NEEDLE = {"id": "test/n01", "volume": "test", "role": "needle", "at": 0.5, "unique": "Zanzibar",
          "text": "The vault code was kept in a tin from Zanzibar on the top shelf of the pantry.",
          "question": "Where was the vault code kept?", "answer": "A tin from Zanzibar"}
DECOY = {"id": "test/d01", "volume": "test", "role": "decoy", "decoy_of": "test/n01", "at": 0.9,
         "text": "Nobody in the house ever spoke of the vault code, or of where it might be kept."}


def test_key_resolves_gold_needles_and_decoys(tmp_path):
    q = [{"id": "test/q01", "volume": "test", "question": "q", "answer": "a", "answerable": True,
          "evidence": ["w3x0 w3x1 w3x2"], "tags": []},
         {"id": "test/q02", "volume": "test", "question": "q", "answer": "not in the documents",
          "answerable": False, "absent": ["submarine"], "tags": []}]
    vols, out = setup(tmp_path, q, [NEEDLE, DECOY])
    assert A.build_all(out, vols, count=words)["rows"] == 3
    key = {r["id"]: r for r in map(json.loads, (out / "answer-key.jsonl").read_text().splitlines())}
    assert key["test/q01"]["gold"]["chaptered"] and key["test/q01"]["gold"]["plain"]
    assert key["test/n01"]["needle_id"] == "test/n01" and key["test/n01"]["decoy_ids"] == ["test/d01"]
    assert not set(key["test/n01"]["gold"]["plain"]) & set(key["test/n01"]["decoy_gold"]["plain"])
    assert "Failures | 0" in (out / "audit.md").read_text()


@pytest.mark.parametrize("change, message", [
    ({"evidence": ["not in this book at all"]}, "evidence not found"),
    ({"answerable": False, "absent": ["w3x0"]}, "unanswerable but"),
])
def test_bad_questions_stop_the_run(tmp_path, change, message):
    q = {"id": "test/q01", "volume": "test", "question": "q", "answer": "a", "answerable": True,
         "evidence": ["w3x0"], "tags": [], **change}
    vols, out = setup(tmp_path, [q], [])
    with pytest.raises(SystemExit, match=message):
        A.build_all(out, vols, count=words)
    assert not (out / "answer-key.jsonl").exists()


def test_needle_answer_elsewhere_fails(tmp_path):
    vols, out = setup(tmp_path, [], [{**NEEDLE, "unique": "w3x0"}])
    with pytest.raises(SystemExit, match="must be once"):
        A.build_all(out, vols, count=words)


def test_decoy_evidence_resolves_and_gold_wins_overlap(tmp_path):
    q = {"id": "test/q01", "volume": "test", "question": "q", "answer": "a", "answerable": True,
         "evidence": ["w3x0 w3x1"], "decoy_evidence": ["w6x0 w6x1"], "tags": []}
    vols, out = setup(tmp_path, [q], [])
    A.build_all(out, vols, count=words)
    row = json.loads((out / "answer-key.jsonl").read_text().splitlines()[0])
    assert row["decoy_gold"]["plain"] and not set(row["decoy_gold"]["plain"]) & set(row["gold"]["plain"])
    vols, out = setup(tmp_path / "b", [{**q, "decoy_evidence": ["w3x0"]}], [])
    with pytest.raises(SystemExit, match="every decoy passage is also gold"):
        A.build_all(out, vols, count=words)
