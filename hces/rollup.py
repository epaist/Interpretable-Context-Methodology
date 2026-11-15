"""Code-owned rollup and budget fill. JEV answers; this module decides.

Order of keeping: critical units first (contains_fact likely yes), then units at or above the
cutoff by score, then the unsure band if room is left. Ties go to retrieval rank. Units are
kept whole; a unit that does not fit is skipped and smaller ones after it may still fit.
"""

from __future__ import annotations

from dataclasses import dataclass

CUTOFF = 0.60  # provisional; stage 04 searches for it
UNSURE_LOW = 0.50
CRITICAL_AT = 0.50


@dataclass(frozen=True)
class Scored:
    unit_id: str
    tokens: int
    score: float  # 0..1 from the rubric's Score answers
    critical_p: float  # contains_fact yes-probability
    rank: int  # retrieval rank, 1 = best
    failed: bool = False


@dataclass(frozen=True)
class Cutoffs:
    cutoff: float = CUTOFF
    unsure_low: float = UNSURE_LOW
    critical_at: float = CRITICAL_AT


DEFAULT = Cutoffs()


def tier(u: Scored, c: Cutoffs = DEFAULT) -> int:
    if u.failed:
        return 0  # a unit the judge could not answer is kept like an unsure one: errs toward recall
    if u.critical_p >= c.critical_at:
        return 3
    if u.score >= c.cutoff:
        return 2
    if u.score >= c.unsure_low:
        return 1
    return -1


def fill(units: list[Scored], budget: int, c: Cutoffs = DEFAULT) -> tuple[list[tuple[Scored, str]], list[tuple[Scored, str]]]:
    """Returns (kept, cut), each with a reason."""
    order = sorted(units, key=lambda u: (-tier(u, c), -u.score, u.rank))
    kept, cut, used = [], [], 0
    names = {3: "critical", 2: "above cutoff", 1: "unsure band", 0: "judge failed, kept for recall"}
    for u in order:
        t = tier(u, c)
        if t < 0:
            cut.append((u, f"score {u.score:.2f} below {c.unsure_low:.2f}"))
        elif used + u.tokens > budget:
            cut.append((u, f"{names[t]}, no room in budget"))
        else:
            kept.append((u, names[t]))
            used += u.tokens
    return kept, cut
