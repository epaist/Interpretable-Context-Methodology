from hces.report import rescore
from hces.store import Store


def test_rescore_uses_decisions_and_current_key(tmp_path):
    s = Store(tmp_path / "r.db")
    s.add_decisions("run1", [{"unit_id": "v/a", "kept": True, "rank": 1, "final_score": None, "reason": "within budget"},
                             {"unit_id": "v/b", "kept": True, "rank": 2, "final_score": None, "reason": "within budget"},
                             {"unit_id": "v/c", "kept": False, "rank": 3, "final_score": None, "reason": "over budget"}])
    runs = [{"run_id": "run1", "question_id": "v/q01", "variant": "hybrid/plain",
             "notes": {"gold_kept": 0, "decoys_kept": 0}}]
    key = {"v/q01": {"gold": {"plain": ["v/b", "v/c"], "chaptered": []},
                     "decoy_gold": {"plain": ["v/a"], "chaptered": []}}}
    rescore(s, runs, key)
    assert runs[0]["notes"] == {"gold_kept": 1, "decoys_kept": 1}
