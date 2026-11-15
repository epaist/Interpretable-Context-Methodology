# Stage 04: The Exam

Tune cutoffs on two volumes, test on the third, rotate and pool, then freeze cutoffs and confirm on a fresh set.

## Inputs

| Source | File/Location | Section/Scope | Why |
|--------|--------------|---------------|-----|
| Constants | `../../shared/constants.md` | "Starting Bars" | Pass conditions |
| Arms | `../../shared/arms.md` | Full file | What is compared |
| Timings | `../../shared/timings.md` | "Rules" | Median and slowest 10% reporting |
| Answer key | `../02-test-material/output/answer-key.jsonl` | Full file | All three volumes |
| Stage 03 report | `../03-pipeline-v0/output/run-report.md` | Full file | Best variant and k to carry forward |
| Exam method | `references/exam-method.md` | Full file | Rotation and freezing rules |

## Process

1. Pick the retrieval variant and k from stage 03; write them down before any scoring.
2. **[Checkpoint]** State the JEV cost for all three volumes and wait for OK.
3. Run every question on every arm for all three volumes and both shapes.
4. Grid-search cutoffs on two volumes; apply them unchanged to the third. Rotate three times; pool.
5. Freeze the pooled cutoffs. Build a small fresh question set and confirm.
6. Rerun one volume with frozen cutoffs to measure run-to-run noise.
7. **[Checkpoint]** Remind the user about the second-rubric check, then for about 10 questions have Claude write a second rubric from the same prompt; rerun with frozen cutoffs and compare what is kept.
8. Run the audit, then write the scorecard.

## Checkpoints

| After Step | Agent Presents | Human Decides |
|------------|---------------|---------------|
| 2 | Cost estimate | Go or stop |
| 7 | Reminder: second rubric for about 10 questions, with its cost | Go or skip |
| 8 | Scorecard against the bars | Keep JEV, retune, or drop it from this step |

## Audit

| Check | Pass Condition |
|-------|---------------|
| No leakage | Cutoffs never tuned on the volume they are tested on |
| Frozen | Confirmation run uses the frozen cutoffs unchanged |
| Rubric variance | Kept-set overlap between first and second rubric reported next to run-to-run noise |
| Bars | Each bar marked pass or fail with its number |
| Timings | Median and slowest 10% per arm and volume size |

## Outputs

| Artifact | Location | Format |
|----------|----------|--------|
| Scorecard | `output/scorecard.md` | Per arm: needles, gold, misses, false keeps, answerability, budget, cost, timings |
| Frozen cutoffs | `output/cutoffs.json` | Cutoffs with rubric version and JEV model |
| HTML report | `output/report.html` | Same as scorecard, readable in a browser |
| Rotation | `output/rotation.md` | Per-rotation cutoffs, tune and test results, pooled result |
| Noise and rubric checks | `output/noise.md`, `output/rubric2.md` | Kept-set overlap, judge twice and second rubric |
| Confirmation | `output/confirm.md` | Fresh questions with frozen cutoffs and real answerability calls |
