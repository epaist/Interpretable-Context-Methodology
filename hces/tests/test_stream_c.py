import collections

import pytest

from hces import stream as T


@pytest.fixture(scope="module")
def world():
    path = T.out_dir() / "quillmere-company.md"
    if not path.exists():
        pytest.skip("company sheet not on this machine")
    sheet = path.read_text(encoding="utf-8")
    dl = T.docs(sheet)
    led = T.ledger(sheet) + T.doc_ledger(dl)
    pa = T.plan_a(T.ledger(sheet))
    pb = T.plan_b(led, dl)
    pc = T.plan_c(led, dl)
    return led, dl, pa + pb, pc, T.questions_c(led, pa + pb + pc, dl)


def test_plan_c_has_100_records_of_four_kinds(world):
    _, _, _, pc, _ = world
    assert len(pc) == 100 and len({p["id"] for p in pc}) == 100
    assert collections.Counter(p["kind"] for p in pc) == {"announcement": 15, "meeting notes": 21, "newsletter": 24, "chatter": 40}


def test_every_change_with_no_sop_is_announced_before_it_starts(world):
    led, dl, _, pc, _ = world
    owned = {k for d in dl for k in d["keys"]}
    for r in led:
        if r["kind"] == "changing" and r["key"] not in owned and r["valid_from"] != "2026-01-01":
            a = [p for p in pc if p["kind"] == "announcement" and p["key"] == r["key"] and p["effective"] == r["valid_from"]]
            assert len(a) == 1 and a[0]["date"] < r["valid_from"]


def test_calder_is_announced_early_then_moved(world):
    _, _, _, pc, _ = world
    cal = [(p["date"], p["style"], p["effective"]) for p in pc if p["key"] == "fiber_towns" and p["value"] == "Adds Calder"
           and p["kind"] == "announcement"]
    assert cal == [("2026-03-02", "early_announce", "2026-03-15"), ("2026-03-12", "delay", "2026-04-01")]


def test_floated_price_never_supports_an_answer(world):
    led, _, ab, pc, _ = world
    assert T.support(ab + pc, "spark_price", "$46") == []
    assert all(r["value"] != "$46" for r in led)


def test_announcements_support_from_their_start_date(world):
    _, _, ab, pc, _ = world
    assert "2026-04-20" in T.support(pc, "support_phone", "1-888-555-0177")
    assert all(d >= "2026-04-20" for d in T.support(pc, "support_phone", "1-888-555-0177"))


def test_questions_c_cover_every_kind_and_are_answerable(world):
    led, _, ab, pc, qs = world
    assert collections.Counter(q["kind"] for q in qs) == {"sop key": 27, "ticket key": 13, "announced, not yet": 10,
                                                          "early announcement": 1, "never valid": 1, "stable": 6}
    for q in qs:
        assert q["expected"] == T.value_at(led, q["key"], q["as_of"])["value"]
        assert any(d <= q["as_of"] for d in T.support(ab + pc, q["key"], q["expected"]))
    nv = next(q for q in qs if q["kind"] == "never valid")
    assert nv["expected"] == "$44" and "$46" in nv["other_values"]
    ea = next(q for q in qs if q["kind"] == "early announcement")
    assert "2026-03-15" <= ea["as_of"] < "2026-04-01" and ea["expected"] == "Alder, Brook"


def world_plan():
    sheet = (T.out_dir() / "quillmere-company.md").read_text(encoding="utf-8")
    dl = T.docs(sheet)
    return T.plan_c(T.ledger(sheet) + T.doc_ledger(dl), dl)


def test_phase_c_prompt_and_chatter_check(world):
    p = {"id": "qc-001", "date": "2026-02-01", "kind": "chatter", "key": None, "value": None, "style": "noise"}
    assert "no Quillmere fact" in T.write_prompt([p])
    got = T.check([p], [{"id": "qc-001", "text": "Lunch was great. The pizza cost $12.", "quote": "Who won the game?"}])
    assert got[0]["quote"] == "Lunch was great."
    a = {"id": "ann-001", "date": "2026-04-10", "kind": "announcement", "key": "support_phone", "value": "1-888-555-0177",
         "style": "announce", "effective": "2026-04-20"}
    assert "from April 20, 2026" in T.write_prompt([a])
    for p in world_plan():
        if p["key"]:
            assert p["id"] in T.write_prompt([p])


def test_phase_c_text_must_give_the_value():
    assert T.names_value("Adds Calder", "Fiber reaches Calder on April 1.")
    assert not T.names_value("Adds Calder", "The new phase starts April 1.")
    assert not T.names_value("$5/mo", "a discount of five dollars per month")
    assert T.names_value("$5/mo", "a discount of $5 per month") and T.names_value("Closed to new signups", "No new signups.")
    assert not T.names_value("$15 per 50 GB", "now $15 per GB")
    assert T.names_value("Script v1", "agents read script v1 first") and not T.names_value("Script v1", "script v11")
    p = {"id": "ann-004", "phase": "c", "key": "fiber_towns", "value": "Adds Calder", "style": "delay"}
    with pytest.raises(ValueError):
        T.check([p], [{"id": "ann-004", "text": "The new phase starts April 1.", "quote": "The new phase starts April 1."}])
