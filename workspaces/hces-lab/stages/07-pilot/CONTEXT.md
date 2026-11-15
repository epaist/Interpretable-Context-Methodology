# Stage 07: Pilot on Workspace-Builder

Test whether the HCES gate can replace hand-written Section/Scope in a real ICM workspace without hurting the stage's work.

## Inputs

| Source | File/Location | Section/Scope | Why |
|--------|--------------|---------------|-----|
| Plan | `../05-end-to-end/output/pilot-plan.md` | Full file | Design, bars, cost |
| Next-level plan | `../05-end-to-end/output/next-level-plan.md` | "Design" | How the gate sits in ICM layers |
| Frozen cutoffs | `../04-exam/output/cutoffs.json` | Full file | Gate settings, unchanged |
| Domains | `references/domains.md` | Full file | The two user workflow descriptions |
| Target workspace | `../../../workspace-builder/` | Every stage CONTEXT.md and the files its Inputs table names | The workspace under test |

## Process

1. Build `hces.gate` (Inputs table, sections, JEV, frozen cutoffs) and `hces.pilot`; unit tests pass.
2. Run `python -m hces.pilot --judge --yes`: JEV judges every reference section for all 10 tasks.
3. Run `--estimate` and state the Claude and JEV cost.
4. **[Checkpoint]** Present the estimate and the gate's kept sections; wait for go.
5. Run `--run --yes --cap 10`, then `--grade --yes`, then `--report`.
6. Run the audit, write findings into `output/pilot.md`, update core-design.md and the design page.

## Checkpoints

| After Step | Agent Presents | Human Decides |
|------------|---------------|---------------|
| 4 | Cost estimate and kept sections per task | Go, change, or stop |

## Audit

| Check | Pass Condition |
|-------|---------------|
| Quality | gate passes at least as many audit checks as hand, summed over the 10 tasks |
| No regressions | No task where gate fails a code check that hand passes |
| Context | gate's median reference tokens below hand's |
| Blind | Grader prompt never carries the arm |
| Spend | Claude spend within the $10 cap |

## Outputs

| Artifact | Location | Format |
|----------|----------|--------|
| Stage runs | `output/runs/<domain>/<stage>/<arm>.md` | Raw stage output, file blocks |
| Answers and grades | `output/answers.jsonl`, `output/grades.jsonl` | One row per run and per grade |
| Report | `output/pilot.md` | Arms table, per-task table, audit, findings |
