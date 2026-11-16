# Stage 05: End to End, Then Up the Hierarchy

Check that answers built from the gated context hold up, then bring in structured instruction files.

## Inputs

| Source | File/Location | Section/Scope | Why |
|--------|--------------|---------------|-----|
| Constants | `../../shared/constants.md` | Full file | Budget, bars |
| Timings | `../../shared/timings.md` | Full file | Response time per arm |
| Scorecard | `../04-exam/output/scorecard.md` | Full file | Which arm won |
| Frozen cutoffs | `../04-exam/output/cutoffs.json` | Full file | Settings to use |
| Answer key | `../02-test-material/output/answer-key.jsonl` | Answerable questions | Questions to answer |

## Process

1. Claude answers each question from the winning arm's context and from full context (split if over the limit).
2. Shuffle and blind the answers; grade them against the gold passages.
3. **[Checkpoint]** Present the blind comparison.
4. Add instruction files (CLAUDE.md, CONTEXT.md, stage files from `_core/` and a real workspace) as a second test set; score sections by heading instead of retrieving passages.
5. Optional: run a local judge (Qwen on llama.cpp, or a JEV-style open model) next to JEV on the same questions.
6. Run the audit, then write the report and the next-level plan.

## Checkpoints

| After Step | Agent Presents | Human Decides |
|------------|---------------|---------------|
| 3 | Blind answer comparison | Continue up the hierarchy or fix first |

## Audit

| Check | Pass Condition |
|-------|---------------|
| Blind | Grader never sees which arm produced an answer |
| Bar | Gated answers no worse than full context |
| Timings | response time reported per arm |

## Outputs

| Artifact | Location | Format |
|----------|----------|--------|
| Comparison | `output/end-to-end.md` | Per question: grades, arm, cost, timings |
| Next-level plan | `output/next-level-plan.md` | How HCES gates ICM layer 3 and 4 in a real workspace |
