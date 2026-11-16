import sqlite3

import pytest

from hces import memory as M


def f(fid, value, dated, record_date=None, vclass=None):
    return {"fact_id": fid, "value": value, "dated": dated, "record_date": record_date or dated, "vclass": vclass}


def test_current_takes_latest_dated_value():
    facts = [f("a", "$39/mo", "2026-01-10"), f("b", "$42", "2026-03-05")]
    assert M.current(facts, "2026-02-01")["fact_id"] == "a"
    assert M.current(facts, "2026-03-10")["fact_id"] == "b"
    assert M.current(facts, "2026-01-01") is None


def test_effective_date_counts_only_once_record_is_seen():
    facts = [f("a", "14 days", "2026-01-10"), f("b", "30 days", "2026-04-01", record_date="2026-03-20")]
    assert M.current(facts, "2026-03-25")["fact_id"] == "a"  # stated, not yet in force
    assert M.current(facts, "2026-04-02")["fact_id"] == "b"
    assert M.current(facts, "2026-03-19")["fact_id"] == "a"  # record not seen yet


def test_one_stale_record_cannot_roll_back():
    facts = [f("a", "14 days", "2026-01-10"), f("b", "30 days", "2026-04-01"), f("c", "14 days", "2026-04-08")]
    assert M.current(facts, "2026-04-10")["fact_id"] == "b"


def test_reversion_needs_two_records():
    facts = [f("a", "14 days", "2026-01-10"), f("b", "30 days", "2026-04-01"),
             f("c", "14 days", "2026-04-08"), f("d", "14 days", "2026-05-01")]
    assert M.current(facts, "2026-04-20")["fact_id"] == "b"
    assert M.current(facts, "2026-05-02")["fact_id"] == "d"


def test_value_class_beats_wording():
    facts = [f("a", "two weeks", "2026-01-10", vclass="x"), f("b", "30 days", "2026-04-01", vclass="y"),
             f("c", "14 days", "2026-04-08", vclass="x")]
    assert M.current(facts, "2026-04-10")["fact_id"] == "b"  # same class as the superseded value, held back


def test_group_ids_unions_pairs():
    g = M.group_ids(["a", "b", "c", "d"], [("b", "a"), ("c", "b"), ("x", "d")])
    assert g["a"] == g["b"] == g["c"] != g["d"]


def fact(fid, record_date, value, vector):
    return {"fact_id": fid, "record_id": fid.split("#")[0], "record_date": record_date, "effective": None,
            "dated": record_date, "subject": "Spark 100", "attribute": "price", "value": value, "quote": value,
            "statement": f"Spark 100, price: {value}", "vector": vector}


def test_store_is_insert_only_and_groups_by_links(tmp_path):
    mem = M.Memory(tmp_path / "m.sqlite")
    mem.add_fact(fact("r1#f1", "2026-01-10", "$39", [1.0, 0.0]))
    mem.add_fact(fact("r2#f1", "2026-03-05", "$42", [1.0, 0.1]))
    mem.add_fact(fact("r3#f1", "2026-03-06", "42 dollars", [1.0, 0.1]))
    mem.add_fact(fact("r4#f1", "2026-03-07", "1.2 TB", [0.0, 1.0]))
    mem.add_links([("r2#f1", "r1#f1", 2.0, 0.9, 0.1, 0), ("r3#f1", "r2#f1", 2.0, 0.9, 0.9, 0),
                   ("r4#f1", "r1#f1", 1.0, 0.2, 0.0, 0), ("r4#f1", "r3#f1", None, None, None, 1)])
    g = mem.groups()
    assert g["r1#f1"] == g["r2#f1"] == g["r3#f1"] != g["r4#f1"]
    v = mem.value_classes()
    assert v["r2#f1"] == v["r3#f1"] != v["r1#f1"]
    assert set(mem.groups("2026-03-05")) == {"r1#f1", "r2#f1"}
    with pytest.raises(sqlite3.DatabaseError):
        mem.db.execute("UPDATE facts SET value='x'")
    with pytest.raises(sqlite3.DatabaseError):
        mem.db.execute("DELETE FROM links")


