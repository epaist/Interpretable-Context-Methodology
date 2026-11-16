# Instruction Files: End to End

Opus 5.5 answers from the gated sections (RAG + JEV, frozen cutoffs, 6000 tokens) and from all files. Blind grading as in end-to-end.md.

| Arm | Answerable score | Correct | Partial | Wrong | Abstained on answerable | Unanswerable abstained | Median ms | Slowest 10% ms | Median input tokens | Cost |
|-----|------------------|---------|---------|-------|-------------------------|------------------------|-----------|----------------|---------------------|------|
| gated | 23 of 24 (96%) | 22 | 2 | 0 | 0 | 6 of 6 | 1533 | 1972 | 1042 | $0.24 |
| all-files | 24 of 24 (100%) | 24 | 0 | 0 | 0 | 6 of 6 | 1812 | 2274 | 37486 | $0.46 |

## Where the arms disagree

| Question | Gated | All files | Gated answer | All-files answer |
|----------|-------|-----------|--------------|------------------|
| instructions/q13 | partial | correct | A needle is one of the "Short invented passages, written in the volume's style, inserted between real passages," and "Each needle is the only place it | A needle is a "short invented passage, written in the volume's style, inserted between real passages," and "each needle is the only place its question |
| instructions/q23 | partial | correct | Em dashes are banned throughout: the conventions say "No em dashes anywhere in the repo" and HCES Lab says "No em dashes in any file," with the Stage  | `_core/CONVENTIONS.md` says "No em dashes anywhere in the repo," and the HCES Lab repeats "No em dashes in any file." The workspace-builder validation |

Answering $0.70, grading $0.28.

## Audit

| Check | Result | Evidence |
|-------|--------|----------|
| Blind | Pass | Grader prompt holds the question, gold sections and one answer; the code raises if a uid or arm label appears in it. Answers graded one at a time in shuffled order. |
| Bar | Strict miss, 23 of 24 vs 24 of 24 | Both gated partials (q13, q23) are grading asymmetry, not a retrieval miss. See below. No wrong answers and 6 of 6 abstentions in both arms. |
| Timings | Pass | Median 1533 ms gated vs 1812 ms all files; slowest 10% 1972 vs 2274 ms. |
| Cutoffs | Transferred unchanged | Frozen 0.75/0.75/0.9 from stage 04, tuned on novels, used as is on markdown instruction files. |

## Why q13 and q23 are partial

The grader sees only the gold sections. Both gated answers added one true detail from a section outside the gold set:

- q13: "about 10 needles per volume" is in `workspaces/hces-lab/stages/02-test-material/CONTEXT.md` line 21.
- q23: the Stage 01 "None in new files" check is in `stages/01-setup-smoke/CONTEXT.md` line 42, and "replace with --" is in `workspace-builder/stages/05-validation/CONTEXT.md` line 42.

The all-files answers made the same kind of extra claims and were graded correct. So the gap is grader variance on unsupported but true details. Taken strictly the bar is missed by one point; on substance the gate lost nothing.

## Findings

1. The section gate works on structured text with no retuning: every gold section was kept at both budgets, and the median kept set was 570 tokens.
2. Context per question fell from about 37,500 to about 1,000 input tokens (36x) with the same abstention record.
3. RAG alone kept something for every unanswerable question; RAG+JEV kept nothing for 6 of 6. The answerer still abstained correctly in both arms, so it stays the final check.
4. The grader needs the full corpus (or a fact check pass) to judge extra details fairly. Without it, the more context an answer draws from, the more it risks a "partial" for true claims.
