# Stage 01 Smoke Report

Run `20261101-060830-dce13ab0`, 2026-11-01, on the PC (`.venv`, Python 3.12.10).

## The JEV Call

| Item | Value |
|------|-------|
| Task | Why does the lighthouse keeper leave the island? |
| Passage judged | `toy/p3` (ranked first by hybrid search) |
| Rubric | smoke-relevance v1, one Score question with 4 levels (0 to 3) |
| Model requested / answered | jev-1.14.0 / jev-1.14.0 |
| Answer | Expected level 3.0 of 3 ("Directly answers the task"), confidence 1.0 |
| Unit score | 1.0 |
| Input tokens (billed) | 380 |
| Cost | $0.000016 |

## Timings and Memory

| Span | ms | What it covered |
|------|----|-----------------|
| access | 1,816.6 | Loading the embedder (cold), opening the toy index, hybrid search |
| analysis | 1,664.6 | One JEV request over the network |
| response | 4.9 | Writing judgments and the decision |
| peak memory | 237.1 MB | Whole run, mostly the embedder |

Toy index build (separate run): 1,710 ms, 231 MB peak, 3 passages.

## Audit

| Check | Result |
|-------|--------|
| Unit tests | Pass: 41 of 41 |
| JEV call | Pass: answer stored with model ID and 380 tokens |
| Timings | Pass: access, analysis, response all logged |
| Insert-only | Pass: a DELETE on judgments was refused by the database |
| No em dashes | Pass: none in `hces/` |

## Findings

1. **The cost estimate was 3.4 times too low.** Estimated 113 tokens, billed 380. The estimate counts the state and questions at 4 characters per token; JEV adds its own overhead per request. Before any stage 03 batch, calibrate the estimator on a few real calls so the cost checkpoint never under-reports.
2. **Access time is mostly loading the embedder.** About 1.7 s of the 1.8 s is model load, paid once per process. Stage 03 keeps one embedder loaded across questions, so per-question access time should drop to milliseconds. The bake-off measures this for both engines.
3. **One JEV request took 1.7 s.** With 6 parallel workers, 50 candidates per question is about 9 rounds, roughly 15 s per question before batching. Stage 03 should test whether several passages can share one request.
