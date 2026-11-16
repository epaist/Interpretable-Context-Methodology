# HCES Lab

Builds and tests the ICM + HCES context system: RAG retrieval finds candidate passages, JEV scores them against a rubric, and code fills a token budget before anything reaches Claude.

## Folder Map

```
hces-lab/
├── CLAUDE.md          (you are here)
├── CONTEXT.md         (start here for task routing)
├── setup/             (onboarding questionnaire)
├── shared/            (constants, timing rules, the test arms)
├── kb/                (knowledge base: volumes and their indexes)
└── stages/
    ├── 01-setup-smoke/    (design and build the core, unit tests, one JEV call)
    ├── 02-test-material/  (volumes, questions, gold passages, needles)
    ├── 03-pipeline-v0/    (three arms run end to end on one volume)
    ├── 04-exam/           (rotated exam with frozen cutoffs)
    ├── 05-end-to-end/     (Claude answers from each arm, then move up the hierarchy)
    ├── 06-memory-stream/  (Phase 4: self-learning memory on a dated company stream)
    └── 07-pilot/          (the gate on workspace-builder: whole vs hand scope vs gate)
```

Code lives in `D:\0001_LOCAL_RAG\hces\` (shared, so later workspaces can use the gate). Stage files describe work; they do not hold code.

## Triggers

| Keyword | Action |
|---------|--------|
| `setup` | Run `setup/questionnaire.md`, fill `shared/constants.md` |
| `status` | Scan `stages/*/output/`; a stage with files other than .gitkeep is COMPLETE, else PENDING |

## Routing

| Task | Go To |
|------|-------|
| Set up and smoke test | `stages/01-setup-smoke/CONTEXT.md` |
| Build test material | `stages/02-test-material/CONTEXT.md` |
| Run the three arms | `stages/03-pipeline-v0/CONTEXT.md` |
| Run the exam | `stages/04-exam/CONTEXT.md` |
| Compare answers, go up the hierarchy | `stages/05-end-to-end/CONTEXT.md` |
| Test self-learning memory | `stages/06-memory-stream/CONTEXT.md` |
| Pilot the gate on a real workspace | `stages/07-pilot/CONTEXT.md` |

## What to Load

| Task | Load These | Do NOT Load |
|------|-----------|-------------|
| Setup | `shared/constants.md`, `shared/timings.md`, stage 01 references | `kb/volumes/`, other stages |
| Test material | `shared/constants.md`, `kb/CONTEXT.md`, stage 02 references | `hces/` code, stages 03 to 05 |
| Pipeline v0 | `shared/*`, `kb/CONTEXT.md`, stage 02 output, stage 03 references | stage 01 references |
| Exam | `shared/*`, stage 02 and 03 output, stage 04 references | raw volume text |
| End to end | `shared/*`, stage 04 output | stage 01 to 03 references |
| Memory stream | `shared/constants.md`, `shared/timings.md`, `kb/CONTEXT.md`, stage 04 cutoffs, stage 06 references | `kb/volumes/`, stage 01 to 05 references |

Never load a whole volume or stream into context. They are read by code, not by the agent.

## Stage Handoffs

Each stage writes to its own `output/`. The next stage reads from there. Edit an output and the next stage uses your edit. Every stage stops for the user's go before the next one starts.

## Standing Rules

- Recall first: when unsure, keep the passage.
- Log access, analysis and response time on every run (`shared/timings.md`).
- Test texts are public domain only. Private files need a privacy check before going to JEV's cloud.
- State the JEV cost estimate before any batch run.
- After every run, update `stages/01-setup-smoke/output/core-design.md` and `core-design.html` with the real results, rubrics in use, metrics, and any design change the run forced.
- No em dashes in any file.
