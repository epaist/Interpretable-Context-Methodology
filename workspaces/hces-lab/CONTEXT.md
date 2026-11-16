# HCES Lab: Task Routing

Six test stages, bottom of the hierarchy first: large plain-text volumes now, structured instruction files in stage 05, memory in stage 06 (Phase 4).

## Task Routing

| Task Type | Go To | Description |
|-----------|-------|-------------|
| Setup | `stages/01-setup-smoke/CONTEXT.md` | Design the core from scratch, build it with unit tests, one JEV call |
| Test material | `stages/02-test-material/CONTEXT.md` | Three volumes, questions, gold passages, needles, unanswerables |
| Pipeline v0 | `stages/03-pipeline-v0/CONTEXT.md` | RAG only, RAG + JEV, JEV on everything, on one volume |
| Exam | `stages/04-exam/CONTEXT.md` | Tune on two volumes, test on the third, rotate, freeze, confirm |
| End to end | `stages/05-end-to-end/CONTEXT.md` | Claude answers per arm vs full context; add CLAUDE.md-style files |
| Memory stream | `stages/06-memory-stream/CONTEXT.md` | Replay Quillmere Broadband records in date order, phases A to C |
| Workspace pilot | `stages/07-pilot/CONTEXT.md` | Gate vs hand scope vs whole files on workspace-builder |

## Shared Resources

| Resource | Location | Contains |
|----------|----------|----------|
| Constants | `shared/constants.md` | Model, store, embedder, budget, candidate counts |
| Timings | `shared/timings.md` | What access, analysis and response mean and how to log them |
| Arms | `shared/arms.md` | The three arms and the retrieval variants |
| Knowledge base | `kb/CONTEXT.md` | Volumes, passage IDs, indexes |
| Code | `../../hces/README.md` | Module layout; each stage builds the modules it needs |

## Plan Documents

Full plan: https://claude.ai/artifact/BThLrQVoNKKJSWZka7qQ5K
Stage visual: https://claude.ai/artifact/DGWUaNc8T6L8W5mrCyRU45
Roadmap: https://claude.ai/artifact/CWPi1juPwKLgvcLFKxYRM8
