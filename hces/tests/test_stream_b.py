import collections

import pytest

from hces import stream as T


@pytest.fixture(scope="module")
def world():
    path = T.out_dir() / "quillmere-company.md"
    if not path.exists():
        pytest.skip("company sheet not on this machine")
    sheet = path.read_text(encoding="utf-8")
    led, dl = T.ledger(sheet), T.docs(sheet)
    led = led + T.doc_ledger(dl)
    pa = T.plan_a(T.ledger(sheet))
    pb = T.plan_b(led, dl)
    return led, dl, pa, pb, T.questions_b(led, pa + pb, dl)


def test_docs_own_27_keys_in_33_versions(world):
    led, dl, _, pb, _ = world
    assert sum(len(d["versions"]) for d in dl) == 33 and len({k for d in dl for k in d["keys"]}) == 27
    assert sum(p["style"] == "official" for p in pb) == 33 and set(T.LABEL) == {k for d in dl for k in d["keys"]}


def test_each_version_states_the_values_in_force(world):
    led, _, _, pb, _ = world
    sop = next(p for p in pb if p["id"] == "sop-02-v6")
    assert sop["date"] == "2026-10-15" and sop["facts"]["refund_window"] == "21 days" and sop["facts"]["sop_02_version"] == "v6"
    text, quotes = T.sop_text(sop)
    assert all(q in text for q in quotes.values()) and set(quotes) == set(sop["facts"])


def test_stale_citations_quote_an_older_differing_version(world):
    led, _, _, pb, _ = world
    stale = [p for p in pb if p["style"] == "stale_cite"]
    assert len(stale) == 5
    for p in stale:
        assert p["value"] != T.value_at(led, p["key"], p["date"])["value"]
    c = next(p for p in stale if p["key"] == "refund_window")
    assert (c["date"], c["cites"], c["value"]) == ("2026-10-20", "SOP-02 v5", "30 days")


def test_questions_cover_every_kind_and_are_answerable(world):
    led, _, pa, pb, qs = world
    kinds = collections.Counter(q["kind"] for q in qs)
    assert kinds == {"sop key": 27, "ticket key": 13, "doc version": 7, "stale citation": 5, "stable": 6}
    for q in qs:
        assert any(d <= q["as_of"] for d in T.support(pa + pb, q["key"], q["expected"]))


def test_check_needs_the_cited_document():
    p = {"id": "qb-001", "cites": "SOP-02 v6"}
    with pytest.raises(ValueError):
        T.check([p], [{"id": "qb-001", "text": "Refunds are 21 days.", "quote": "Refunds are 21 days."}])
    assert T.check([p], [{"id": "qb-001", "text": "Per SOP-02, refunds are 21 days.", "quote": "refunds are 21 days."}])


def test_check_takes_the_sentence_a_misquote_points_to():
    text = "Per SOP-04 version 1, the limit is set. We do not throttle. The figure is 1.2 TB per cycle."
    got = T.check([{"id": "qb-005", "cites": "SOP-04 v1"}],
                  [{"id": "qb-005", "text": text, "quote": "Per SOP-04 version 1, the limit is set. The figure is 1.2 TB per cycle."}])
    assert got[0]["quote"] == "The figure is 1.2 TB per cycle."
    with pytest.raises(ValueError):
        T.check([{"id": "x"}], [{"id": "x", "text": "Hello there. Goodbye now.", "quote": "The cap is 1.2 TB."}])


def test_check_prefers_the_sentence_that_states_the_value():
    text = "The agent said we use Script v1 for all calls. She said the rule comes from GOV-02 v1."
    got = T.check([{"id": "q", "cites": "GOV-02 v1", "value": "Script v1"}],
                  [{"id": "q", "text": text, "quote": "She stated that the rule comes from GOV-02 v1."}])
    assert got[0]["quote"] == "The agent said we use Script v1 for all calls."
