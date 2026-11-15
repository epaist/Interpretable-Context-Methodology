"""Versioned rubrics: the typed questions the judge answers about each unit.

The shape is fixed (relevance Scores, an optional critical Noul, metadata Choices, one
answerability Noul). The wording is written per task. A rubric is hashed, so a stored
result always points at the exact questions that produced it.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from pathlib import Path

TYPES = ("score", "noul", "choice")


class RubricError(ValueError):
    pass


@dataclass(frozen=True)
class Question:
    key: str
    type: str
    instructions: str
    criteria: list | dict | None = None
    weight: float = 1.0
    critical: bool = False

    def validate(self) -> None:
        if self.type not in TYPES:
            raise RubricError(f"Question '{self.key}': type must be one of {TYPES}")
        if not self.instructions.strip():
            raise RubricError(f"Question '{self.key}': instructions are empty")
        if self.type == "score":
            if not isinstance(self.criteria, list) or len(self.criteria) < 2:
                raise RubricError(f"Score '{self.key}': needs at least 2 ordered criteria, one per level from 0")
            if self.weight <= 0:
                raise RubricError(f"Score '{self.key}': weight must be above 0")
        if self.type == "choice" and (not isinstance(self.criteria, dict) or not self.criteria):
            raise RubricError(f"Choice '{self.key}': needs a nonempty label mapping")
        if self.critical and self.type != "noul":
            raise RubricError(f"Question '{self.key}': only a Noul can be critical")

    def wire(self) -> dict:
        out: dict = {"type": self.type, "instructions": self.instructions}
        if self.criteria is not None:
            out["criteria"] = self.criteria
        return out


@dataclass(frozen=True)
class Rubric:
    rubric_id: str
    version: int
    task: str
    questions: tuple[Question, ...]
    answerability: Question
    notes: str = ""
    _hash: str = field(default="", compare=False, repr=False)

    def __post_init__(self) -> None:
        if not self.task.strip():
            raise RubricError("Rubric task is empty")
        keys = [q.key for q in self.questions]
        if len(set(keys)) != len(keys):
            raise RubricError(f"Duplicate question keys: {keys}")
        for q in self.questions:
            q.validate()
        if not any(q.type == "score" for q in self.questions):
            raise RubricError("A rubric needs at least one Score question for relevance")
        self.answerability.validate()
        if self.answerability.type != "noul":
            raise RubricError("The answerability question must be a Noul")
        object.__setattr__(self, "_hash", hashlib.sha256(self.canonical().encode()).hexdigest())

    @property
    def hash(self) -> str:
        return self._hash

    def canonical(self) -> str:
        body = {
            "rubric_id": self.rubric_id,
            "version": self.version,
            "task": self.task,
            "questions": [asdict(q) for q in self.questions],
            "answerability": asdict(self.answerability),
        }
        return json.dumps(body, sort_keys=True, ensure_ascii=False)

    def wire_questions(self) -> dict[str, dict]:
        return {q.key: q.wire() for q in self.questions}

    def critical_keys(self) -> list[str]:
        return [q.key for q in self.questions if q.critical]

    def unit_score(self, scores: dict[str, float]) -> float:
        """Weighted mean of Score answers, each scaled to 0..1 by its number of levels."""
        total = weight = 0.0
        for q in self.questions:
            if q.type != "score":
                continue
            if q.key not in scores:
                raise RubricError(f"Missing Score answer '{q.key}'")
            top = len(q.criteria) - 1
            total += q.weight * (scores[q.key] / top)
            weight += q.weight
        return total / weight

    @classmethod
    def from_dict(cls, data: dict) -> "Rubric":
        return cls(
            rubric_id=data["rubric_id"],
            version=int(data["version"]),
            task=data["task"],
            questions=tuple(Question(**q) for q in data["questions"]),
            answerability=Question(**data["answerability"]),
            notes=data.get("notes", ""),
        )

    @classmethod
    def load(cls, path: Path) -> "Rubric":
        return cls.from_dict(json.loads(Path(path).read_text(encoding="utf-8")))


def for_question(qid: str, question: str, fact: str, topic: str, version: int = 1) -> Rubric:
    """Build the fixed four-part rubric from per-question wording: the fact asked for and its topic."""
    return Rubric(
        rubric_id=qid,
        version=version,
        task=question,
        questions=(
            Question("relevance", "score", f"How directly does this passage help answer: {question}", [
                "Unrelated to the question.",
                f"Shares words or names with the question but says nothing about {topic}.",
                f"About {topic}, but does not touch {fact}.",
                f"Gives part of {fact}, or strong clues to it.",
                f"States {fact} plainly.",
            ]),
            Question("contains_fact", "noul", f"Does this passage itself state {fact}?", critical=True),
            Question("evidence_form", "choice", "How does this passage present anything about the question?", {
                "narration": "The narrator states it.",
                "dialogue": "A character says it.",
                "document": "A letter, note, card or printed text shows it.",
                "none": "Nothing about the question appears.",
            }),
        ),
        answerability=Question("answerable", "noul", f"Taken together, do these passages give enough to answer: {question}"),
    )