class Embed:
    def embed(self, texts):
        return [[1.0, 0.05] for _ in texts]


def test_notes_give_current_value_and_history(tmp_path):
    mem = M.Memory(tmp_path / "m.sqlite")
    mem.add_fact(fact("r1#f1", "2026-01-10", "$39", [1.0, 0.0]))
    mem.add_fact(fact("r2#f1", "2026-03-05", "$42", [1.0, 0.1]))
    mem.add_links([("r2#f1", "r1#f1", 2.0, 0.9, 0.1, 0)])
    n = M.notes(mem, "What does Spark 100 cost?", "2026-04-01", Embed())
    assert n.startswith("- Spark 100, price: $42") and "$39 (2026-01-10)" in n
    assert "$42" not in M.notes(mem, "What does Spark 100 cost?", "2026-02-01", Embed())
    assert M.notes(mem, "x", "2026-01-01", Embed()) == ""


def test_link_rubric_is_valid():
    assert M.LINK_RUBRIC.critical_keys() == ["same_attribute"]


def test_fact_joins_only_its_best_match(tmp_path):
    mem = M.Memory(tmp_path / "m.sqlite")
    mem.add_fact(fact("r1#f1", "2026-01-10", "$39", [1.0, 0.0]))
    mem.add_fact(fact("r2#f1", "2026-01-11", "1.2 TB", [0.0, 1.0]))
    mem.add_fact(fact("r3#f1", "2026-01-12", "$42", [1.0, 0.0]))
    mem.add_links([("r3#f1", "r1#f1", 2.0, 0.95, 0.1, 0), ("r3#f1", "r2#f1", 1.0, 0.6, 0.0, 0)])
    g = mem.groups()
    assert g["r3#f1"] == g["r1#f1"] != g["r2#f1"]


def test_fork_copies_facts_links_and_spend(tmp_path, monkeypatch):
    monkeypatch.setattr(M, "mem_path", lambda run: tmp_path / f"memory-{run}.sqlite")
    src = M.Memory(tmp_path / "memory-a.sqlite")
    src.add_fact(fact("r1#f1", "2026-01-10", "$39", [1.0, 0.0]))
    src.add_links([("r1#f1", "r0#f1", 1.0, 0.1, 0.0, 0)])
    src.add_spend("extract", "r1", 0.5)
    src.add_spend("answer", None, 0.2)
    src.db.close()
    M.fork("a", "a2")
    new = M.Memory(tmp_path / "memory-a2.sqlite")
    assert len(new.facts()) == 1 and new.done_records() == {"r1"} and new.spent() == 0.5
    assert new.db.execute("SELECT COUNT(*) FROM links").fetchone()[0] == 1


def test_canonical_keys_group_and_jev_can_veto(tmp_path):
    mem = M.Memory(tmp_path / "m.sqlite")
    for fid, day, val in (("r1#f1", "2026-01-10", "12 months"), ("r2#f1", "2026-05-20", "24 months"),
                          ("r3#f1", "2026-05-21", "month-to-month"), ("r4#f1", "2026-05-22", "$39")):
        mem.add_fact(fact(fid, day, val, [1.0, 0.0]))
    for fid, key in (("r1#f1", "price_lock_length"), ("r2#f1", "price_lock_length"), ("r3#f1", "price_lock_length"),
                     ("r4#f1", "spark_100_monthly_price")):
        mem.add_key(fid, key)
    mem.add_links([("r2#f1", "r1#f1", 2.0, 0.81, 0.05, 0),   # true change: JEV agrees with the key
                   ("r3#f1", "r1#f1", 1.0, 0.2, 0.0, 0), ("r3#f1", "r2#f1", 1.0, 0.3, 0.0, 0)])  # JEV vetoes
    g = mem.groups()
    assert g["r1#f1"] == g["r2#f1"] == "k:price_lock_length"
    assert g["r3#f1"] == "r3#f1" and g["r4#f1"] == "k:spark_100_monthly_price"
    assert M.current([{**dict(r), "vclass": None} for r in mem.facts() if g[r["fact_id"]] == "k:price_lock_length"],
                     "2026-06-01")["value"] == "24 months"


