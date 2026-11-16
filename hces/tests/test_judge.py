from types import SimpleNamespace

import pytest

from hces.judge import JevJudge, evidence_batches
from hces.units import Unit


class FakeClient:
    """Stands in for TypeSafeClient: same call, same answer shapes."""

    def __init__(self, fail_on=None):
        self.calls = []
        self.fail_on = fail_on

    def system_one(self, state, questions, model=None):
        self.calls.append((state, questions, model))
        text = state.get("passage", "")
        if self.fail_on and self.fail_on in text:
            raise RuntimeError("boom")
        answers = {}
        for key, q in questions.items():
            if q["type"] == "score":
                answers[key] = SimpleNamespace(score=float(len(q["criteria"]) - 1), confidence=0.9)
            elif q["type"] == "noul":
                answers[key] = SimpleNamespace(noul=0.8)
            else:
                answers[key] = SimpleNamespace(choice=next(iter(q["criteria"])), confidence=0.7)
        return SimpleNamespace(answers=answers, model="jev-1.14.0", usage=SimpleNamespace(input_tokens=55))


def make(client, cap=32000):
    return JevJudge("jev-1.14.0", workers=3, price_per_million=0.042, state_cap=cap, client_factory=lambda: client)


UNITS = [Unit(f"u{i}", f"passage number {i} about the keeper") for i in range(5)]


def test_one_request_per_unit_with_typed_answers(rubric):
    client = FakeClient()
    js = make(client).judge(rubric.task, rubric, UNITS)
    assert len(client.calls) == 5
    assert len(js) == 5 * len(rubric.questions)
    rel = [j for j in js if j.question_key == "relevance"][0]
    assert rel.value == 3.0 and rel.model == "jev-1.14.0" and rel.tokens_in == 55
    sp = [j for j in js if j.question_key == "speaker"][0]
    assert sp.label == "keeper" and sp.confidence == 0.7
    assert client.calls[0][2] == "jev-1.14.0"
    assert client.calls[0][0]["task"] == rubric.task


def test_failure_is_recorded_not_skipped(rubric):
    js = make(FakeClient(fail_on="number 2")).judge(rubric.task, rubric, UNITS)
    failed = [j for j in js if j.failed]
    assert len(failed) == len(rubric.questions)
    assert all(j.unit_id == "u2" and "boom" in j.error for j in failed)


def test_answerable_takes_best_batch(rubric):
    j = make(FakeClient())
    assert j.answerable(rubric.task, rubric, UNITS) == pytest.approx(0.8)
    assert j.last_tokens == 55 * len(j._client.calls)
    assert j.answerable(rubric.task, rubric, []) == 0.0
    assert j.last_tokens == 0


def test_evidence_batches_respect_cap():
    units = [Unit(f"u{i}", "x" * 400) for i in range(10)]  # about 100 tokens each
    batches = evidence_batches(units, cap_tokens=600, task="t")
    assert sum(len(b) for b in batches) == 10
    assert all(sum(u.token_count for u in b) <= 400 for b in batches)
    with pytest.raises(ValueError):
        evidence_batches([Unit("big", "x" * 4000)], cap_tokens=600, task="t")


def test_cost_estimate_scales_with_units(rubric):
    j = make(FakeClient())
    one = j.estimate_cost(rubric.task, rubric, UNITS[:1])
    five = j.estimate_cost(rubric.task, rubric, UNITS)
    assert 0 < one < five < 0.001
