import sqlite3

import pytest

from hces.judge import Judgment
from hces.store import TABLES, Store, new_run_id


def run_row(run_id):
    return dict(run_id=run_id, arm="rag+jev", access_ms=1.0, analysis_ms=2.0, response_ms=3.0,
                peak_rss_mb=50.0, tokens_in=100, cost_usd=0.0)


def test_round_trip(tmp_path, rubric):
    s = Store(tmp_path / "r.db")
    s.add_rubric(rubric)
    s.add_rubric(rubric)  # same hash: no-op
    rid = new_run_id()
    s.add_judgments(rid, rubric, [Judgment("u1", "relevance", "score", 2.5, model="jev", tokens_in=40)])
    s.add_decisions(rid, [{"unit_id": "u1", "kept": True, "final_score": 0.8, "rank": 1, "reason": "score"}])
    s.add_run(run_row(rid))
    assert s.run(rid)["peak_rss_mb"] == 50.0
    assert s.judgments(rid)[0]["value"] == 2.5


@pytest.mark.parametrize("table", TABLES)
@pytest.mark.parametrize("op", ["UPDATE {t} SET rowid = rowid", "DELETE FROM {t}"])
def test_insert_only_is_enforced(tmp_path, rubric, table, op):
    s = Store(tmp_path / "r.db")
    rid = new_run_id()
    s.add_rubric(rubric)
    s.add_judgments(rid, rubric, [Judgment("u1", "relevance", "score", 1.0)])
    s.add_decisions(rid, [{"unit_id": "u1", "kept": False, "reason": "below cutoff"}])
    s.add_run(run_row(rid))
    with pytest.raises(sqlite3.IntegrityError, match="insert-only"):
        with s.db:
            s.db.execute(op.format(t=table))


def test_changed_rubric_needs_new_version(tmp_path, rubric):
    from hces.rubric import Rubric

    s = Store(tmp_path / "r.db")
    s.add_rubric(rubric)
    edited = Rubric(rubric.rubric_id, rubric.version, "a different task", rubric.questions, rubric.answerability)
    with pytest.raises(ValueError, match="bump the version"):
        s.add_rubric(edited)


def test_run_without_timings_is_refused(tmp_path):
    s = Store(tmp_path / "r.db")
    row = run_row(new_run_id())
    row.pop("response_ms")
    with pytest.raises(ValueError, match="response_ms"):
        s.add_run(row)
