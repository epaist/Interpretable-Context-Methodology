import json
from types import SimpleNamespace

import pytest

from hces import __main__ as C
from hces import memory as M


class Fake:
    """Claude-shaped client: replies in order, records prompts."""

    def __init__(self, replies):
        self.replies, self.prompts = list(replies), []
        self.messages = self

    def create(self, **kw):
        self.prompts.append(kw["messages"][-1]["content"])
        return SimpleNamespace(stop_reason="end_turn", content=[SimpleNamespace(type="text", text=self.replies.pop(0))],
                               usage=SimpleNamespace(input_tokens=0, output_tokens=0, cache_read_input_tokens=0,
                                                     cache_creation_input_tokens=0))


class Embed:
    def embed(self, texts):
        return [[1.0, 0.0] for _ in texts]


def fact(value, key="refund_window_days"):
    return {"key": key, "subject": "Refunds", "attribute": "window", "value": value, "effective_date": "", "quote": f"Refunds within {value}."}


@pytest.fixture
def wired(monkeypatch):
    monkeypatch.setattr(C, "tools", lambda: (SimpleNamespace(price_per_million=0.0), Embed(), None))

    def use(client):
        monkeypatch.setattr(C, "client_for", lambda a: client)
    return use


def test_remember_then_recall(tmp_path, wired, capsys):
    store, note = tmp_path / "m.sqlite", tmp_path / "policy.md"
    note.write_text("Refunds are accepted within 30 days.", encoding="utf-8")
    wired(Fake([json.dumps({"facts": [fact("30 days")]})]))
    assert C.main(["remember", "--store", str(store), "--file", str(note), "--date", "2026-04-02", "--yes"]) == 0
    assert "1 facts" in capsys.readouterr().out
    client = Fake(["The refund window is 30 days."])
    wired(client)
    assert C.main(["recall", "--store", str(store), "How long is the refund window?", "--as-of", "2026-05-01", "--notes"]) == 0
    out = capsys.readouterr().out
    assert out.startswith("The refund window is 30 days.") and "30 days" in client.prompts[0]


def test_recall_before_the_record_date_knows_nothing(tmp_path, wired, capsys):
    store, note = tmp_path / "m.sqlite", tmp_path / "policy.md"
    note.write_text("Refunds are accepted within 30 days.", encoding="utf-8")
    wired(Fake([json.dumps({"facts": [fact("30 days")]})]))
    C.main(["remember", "--store", str(store), "--file", str(note), "--date", "2026-04-02", "--yes"])
    wired(Fake([]))
    C.main(["recall", "--store", str(store), "How long is the refund window?", "--as-of", "2026-03-01"])
    assert capsys.readouterr().out.strip().endswith(M.NOT_KNOWN)


def test_remember_needs_yes_and_refuses_a_second_copy(tmp_path, wired):
    store, note = tmp_path / "m.sqlite", tmp_path / "n.md"
    note.write_text("Support is 24/7.", encoding="utf-8")
    with pytest.raises(SystemExit):
        C.main(["remember", "--store", str(store), "--file", str(note)])
    wired(Fake([json.dumps({"facts": []})]))
    C.main(["remember", "--store", str(store), "--file", str(note), "--date", "2026-01-01", "--yes"])
    with pytest.raises(SystemExit, match="insert-only"):
        C.main(["remember", "--store", str(store), "--file", str(note), "--date", "2026-01-01", "--yes"])


def test_bad_date_and_missing_store_fail(tmp_path, wired):
    note = tmp_path / "n.md"
    note.write_text("x", encoding="utf-8")
    with pytest.raises(ValueError):
        C.main(["remember", "--store", str(tmp_path / "m.sqlite"), "--file", str(note), "--date", "15/11/2026", "--yes"])
    with pytest.raises(SystemExit, match="No memory store"):
        C.main(["recall", "--store", str(tmp_path / "none.sqlite"), "q"])


def test_gate_is_passed_through(monkeypatch):
    from hces import gate

    seen = []
    monkeypatch.setattr(gate, "main", lambda argv: seen.append(argv) or 0)
    assert C.main(["gate", "stage-dir", "--task", "t"]) == 0 and seen == [["stage-dir", "--task", "t"]]
