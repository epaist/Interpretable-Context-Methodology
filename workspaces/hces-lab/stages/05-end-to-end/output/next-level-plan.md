# Next-Level Plan: HCES Gating ICM Layers 3 and 4

How to put the gate into a real ICM workspace, based on the stage 05 results.

## What the results allow

| Result | Source | Consequence |
|--------|--------|-------------|
| Gated answers match the whole book (70/73 vs 69/73) at 1/15 the cost | `end-to-end.md` | Gating reference material (layer 4) is safe |
| Gated answers match all instruction files (23/24 vs 24/24, gap is grading) at 1/36 the tokens | `instructions/end-to-end.md` | Gating reference files (layer 3) is safe |
| Frozen cutoffs worked on markdown with no retuning | `instructions/retrieval.md` | One cutoff set for both layers |
| RAG+JEV kept nothing for 12/12 holdout and 6/6 instruction unanswerables | stage 04 audit, `instructions/retrieval.md` | An empty kept set is a reliable "not in the documents" |
| The answerer abstained on every unanswerable, even with off-topic passages | both end-to-end runs | Keep the answerer as the last abstention check |

## Design

1. **Layers 0 to 2 stay whole.** Root CLAUDE.md, the workspace CLAUDE.md and the current stage CONTEXT.md are routing. They are small, always needed, and loaded as today. No gate.
2. **Layer 3 (reference files) is gated by section.** Cut every file named in the stage's Inputs table into sections with `hces.sections`. At stage start, the stage task is the query; RAG takes the top 50 sections, JEV scores them with the frozen rubric, code fills up to 2000 tokens.
3. **Layer 4 (working material, kb, volumes) is gated by passage.** Same pipeline as stage 04, budget 6000 tokens, per question or per sub-task.
4. **Empty set means stop.** If the gate keeps nothing, the agent says the material does not cover it instead of loading files whole.
5. **Index on change.** Rebuild a file's sections and embeddings when its hash changes; JEV verdicts are cached by (section hash, query).

## Rollout

| Step | Work | Pass condition |
|------|------|----------------|
| 1 | Add a `gate` command to hces that takes a stage folder and a task, reads its Inputs table, and prints the kept sections | Runs on hces-lab stage 05 and keeps the gold sections for its own task |
| 2 | Pilot on one real workspace (workspace-builder) with 10 tasks, gated vs whole Inputs | Output quality no worse on blind grading; tokens and time reported |
| 3 | Fix the grader: give it the full corpus to check extra claims, so true details are not marked partial | q13 and q23 regrade correct; no other grade moves |
| 4 | Recheck moonstone n05 (abstained in both arms) | Question or gold fixed, or dropped with a note |
| 5 | Optional: local judge (Qwen on llama.cpp) next to JEV on the stage 04 exam | Same pass rate at the frozen cutoffs, or JEV stays |

## Costs to expect

JEV per gated call is under a cent at 50 candidates ($0.17 for 30 instruction questions). Claude per answer falls by the token ratio (15x to 36x here). The pilot in step 2 should cost under $3 in Claude and under $1 in JEV; estimate before running.

## Risks

- Tasks that need a whole file (a template to copy) must bypass the gate. Mark those Inputs rows "Full file" and load them whole, as the Inputs table already says.
- Very short files gain nothing from gating; skip files under the budget.
- Cutoffs were tested on two corpora only. Recheck them on the pilot before wider use.