def test_local_extraction_adds_a_second_pass_for_missed_facts():
    import json
    from types import SimpleNamespace

    def fact(v):
        return {"key": "k", "subject": "s", "attribute": "a", "value": v, "effective_date": "", "quote": "q"}

    class Fake:
        def __init__(self, local, replies):
            self.local, self.replies, self.prompts = local, list(replies), []
            self.messages = self

        def create(self, **kw):
            self.prompts.append((kw["system"], kw["messages"][0]["content"]))
            text = json.dumps({"facts": self.replies.pop(0)})
            zero = SimpleNamespace(input_tokens=0, output_tokens=0, cache_creation_input_tokens=0, cache_read_input_tokens=0)
            return SimpleNamespace(stop_reason="end_turn", content=[SimpleNamespace(type="text", text=text)], usage=zero)

    rec = {"id": "r1", "date": "2026-01-01", "kind": "ticket", "text": "Fee is $25. Window is 14 days."}
    local = Fake(True, [[fact("$25")], [fact("14 days")]])
    facts, _ = M.extract(local, rec, keys=[])
    assert [x["value"] for x in facts] == ["$25", "14 days"]
    assert M.LOCAL_HINT in local.prompts[0][0] and "- s a: $25" in local.prompts[1][1]
    claude = Fake(False, [[fact("$25")]])
    assert len(M.extract(claude, rec, keys=[])[0]) == 1 and M.LOCAL_HINT not in claude.prompts[0][0]


def test_local_extraction_keys_after_extracting():
    import json
    from types import SimpleNamespace

    class Fake:
        local = True

        def __init__(self, replies):
            self.replies, self.prompts = list(replies), []
            self.messages = self

        def create(self, **kw):
            self.prompts.append((kw["system"], kw["messages"][0]["content"]))
            zero = SimpleNamespace(input_tokens=0, output_tokens=0, cache_creation_input_tokens=0, cache_read_input_tokens=0)
            return SimpleNamespace(stop_reason="end_turn", content=[SimpleNamespace(type="text", text=json.dumps(self.replies.pop(0)))], usage=zero)

    fact = {"key": "fee", "subject": "install", "attribute": "fee", "value": "$50", "effective_date": "", "quote": "q"}
    c = Fake([{"facts": [fact]}, {"facts": []}, {"keys": ["install_fee"]}])
    facts, _ = M.extract(c, {"id": "r", "date": "2026-01-01", "kind": "ticket", "text": "t"}, keys=["install_fee", "spark_price"])
    assert facts[0]["key"] == "install_fee"
    assert "none yet" in c.prompts[0][1] and "install_fee, spark_price" in c.prompts[2][1]
    two = Fake([{"facts": [fact, fact]}, {"facts": []}, {"keys": ["a"]}, {"keys": ["a"]}, {"keys": ["b"]}])
    assert [x["key"] for x in M.extract(two, {"id": "r", "date": "d", "kind": "k", "text": "t"}, keys=["x"])[0]] == ["a", "b"]
    with pytest.raises(RuntimeError):
        M.extract(Fake([{"facts": [fact]}, {"facts": []}, {"keys": []}, {"keys": []}]), {"id": "r", "date": "d", "kind": "k", "text": "t"}, keys=["x"])


def test_sop_in_force_outranks_tickets():
    sop = {**f("s", "21 days", "2026-10-15"), "official": "SOP-02 v6"}
    stale_ticket = f("t", "30 days", "2026-10-20")
    early_ticket = f("e", "4.3", "2026-08-10")
    assert M.current([sop, stale_ticket], "2026-10-21")["fact_id"] == "s"
    assert M.current([f("v5", "4.2", "2026-07-01") | {"official": "SOP-03 v5"}, early_ticket], "2026-08-12")["value"] == "4.2"
    assert M.current([sop, f("t0", "30 days", "2026-10-01")], "2026-10-14")["fact_id"] == "t0"  # no SOP in force yet
    assert M.official_source("sop-02-v6") == "SOP-02 v6" and M.official_source("gov-01-v2") == "GOV-01 v2"
    assert M.official_source("qb-004") is None


