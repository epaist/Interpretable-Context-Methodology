# Pilot Plan: The Gate on Workspace-Builder

Draft for Bee's go. Nothing here has run. Proposed home: a new stage `07-pilot` in hces-lab (stage 06 stays the memory stream).

## What the pilot can and cannot show

Workspace-builder's reference material is small. The Inputs files that are not upstream outputs total about 12,100 tokens across all five stages, and any one stage loads 1,800 to 5,900 of them. Most rows say "Full file", and stage 02 already scopes CONVENTIONS.md by hand to two patterns.

So token savings will be modest here (expect 30% to 60% of a 10k context, not 36x). The question the pilot really answers is whether the gate can replace the hand-written Section/Scope column without hurting the stage's output. That is the claim ICM needs before gating bigger workspaces.

## Design

| Item | Choice |
|------|--------|
| Domains | 2 made-up workflows with no private data (podcast episode production, small-grant application) |
| Tasks | Each domain runs stages 01 to 05 = 10 tasks |
| Arms | **whole**: every Inputs file whole. **hand**: Inputs as written in the Section/Scope column. **gate**: HCES picks sections, frozen cutoffs, 2000-token budget per task |
| What is gated | Reference rows (CONVENTIONS.md, placeholder-syntax.md, conventions-reference.md, the script-to-animation example). Templates load whole in every arm: they are copied, not consulted |
| Layers 0 to 2 | Workspace CLAUDE.md, CONTEXT.md and the stage CONTEXT.md load whole in every arm |
| Chaining | The whole arm's output for stage N is frozen and becomes the upstream input for all three arms at stage N+1, so arms differ only in reference context |
| Gate query | The stage's Process steps plus the domain description |
| Answerer | Opus 5.5, effort low, same instructions in all arms |
| Grader | Blind, one output at a time, shuffled. Gets the stage CONTEXT.md, its Audit table and **all** reference files (fixes the stage 05 asymmetry). Scores each Audit check pass/fail plus an overall 1 to 5 |
| Code checks | Line caps (CONTEXT.md under 80, references under 200), no em dashes, every placeholder covered: run by code, not the grader |

## Bars

| Bar | Pass condition |
|-----|----------------|
| Quality | gate passes at least as many Audit checks as hand, in total over the 10 tasks |
| No regressions | No task where gate fails a code check that hand passes |
| Context | gate's reference tokens below hand's on median |
| Blind | Grader prompt never carries the arm |

## Work

1. `hces.gate`: read a stage's Inputs table, resolve paths, cut sections, run RAG + JEV, print kept sections and tokens. Unit tests. No spend except one JEV smoke call.
2. Domain descriptions and the run script (`hces/pilot.py`, same `--estimate / --run --yes --cap / --grade / --report` shape as `endtoend.py`).
3. **[Checkpoint]** Real estimate from token counts, then go.
4. Run, grade, report, audit; update core-design.md and the design page.

## Cost estimate (before step 3 recounts)

| Part | Calls | Estimate |
|------|-------|----------|
| JEV gating | 10 tasks, about 70 sections each | under $0.10 |
| Opus answering | 30 (10 tasks x 3 arms), about 10k in and 5k out each | about $5 |
| Opus grading | 30, about 15k in and 1.5k out each | about $2.70 |
| Total | | about $8, cap $10 |

Output tokens drive the cost; stage 03 writes a whole workspace and may run 10k or more. Three domains instead of two would be about $12.

## Not in this pilot

The local judge (stage 05 step 5) and moonstone n05. Both stay open.
