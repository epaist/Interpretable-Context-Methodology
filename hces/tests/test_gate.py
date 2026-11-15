from pathlib import Path

import pytest

from hces import gate as G
from hces.rollup import Cutoffs

CTX = """# Stage 02: Mapping

## Inputs

| Source | File/Location | Section/Scope | Why |
|--------|--------------|---------------|-----|
| User | (conversation) | Full description | The domain |
| Previous stage | `../01-discovery/output/workflow-map.md` | Full file | The map |
| Template | `/_core/templates/t.md` | Full file | Copy it |
| Core conventions | `/_core/CONVENTIONS.md` | "Pattern 1" and "Pattern 3" | Rules |

## Process

| Not | An | Input | Row |
"""


def test_inputs_table_reads_rows_and_stops_at_next_heading(tmp_path):
    (tmp_path / "CONTEXT.md").write_text(CTX, encoding="utf-8")
    rows = G.inputs_table(tmp_path / "CONTEXT.md")
    assert [r["source"] for r in rows] == ["User", "Previous stage", "Template", "Core conventions"]
    assert rows[3]["scope"] == '"Pattern 1" and "Pattern 3"'


def test_malformed_row_fails(tmp_path):
    (tmp_path / "CONTEXT.md").write_text("## Inputs\n\n| a | b |\n", encoding="utf-8")
    with pytest.raises(ValueError):
        G.inputs_table(tmp_path / "CONTEXT.md")


def test_kinds_and_upstream_stage(tmp_path):
    stage, root = tmp_path / "ws" / "stages" / "02-mapping", tmp_path
    paths = [G.resolve(loc, stage, root) for loc in
             ["(conversation)", "`../01-discovery/output/workflow-map.md`", "`/_core/templates/t.md`", "`/_core/CONVENTIONS.md`"]]
    assert [G.kind(p) for p in paths] == ["user", "upstream", "template", "reference"]
    assert G.upstream_stage(paths[1]) == "01-discovery"
    assert paths[3] == root / "_core" / "CONVENTIONS.md"


def test_hand_scope_selects_named_headings_and_fails_on_unknown():
    units = [{"id": "a", "trail": ["C", "Pattern 1"]}, {"id": "b", "trail": ["C", "Pattern 2"]},
             {"id": "c", "trail": ["C", "Pattern 3", "Sub"]}]
    assert [u["id"] for u in G.hand_scope(units, '"Pattern 1" and "Pattern 3"')] == ["a", "c"]
    assert G.hand_scope(units, "Full file") == units
    with pytest.raises(ValueError):
        G.hand_scope(units, '"Pattern 9"')


def test_keep_fills_budget_by_score_and_returns_file_order():
    rub = G.task_rubric("t/1", "02-mapping", "write contracts")
    units = [{"id": f"u{i}", "tokens": 100} for i in range(4)]
    rel = {"u0": 3, "u1": 4, "u2": 0, "u3": 3}
    j = {u: {"relevance": {"value": v}, "contains_fact": {"value": 0.0}} for u, v in rel.items()}
    kept = G.keep(units, j, rub, 200, Cutoffs(0.75, 0.75, 0.9))
    assert [u["id"] for u in kept] == ["u0", "u1"]  # u1 first by score, u0 beats u3 on rank; file order out
    assert G.keep(units, {u: {"relevance": {"value": 0}} for u in rel}, rub, 200, Cutoffs(0.75, 0.75, 0.9)) == []
