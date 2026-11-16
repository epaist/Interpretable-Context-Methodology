from types import SimpleNamespace

from hces import gate as G


def test_gate_writes_kept_sections_with_no_budget_by_default(tmp_path, monkeypatch, capsys):
    import hces.config
    import hces.passages
    import hces.store

    units = [{"id": "a.md#Rules", "text": "No em dashes.", "tokens": 5, "trail": "Rules"},
             {"id": "a.md#History", "text": "Old notes.", "tokens": 4, "trail": "History"}]
    seen = {}
    monkeypatch.setattr(hces.config, "load", lambda: SimpleNamespace(results_store=tmp_path / "r.db"))
    monkeypatch.setattr(hces.store, "Store", lambda path: None)
    monkeypatch.setattr(hces.passages, "TokenCounter", lambda: None)
    monkeypatch.setattr(G, "stage_units", lambda stage, root, count: (units, units))
    monkeypatch.setattr(G, "judge_units", lambda store, cfg, rub, us: ({}, 0.001))
    monkeypatch.setattr(G, "frozen", lambda: None)
    monkeypatch.setattr(G, "keep", lambda us, j, rub, budget, cut: seen.setdefault("budget", budget) and us[:1])
    out = tmp_path / "kept.md"
    assert G.main([str(tmp_path), "--task", "write the stage", "--yes", "--out", str(out)]) == 0
    assert seen["budget"] == G.OPEN
    text = out.read_text(encoding="utf-8")
    assert "## a.md#Rules" in text and "No em dashes." in text and "Old notes." not in text and "1 of 2 sections" in text