def test_local_keying_never_gives_two_facts_of_one_record_one_key():
    import json
    from types import SimpleNamespace

    class Fake:
        local = True

        def __init__(self, replies):
            self.replies, self.prompts = list(replies), []
            self.messages = self

        def create(self, **kw):
            self.prompts.append(kw["messages"][0]["content"])
            zero = SimpleNamespace(input_tokens=0, output_tokens=0, cache_creation_input_tokens=0, cache_read_input_tokens=0)
            return SimpleNamespace(stop_reason="end_turn", content=[SimpleNamespace(type="text", text=json.dumps(self.replies.pop(0)))], usage=zero)

    fix = {"key": "", "subject": "Q-Box", "attribute": "fix", "value": "Firmware 4.2 update", "effective_date": "", "quote": "1. Fix: Firmware 4.2 update."}
    fw = {**fix, "attribute": "firmware", "value": "4.2", "quote": "2. Firmware: 4.2."}
    c = Fake([{"facts": [fix, fw]}, {"facts": []}, {"keys": ["firmware", "firmware"]}, {"keys": ["redlight_fix"]}])
    facts, _ = M.extract(c, {"id": "sop-03-v2", "date": "2026-03-10", "kind": "sop", "text": "t"}, keys=["firmware", "status_page"])
    assert [f["key"] for f in facts] == ["firmware", "redlight_fix"]
    assert "firmware" not in c.prompts[-1].split("Held keys: ")[1].split("\n")[0]


def test_version_value_pattern_for_citations():
    import re
    pat = r"^((sop|gov)-\d+\s+)?(v|version)\s*\w+$"
    assert all(re.match(pat, v, re.I) for v in ("v5", "version five", "SOP-04 version 8", "Version 6"))
    assert not any(re.match(pat, v, re.I) for v in ("Script v1", "4.2", "12 months"))


def test_announcement_outranks_tickets_and_sop_outranks_both():
    ann = {**f("a", "1-888-555-0177", "2026-04-20", "2026-04-10"), "announced": True}
    old, stale = f("o", "1-800-555-0142", "2026-03-01"), f("t", "1-800-555-0142", "2026-04-22")
    assert M.current([old, ann, stale], "2026-04-23")["fact_id"] == "a"
    assert M.current([old, ann, stale], "2026-04-15")["fact_id"] == "o"  # announced, not yet in force
    sop = {**f("s", "x", "2026-04-01"), "official": "SOP-01 v4"}
    assert M.current([ann, sop, stale], "2026-04-23")["fact_id"] == "s"


def test_a_later_notice_moves_the_start_date():
    early = {**f("e", "Adds Calder", "2026-03-15", "2026-03-02"), "effective": "2026-03-15", "announced": True}
    delay = {**f("d", "Adds Calder", "2026-04-01", "2026-03-12"), "effective": "2026-04-01", "announced": True}
    old = f("o", "Alder, Brook", "2026-01-20")
    assert M.current([old, early], "2026-03-20")["fact_id"] == "e"  # before the delay notice is seen
    assert M.current([old, early, delay], "2026-03-20")["fact_id"] == "o"
    assert M.current([old, early, delay], "2026-04-02")["fact_id"] == "d"
    other = {**f("x", "Adds Dunmore", "2026-10-01", "2026-09-21"), "effective": "2026-10-01"}
    assert M.current([old, early, other], "2026-03-20")["fact_id"] == "e"  # a different value moves nothing


def test_fork_copies_canonical_keys(tmp_path, monkeypatch):
    monkeypatch.setattr(M, "mem_path", lambda run: tmp_path / f"memory-{run}.sqlite")
    src = M.Memory(tmp_path / "memory-b.sqlite")
    src.add_fact(fact("r1#f1", "2026-01-10", "$39", [1.0, 0.0]))
    src.add_key("r1#f1", "spark_100_monthly_price")
    src.db.close()
    M.fork("b", "c")
    assert M.Memory(tmp_path / "memory-c.sqlite").keys() == {"r1#f1": "spark_100_monthly_price"}
