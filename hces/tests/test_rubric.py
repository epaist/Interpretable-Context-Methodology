import pytest

from hces.rubric import Question, Rubric, RubricError


def test_hash_is_stable_and_sensitive(rubric):
    same = Rubric.from_dict(__import__("json").loads(rubric.canonical()))
    assert same.hash == rubric.hash
    changed = Rubric(rubric.rubric_id, rubric.version, rubric.task + "?", rubric.questions, rubric.answerability)
    assert changed.hash != rubric.hash


def test_unit_score_weighted_and_scaled(rubric):
    # relevance 3 of 0..3 -> 1.0 (weight 2); specific 0 of 0..1 -> 0.0 (weight 1)
    assert rubric.unit_score({"relevance": 3.0, "specific": 0.0}) == pytest.approx(2 / 3)


def test_missing_score_answer_raises(rubric):
    with pytest.raises(RubricError, match="specific"):
        rubric.unit_score({"relevance": 1.0})


def test_wire_questions_match_sdk_shapes(rubric):
    w = rubric.wire_questions()
    assert w["relevance"]["type"] == "score" and len(w["relevance"]["criteria"]) == 4
    assert w["has_fact"] == {"type": "noul", "instructions": "Does this passage state why the keeper leaves?"}
    assert set(w["speaker"]["criteria"]) == {"keeper", "narrator", "other"}
    assert rubric.critical_keys() == ["has_fact"]


@pytest.mark.parametrize(
    "bad",
    [
        Question("s", "score", "x", ["only one"]),
        Question("c", "choice", "x", {}),
        Question("n", "score", "x", ["a", "b"], critical=True),
        Question("t", "free text", "x"),
    ],
)
def test_bad_questions_are_refused(rubric, bad):
    with pytest.raises(RubricError):
        Rubric("r", 1, "task", rubric.questions[:1] + (bad,), rubric.answerability)


def test_needs_a_score_and_a_noul_answerability(rubric):
    with pytest.raises(RubricError, match="Score"):
        Rubric("r", 1, "task", (rubric.questions[2],), rubric.answerability)
    with pytest.raises(RubricError, match="Noul"):
        Rubric("r", 1, "task", rubric.questions, rubric.questions[0])
