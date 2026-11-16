# Stage 01: Core Design, Build and Smoke Test

Design the HCES core from scratch, build its first modules in `hces/` with unit tests, and confirm one JEV call works with timings.

## Inputs

| Source | File/Location | Section/Scope | Why |
|--------|--------------|---------------|-----|
| Constants | `../../shared/constants.md` | Full file | Model, store, embedder |
| Timings | `../../shared/timings.md` | Full file | What to log |
| HTES ideas | `references/htes-ideas.md` | Full file | The idea to keep; HTES code is reference only |
| Code layout | `../../../../hces/README.md` | Full file | Modules, which stage builds each |

## Process

1. Check prerequisites: Python, the TypeSafe SDK, the JEV key in the environment, GPU visible. List anything missing and stop.
2. Write the core design: the data model (unit, rubric, judgment, run), the judge interface (JEV first, a local judge later behind the same interface), the store schema, and how scores roll up the hierarchy.
3. **[Checkpoint]** Present the design and wait for OK. No code before this.
4. Build the stage 01 modules from `hces/README.md` (config, store, timing, judge, rubric) with unit tests.
5. Set up the vector store and keyword index with a 3-passage toy volume.
6. **[Checkpoint]** State the JEV cost of the smoke call (fractions of a cent) and wait for OK.
7. Run one JEV relevance question on one toy passage; log the three timings.
8. Run the audit, then write the smoke report.

## Checkpoints

| After Step | Agent Presents | Human Decides |
|------------|---------------|---------------|
| 1 | Missing prerequisites, if any | Install or change plan |
| 3 | Core design | Approve, change, or redesign |
| 6 | Smoke call cost | Go or stop |

## Audit

| Check | Pass Condition |
|-------|---------------|
| From scratch | No HTES file copied or ported into `hces/` |
| Unit tests | All pass |
| JEV call | Answer stored with model ID and tokens |
| Timings | access, analysis, response all logged |
| Insert-only | No UPDATE or DELETE on result tables |
| No em dashes | None in new files |

## Outputs

| Artifact | Location | Format |
|----------|----------|--------|
| Core design | `output/core-design.md` | Data model, judge interface, store schema, rollup rules |
| Smoke report | `output/smoke-report.md` | JEV answer, model, tokens, cost, three timings, test results |
| Code | `../../../../hces/` | Python package with tests |
