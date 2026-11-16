import json

import pytest

from hces import passages as P
from hces import planter
from hces.units import MAX_PASSAGE_TOKENS


def words(text: str) -> int:  # stand-in tokenizer: one token per word plus [CLS] and [SEP]
    return len(text.split()) + 2


def para(n: int, k: int = 60) -> str:
    return " ".join(f"w{n}x{i}" for i in range(k)) + "."


BOOK = "\n".join([
    "Header junk", "*** START OF THE PROJECT GUTENBERG EBOOK TEST ***", "",
    "CONTENTS", "", " PROLOGUE", " FIRST PERIOD", " CHAPTER I", " CHAPTER II", " SECOND PERIOD", " CHAPTER I", "",
    "PROLOGUE", "", " A Subtitle", "", "I", "", para(1), "", para(2), "",
    "FIRST PERIOD", "", "CHAPTER I", "", para(3), "", para(4), "",
    "CHAPTER II", "", para(5), "", " ".join(f"long{i}." for i in range(1500)), "",
    "SECOND PERIOD.", "", "FIRST NARRATIVE.", "", "CHAPTER I", "", para(6), "", para(7), "",
    "*** END OF THE PROJECT GUTENBERG EBOOK TEST ***", "licence junk",
])


@pytest.fixture
def vol(tmp_path):
    (tmp_path / "test").mkdir()
    (tmp_path / "test" / "source.txt").write_text(BOOK, encoding="utf-8")
    return tmp_path


def records(root):
    return [json.loads(l) for l in (root / "test" / "passages.jsonl").read_text(encoding="utf-8").splitlines()]


def test_missing_markers_fail():
    with pytest.raises(ValueError, match="markers"):
        P.strip_gutenberg("no markers here")


def test_contents_dropped_and_groups_prefix_titles(vol):
    P.build("test", "T", "A", "U", count=words, root=vol, needles=[])
    plain = (vol / "test" / "plain.txt").read_text(encoding="utf-8")
    chapters = [json.loads(l) for l in (vol / "test" / "chapters.jsonl").read_text().splitlines()]
    assert plain.startswith("PROLOGUE") and "CONTENTS" not in plain and "junk" not in plain
    assert [c["title"] for c in chapters] == [
        "PROLOGUE / I", "FIRST PERIOD / CHAPTER I", "FIRST PERIOD / CHAPTER II",
        "SECOND PERIOD / FIRST NARRATIVE / CHAPTER I",
    ]
    assert chapters[-1]["end_char"] == len(plain)


def test_every_character_covered_and_under_cap(vol):
    P.build("test", "T", "A", "U", count=words, root=vol, needles=[])
    plain = (vol / "test" / "plain.txt").read_text(encoding="utf-8")
    recs = records(vol)
    assert len({r["id"] for r in recs}) == len(recs)
    for shape in ("chaptered", "plain"):
        covered = set()
        for r in (r for r in recs if r["shape"] == shape):
            assert r["tokens"] <= MAX_PASSAGE_TOKENS
            covered.update(range(r["start_char"], r["end_char"]))
        assert all(i in covered for i, ch in enumerate(plain) if not ch.isspace())


def test_long_paragraph_split_at_sentences(vol):
    P.build("test", "T", "A", "U", count=words, root=vol, needles=[])
    plain = (vol / "test" / "plain.txt").read_text(encoding="utf-8")
    long_parts = [r for r in records(vol) if r["shape"] == "chaptered" and "long" in plain[r["start_char"]:r["end_char"]]]
    assert len(long_parts) >= 3
    assert all(plain[r["end_char"] - 1] == "." for r in long_parts)


def test_ids_stable_across_builds(vol):
    P.build("test", "T", "A", "U", count=words, root=vol, needles=[])
    first = records(vol)
    P.build("test", "T", "A", "U", count=words, root=vol, needles=[])
    assert records(vol) == first


def test_needles_planted_between_paragraphs(vol):
    needles = [{"id": f"test/n{i}", "volume": "test", "at": at, "text": f"Needle {i} says the vault code is {i}{i}{i}{i} and nothing else matters here."}
               for i, at in enumerate([0.0, 0.5, 1.0])]
    stats = P.build("test", "T", "A", "U", count=words, root=vol, needles=needles)
    plain = (vol / "test" / "plain.txt").read_text(encoding="utf-8")
    assert stats["planted"] == 3
    for i in range(3):
        k = plain.index(f"Needle {i}")
        assert plain[k - 2 : k] == "\n\n" and plain.count(f"Needle {i} ") == 1
        hits = P.locate("test", k, k + 10, vol)
        assert len(hits["chaptered"]) == 1 and len(hits["plain"]) == 1
    chapters = [json.loads(l) for l in (vol / "test" / "chapters.jsonl").read_text().splitlines()]
    assert [plain[c["start_char"]:].split("\n")[0] for c in chapters] == ["PROLOGUE", "FIRST PERIOD", "CHAPTER II", "SECOND PERIOD."]


def test_planter_refuses_bad_input(vol):
    body = P.strip_gutenberg(BOOK)
    plain, chapters = P.find_chapters(body)
    with pytest.raises(ValueError, match="duplicate"):
        planter.plant(plain, chapters, [{"id": "a", "at": 0.1, "text": "x"}, {"id": "a", "at": 0.2, "text": "y"}])
    with pytest.raises(ValueError, match="0..1"):
        planter.plant(plain, chapters, [{"id": "a", "at": 1.5, "text": "x"}])


def test_load_passages_attaches_text(vol):
    P.build("test", "T", "A", "U", count=words, root=vol, needles=[])
    got = P.load_passages("test", "plain", vol)
    assert got and all(r["text"].strip() and "text" not in json.dumps(records(vol)[0]) for r in got[:1])
