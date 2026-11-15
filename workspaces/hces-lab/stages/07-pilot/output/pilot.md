# Pilot: The Gate on Workspace-Builder

Opus 5.5 runs each workspace-builder stage for two made-up domains. Arms differ only in reference files. Blind grading against each stage's audit plus a reference-rules check; the grader sees every reference file in full.

| Arm | Checks passed | Overall (mean of 5) | Median reference tokens | Median input tokens | Code-check fails | Dashes | Own calls | Cost |
|-----|---------------|---------------------|-------------------------|---------------------|------------------|--------|-----------|------|
| whole | 48 of 50 | 4.3 | 3,808 | 19,170 | 0 | 0 | 10 of 10 | $2.66 |
| gate | 45 of 50 | 4.3 | 1,321 | 18,271 | 0 | 17 | 10 of 10 | $2.44 |
| hand | 48 of 50 | 4.3 | 1,116 | 7,830 | 0 | 2 | 2 of 10 | $0.29 |
| gate-open | 47 of 50 | 4.3 | 1,321 | 17,360 | 0 | 16 | 4 of 10 | $1.02 |

## Per task

| Domain | Stage | Arm | Reference tokens | Checks | Overall | Failed checks | Same as |
|--------|-------|-----|------------------|--------|---------|---------------|---------|
| podcast-episode | 01-discovery | whole | 3,808 | 5 of 5 | 4 | none |  |
| podcast-episode | 01-discovery | gate | 1,987 | 4 of 5 | 4 | Reference rules |  |
| podcast-episode | 01-discovery | hand | 3,808 | 5 of 5 | 4 | none | whole |
| podcast-episode | 01-discovery | gate-open | 2,645 | 5 of 5 | 4 | none |  |
| podcast-episode | 02-mapping | whole | 4,747 | 5 of 5 | 4 | none |  |
| podcast-episode | 02-mapping | gate | 1,384 | 5 of 5 | 4 | none |  |
| podcast-episode | 02-mapping | hand | 385 | 5 of 5 | 4 | none |  |
| podcast-episode | 02-mapping | gate-open | 1,384 | 5 of 5 | 4 | none | gate |
| podcast-episode | 03-scaffolding | whole | 1,116 | 7 of 7 | 5 | none |  |
| podcast-episode | 03-scaffolding | gate | 762 | 6 of 7 | 4 | Contract fidelity |  |
| podcast-episode | 03-scaffolding | hand | 1,116 | 7 of 7 | 5 | none | whole |
| podcast-episode | 03-scaffolding | gate-open | 762 | 6 of 7 | 4 | Contract fidelity | gate |
| podcast-episode | 04-questionnaire-design | whole | 1,116 | 5 of 5 | 5 | none |  |
| podcast-episode | 04-questionnaire-design | gate | 1,053 | 5 of 5 | 5 | none |  |
| podcast-episode | 04-questionnaire-design | hand | 1,116 | 5 of 5 | 5 | none | whole |
| podcast-episode | 04-questionnaire-design | gate-open | 1,053 | 5 of 5 | 5 | none | gate |
| podcast-episode | 05-validation | whole | 5,863 | 3 of 3 | 4 | none |  |
| podcast-episode | 05-validation | gate | 1,911 | 2 of 3 | 4 | Call accuracy |  |
| podcast-episode | 05-validation | hand | 5,863 | 3 of 3 | 4 | none | whole |
| podcast-episode | 05-validation | gate-open | 2,724 | 2 of 3 | 4 | Call accuracy |  |
| small-grant | 01-discovery | whole | 3,808 | 5 of 5 | 4 | none |  |
| small-grant | 01-discovery | gate | 1,987 | 4 of 5 | 4 | Reference rules |  |
| small-grant | 01-discovery | hand | 3,808 | 5 of 5 | 4 | none | whole |
| small-grant | 01-discovery | gate-open | 2,645 | 5 of 5 | 4 | none |  |
| small-grant | 02-mapping | whole | 4,747 | 5 of 5 | 4 | none |  |
| small-grant | 02-mapping | gate | 1,258 | 5 of 5 | 5 | none |  |
| small-grant | 02-mapping | hand | 385 | 5 of 5 | 4 | none |  |
| small-grant | 02-mapping | gate-open | 1,258 | 5 of 5 | 5 | none | gate |
| small-grant | 03-scaffolding | whole | 1,116 | 7 of 7 | 5 | none |  |
| small-grant | 03-scaffolding | gate | 447 | 7 of 7 | 4 | none |  |
| small-grant | 03-scaffolding | hand | 1,116 | 7 of 7 | 5 | none | whole |
| small-grant | 03-scaffolding | gate-open | 447 | 7 of 7 | 4 | none | gate |
| small-grant | 04-questionnaire-design | whole | 1,116 | 4 of 5 | 4 | Defaults present |  |
| small-grant | 04-questionnaire-design | gate | 1,053 | 5 of 5 | 5 | none |  |
| small-grant | 04-questionnaire-design | hand | 1,116 | 4 of 5 | 4 | Defaults present | whole |
| small-grant | 04-questionnaire-design | gate-open | 1,053 | 5 of 5 | 5 | none | gate |
| small-grant | 05-validation | whole | 5,863 | 2 of 3 | 4 | Call accuracy |  |
| small-grant | 05-validation | gate | 1,911 | 2 of 3 | 4 | Call accuracy |  |
| small-grant | 05-validation | hand | 5,863 | 2 of 3 | 4 | Call accuracy | whole |
| small-grant | 05-validation | gate-open | 2,944 | 2 of 3 | 4 | Call accuracy |  |

