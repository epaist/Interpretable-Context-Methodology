# Stage 03: Pipeline v0, Three Arms

Run RAG only, RAG + JEV and JEV on everything on one volume, with retrieval variants, and show what each kept and cut.

## Inputs

| Source | File/Location | Section/Scope | Why |
|--------|--------------|---------------|-----|
| Constants | `../../shared/constants.md` | Full file | Budget, sweep, store |
| Arms | `../../shared/arms.md` | Full file | What each arm does |
| Timings | `../../shared/timings.md` | Full file | What to log |
| Answer key | `../02-test-material/output/answer-key.jsonl` | Smallest volume only | Questions and gold |
| Rubric guide | `references/rubric-guide.md` | Full file | How Claude writes the per-task rubric |

## Process

1. Build vector and keyword indexes for the smallest volume, both shapes; log `index_build` and peak memory.
   Embedder bake-off: in WSL Ubuntu, embed the same passages with fastembed and fasttextembed; compare cosine per passage, throughput and peak memory.
2. For each question, Claude writes a rubric (relevance scores, metadata tags, answerability question).
3. Run RAG only for vector and hybrid at each candidate count.
4. Run RAG + JEV on the same candidates: score, tag, judge answerability, roll up in code, fill the budget.
5. Run JEV on everything for the same questions.
6. **[Checkpoint]** State the JEV cost before steps 4 and 5 and wait for OK.
7. Write per-question manifests: kept, cut, scores, why.
8. Run the audit, then write the run report.

## Checkpoints

| After Step | Agent Presents | Human Decides |
|------------|---------------|---------------|
| 2 | Three sample rubrics | Approve rubric style |
| 6 | JEV cost estimate | Go or stop |

## Audit

| Check | Pass Condition |
|-------|---------------|
| All arms ran | Every question has results for every arm and variant |
| Budget | No context over budget |
| Manifests | Every kept and cut passage listed with its score |
| Timings | Three timings on every run |
| Retrieval misses | Counted per variant and k |
| Embedder bake-off | Lowest cosine, throughput and peak memory reported for both engines |

## Outputs

| Artifact | Location | Format |
|----------|----------|--------|
| Manifests | `output/manifests/<question-id>.md` | Per arm: kept, cut, scores, answerability |
| Run report | `output/run-report.md` | Catch rates, misses, budget use, cost, timings |
| Speed bars proposal | `output/speed-bars.md` | Proposed bars from these numbers |
| Embedder bake-off | `output/embedder-bakeoff.md` | Both engines side by side; switch only if every cosine is at least 0.9998 and memory drops |
| Rubrics | `output/rubrics/<slug>.jsonl` | One versioned, hashed rubric per question; `<slug>-targets.jsonl` holds the per-question wording |
| Raw logs | `output/index-builds.jsonl`, `output/rag-only.json`, `output/judge-progress.log` | One line per build, run summary, one line per judged question |
| Audit | `output/audit.md` | Every audit check with its result |
