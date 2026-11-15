# HTES Ideas (reference only)

HCES is built from scratch. HTES supplied the idea, not the architecture: no HTES file is ported, copied or used as a template. Its code can be read to see how a problem was solved before, nothing more.

HTES lives in Google Drive, folder "01-HTES-HIERARCHICAL TRANSLATION EVALUATION SYSTEM" (owner's private Drive)

## The Idea HCES Keeps

| Idea | What it means for HCES |
|------|------------------------|
| Judge, do not generate | A cheap model answers fixed, typed questions about each piece of text. It never writes the context. |
| Code decides | Every keep, cut, rollup and budget choice is made by code from the judge's answers, so it can be tested and repeated. |
| Rubric from the task | The questions come from what the current task needs, and each rubric is versioned with its results. |
| Hierarchy | Small units are judged and their scores roll up to their parents (passage to chapter to volume; section to file). |
| Recall first | When unsure, keep. A random sample of cuts is re-checked. |
| Every decision on record | Results are never overwritten, and each kept or cut piece can be traced to the answers behind it. |
| Proof by planted needles | Measure on text where the right answer is known; tune on some sets, test on others, then freeze. |

## What HCES Does Not Inherit

- HTES file layout, scripts, runner, worker pool or database schema.
- Translation-specific state, rubrics and cutoffs.
- Any HTES cutoff value. Cutoffs are set fresh in stage 04.

## Lessons From HTES Phase 1 (2026-10-14)

- Cutoffs are fragile: one that looked safe failed on the next fresh set. Expect the same for relevance.
- Agreement between runs of one model is not confirmation; use a second judge or planted needles.
- HTES had no unit tests. HCES writes tests with every module.