Answering $6.41, grading $2.89.

Hand equals whole on 8 of 10 tasks (only stage 02 scopes a reference file), so hand reuses whole's output and grade there; its median input tokens cover its 2 own calls only. JEV gating cost $0.013. First run total $7.86 of the $10 cap.

## Audit (first run: gate at 2000 tokens)

| Check | Result | Evidence |
|-------|--------|----------|
| Quality | FAIL, gate 45 of 50 vs hand 48 of 50 | Two of the three lost checks trace to one budget cut (below) |
| No regressions | Pass | No output over a line cap and no malformed placeholder in any arm (a placeholder regex false positive was fixed before this table) |
| Context | FAIL as written, median 1,321 vs 1,116 | Hand is whole on 8 of 10 tasks; in total gate loads 13,753 reference tokens vs hand's 24,576 (44% less) |
| Blind | Pass | Grader prompt holds no arm label; code raises if one appears |
| Spend | Pass | $5.39 answering, $2.45 grading, $0.01 JEV |

## Why the gate lost checks

Every relevant section the gate dropped on a failed task was cut by the 2000-token budget, not by the cutoffs:

- Stage 01, both domains: `conventions-reference.md#s02-3` (66 tokens, critical at 0.93 and 0.94) was cut with "no room in budget" at 1,987 tokens used. That one chunk holds "conditional blocks (whole sections only)" and "no em dashes". The two stage 01 failures are exactly those rules: small-grant wrapped a table row in a conditional, podcast used en dashes.
- Stage 05: Pattern 1 (Stage Contracts, critical 0.86 to 0.88) and in small-grant Pattern 4 were cut for room.
- The other two gate misses (podcast stage 03 contract fidelity, podcast stage 05 call accuracy) match misses whole also had on other tasks (small-grant stage 05 call accuracy, small-grant stage 04 defaults). Read as grader and run noise.
- Dashes: 15 of gate's 17 are in podcast stage 03, where neither arm's context holds a dash rule; whole had 0. Run variance, not the gate. The one stage 01 dash follows the dropped rule.

## Findings

1. Rule-following stages need many sections, not one fact. A 2000-token budget that suited question answering binds here and drops short critical rule lists.
2. The frozen cutoffs alone would have kept the missing sections: about 2,650 of 3,808 tokens on stage 01 and 2,700 to 2,950 of 5,863 on stage 05 (30% to 50% less than whole).
3. The hand-scoped stage 02 (385 tokens) passed every check in both domains. Where an author scopes, hand scoping is cheaper and as good.
4. Giving the grader every reference file worked: each gate miss traces to a named rule the grader could see.
5. Design change: layer 3 gating should use cutoffs with no token budget (or never cut a critical section for room), and short global rule lists (quality rules) should load with layers 0 to 2.

## Rerun: gate-open (frozen cutoffs, no token budget)

Bee approved a rerun at a $3 cap. gate-open keeps every section at or above the cutoffs, with no token budget. Its kept set differs from gate only on stages 01 and 05 (4 tasks); the other 6 reuse gate's output and grade.

| Check | Result | Evidence |
|-------|--------|----------|
| Quality | Strict FAIL by one check, gate-open 47 of 50 vs hand 48 of 50 | Stage 01 now passes 5 of 5 in both domains (the two rule failures are gone). Stage 05 call accuracy failed in both domains; whole failed the same check in one domain |
| No regressions | Pass | No cap or placeholder failures |
| Context | Median 1,321 vs 1,116 as written; total 16,915 vs hand 24,576 reference tokens (31% less, 49% less than whole) | Hand is whole on 8 of 10 tasks |
| Blind | Pass | Same grader and checks |
| Spend | Pass | Rerun $1.44; pilot total $9.30 of $10.86 |

Stage 01 dashes went from 1 to 0 with the "no em dashes" rule back in context. The remaining gap is one stage 05 "call accuracy" judgment, a subjective check that whole also failed once: within run and grader noise at this sample size.

## Conclusion

1. The budget was the cause: removing it recovered both rule-traced failures, at 2,645 to 2,944 reference tokens instead of 3,808 to 5,863.
2. For layer 3, gate with the frozen cutoffs and no token budget. Keep the token budget for layer 4 facts.
3. Where an author already scopes by heading (stage 02), keep the hand scope; it was cheapest and passed every check.
4. Ten tasks cannot separate a one-check gap from noise. A larger pilot or repeat runs would be needed to call gate-open equal to hand.
