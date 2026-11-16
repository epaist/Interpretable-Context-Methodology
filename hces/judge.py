"""The judge interface and its JEV implementation.

A judge answers typed questions; it never decides. Code reads the answers and decides.
Any judge (JEV now, a local model later) implements the same four members.
"""

from __future__ import annotations

import json
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from typing import Callable, Iterable, Protocol, Sequence

from hces.rubric import Rubric
from hces.units import Unit, approx_tokens


@dataclass(frozen=True)
class Judgment:
    unit_id: str
    question_key: str
    qtype: str
    value: float | None  # Score: expected level; Noul: probability of yes; Choice: confidence
    label: str | None = None  # Choice: the chosen label
    confidence: float | None = None
    model: str | None = None
    tokens_in: int | None = None  # tokens for the whole request, recorded on every answer of that request
    error: str | None = None

    @property
    def failed(self) -> bool:
        return self.error is not None


class Judge(Protocol):
    model_id: str

    def judge(self, task: str, rubric: Rubric, units: Sequence[Unit]) -> list[Judgment]: ...

    def answerable(self, task: str, rubric: Rubric, kept: Sequence[Unit]) -> float: ...

    def estimate_cost(self, task: str, rubric: Rubric, units: Sequence[Unit]) -> float: ...


def unit_state(task: str, unit: Unit) -> dict:
    return {"task": task, "passage": unit.text}


def evidence_batches(kept: Sequence[Unit], cap_tokens: int, task: str) -> list[list[Unit]]:
    """Split kept units into groups whose state stays under the per-question cap."""
    room = cap_tokens - approx_tokens(task) - 200  # headroom for keys and the question
    if room <= 0:
        raise ValueError("Task alone exceeds the JEV state cap")
    batches: list[list[Unit]] = [[]]
    used = 0
    for u in kept:
        t = u.token_count
        if t > room:
            raise ValueError(f"Unit {u.id} ({t} tokens) exceeds the JEV state cap on its own")
        if used + t > room and batches[-1]:
            batches.append([])
            used = 0
        batches[-1].append(u)
        used += t
    return [b for b in batches if b]


class JevJudge:
    """JEV through typesafe-sdk. One request per unit, run in parallel."""

    def __init__(self, model: str, workers: int, price_per_million: float, state_cap: int,
                 client_factory: Callable[[], object] | None = None):
        self.model_id = model
        self.workers = workers
        self.price = price_per_million
        self.state_cap = state_cap
        if client_factory is None:
            from typesafe_sdk import TypeSafeClient

            client_factory = lambda: TypeSafeClient(model=model)  # noqa: E731
        self._client = client_factory()

    def _ask(self, state: dict, questions: dict) -> tuple[dict, str, int]:
        resp = self._client.system_one(state=state, questions=questions, model=self.model_id)
        return resp.answers, resp.model, resp.usage.input_tokens

    def _one(self, task: str, rubric: Rubric, unit: Unit) -> list[Judgment]:
        state = unit_state(task, unit)
        if approx_tokens(json.dumps(state)) > self.state_cap:
            return [Judgment(unit.id, q.key, q.type, None, error="state over cap") for q in rubric.questions]
        try:
            answers, model, tokens = self._ask(state, rubric.wire_questions())
        except Exception as exc:  # recorded, never skipped
            return [Judgment(unit.id, q.key, q.type, None, error=f"{type(exc).__name__}: {exc}") for q in rubric.questions]
        out = []
        for q in rubric.questions:
            a = answers.get(q.key)
            if a is None:
                out.append(Judgment(unit.id, q.key, q.type, None, model=model, tokens_in=tokens, error="no answer"))
            elif q.type == "score":
                out.append(Judgment(unit.id, q.key, q.type, float(a.score), confidence=a.confidence, model=model, tokens_in=tokens))
            elif q.type == "noul":
                out.append(Judgment(unit.id, q.key, q.type, float(a.noul), model=model, tokens_in=tokens))
            else:
                out.append(Judgment(unit.id, q.key, q.type, float(a.confidence), label=a.choice,
                                    confidence=a.confidence, model=model, tokens_in=tokens))
        return out

    def judge(self, task: str, rubric: Rubric, units: Sequence[Unit]) -> list[Judgment]:
        with ThreadPoolExecutor(max_workers=self.workers) as pool:
            results = pool.map(lambda u: self._one(task, rubric, u), units)
        return [j for group in results for j in group]

    def answerable(self, task: str, rubric: Rubric, kept: Sequence[Unit]) -> float:
        """Highest yes-probability over evidence batches; 0.0 when nothing was kept."""
        self.last_tokens = 0  # billed tokens of this call, summed over its batches
        if not kept:
            return 0.0
        best = 0.0
        q = rubric.answerability
        for batch in evidence_batches(kept, self.state_cap, task):
            state = {"task": task, "evidence": [{"id": u.id, "text": u.text} for u in batch]}
            answers, _, tokens = self._ask(state, {q.key: q.wire()})
            self.last_tokens += tokens
            best = max(best, float(answers[q.key].noul))
        return best

    def request_tokens(self, task: str, rubric: Rubric, units: Iterable[Unit]) -> int:
        qtok = approx_tokens(json.dumps(rubric.wire_questions()))
        return sum(approx_tokens(json.dumps(unit_state(task, u))) + qtok for u in units)

    def estimate_cost(self, task: str, rubric: Rubric, units: Sequence[Unit]) -> float:
        return self.request_tokens(task, rubric, units) * self.price / 1e6
