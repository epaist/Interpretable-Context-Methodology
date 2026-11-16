# Stage 04 Audit

Exam on three volumes (109k, 256k and 462k tokens), both shapes, budget 6000, retrieval hybrid k 50, judge jev-1.14.0. Frozen cutoffs: keep at score 0.75, no unsure band, critical at fact p 0.9. Numbers come from rotation.md, scorecard.md, confirm.md, noise.md and rubric2.md.

## Audit Checks

| Check | Result | Evidence |
|-------|--------|----------|
| No leakage | PASS | Each test volume was scored with cutoffs tuned on the other two (rotation.md). Fresh questions are tagged and left out of tuning |
| Frozen | PASS | confirm.md uses 0.75, 0.75, 0.9 from cutoffs.json, unchanged |
| Rubric variance | REPORTED | Second rubric: mean kept-set overlap 0.872, lowest 0.250, 11 of 20 identical, 20 of 20 same gold outcome. Run-to-run noise: 0.981, lowest 0.500, 47 of 50 identical, 44 of 44 same gold outcome |
| Bars | DONE | Every bar below is marked pass or fail with its number |
| Timings | DONE | Median and slowest 10% per arm and volume in scorecard.md, summarized below |

## Bars

| Bar | Target | Measured | Result |
|-----|--------|----------|--------|
| Needle catch, RAG + JEV, pooled exam | 100% | 100% (rotation test sets and scorecard) | PASS |
| Gold catch, RAG + JEV | At least 95% | 97% pooled test (130 of 134); 99% with frozen cutoffs | PASS |
| RAG + JEV vs RAG only | Clearly higher | Gold 99% vs 89%, needles 100% vs 90%, misses 2 vs 15, lookalikes kept 9 vs 15, median context 474 vs 5,946 tokens | PASS |
| Budget | Every task within 6000 | Highest kept set 5,992 tokens (JEV on everything); RAG + JEV highest 5,966 | PASS |
| End-to-end answers | No worse than full context | Not measured; stage 05 | NOT RUN |
| Answerability, exam unanswerables | Flag them | 100% flagged, 0% of answerable questions wrongly flagged | PASS |
| Answerability, fresh unanswerables | Flag them | 1 of 6 runs flagged; 12 of 12 answerable runs right | FAIL |
| Answerability, holdout unanswerables | Flag them | 12 of 12 runs flagged (all 36 unanswerable runs: 32 flagged) | PASS |

## Speed Bars (proposed in stage 03)

| Bar | Proposal | Measured | Result |
|-----|---------|----------|--------|
| Access (retrieval), p95 | 50 ms | 31 ms | PASS |
| Analysis, RAG + JEV at k 50, p95 | 2 s | 0.97 s | PASS |
| Analysis, JEV on everything | 10 s per 100k tokens | 5.0, 4.6 and 4.5 s per 100k tokens | PASS |
| Response | 50 ms | 4.4 ms highest | PASS |
| Peak memory, query path | 300 MB | 214 MB | PASS |
| Cost per question, RAG + JEV at k 50 | $0.005 | $0.0020 | PASS |

## Timings (ms per question per shape, access + analysis + response)

| Volume | Arm | Median | Slowest 10% |
|--------|-----|--------|-------------|
| secret-adversary | rag | 11 | 17 |
| secret-adversary | rag+jev | 894 | 966 |
| secret-adversary | jev-all | 5,481 | 5,772 |
| moonstone | rag | 13 | 17 |
| moonstone | rag+jev | 884 | 950 |
| moonstone | jev-all | 11,713 | 12,673 |
| way-we-live-now | rag | 17 | 22 |
| way-we-live-now | rag+jev | 872 | 971 |
| way-we-live-now | jev-all | 20,589 | 21,939 |

RAG + JEV time stays flat with volume size because it judges a fixed 50 candidates. JEV on everything grows linearly with the volume.

## Findings

- Every RAG + JEV miss is a retrieval miss: moonstone q05 has no gold passage in the top 50, in either shape. JEV on everything keeps it.
- Fresh unanswerables fail. JEV rates off-topic passages as holding the fact (0.97 for a passage about Tommy in Kent on the school question), so the kept set looks answerable. The exam unanswerables were all flagged; a likely cause of the gap (not yet tested) is that fresh unanswerables ask about details close to real passages, so JEV finds a near match.
- Rubric wording moves kept sets more than run-to-run noise does (0.872 vs 0.981), but no gold outcome changed in 20 cases.

## Answerability Follow-up (Bee chose: keep JEV, fix answerability)

- 6 holdout unanswerable questions (2 per book) were written before any probing and judged in full ($0.37).
- Holdout: 12 of 12 runs flagged "not in the documents". In every one, nothing cleared the cutoff, so the kept set was empty.
- Across all 36 unanswerable runs (exam, fresh, holdout), 32 are flagged, and 0 of 144 answerable runs are wrongly flagged. Only 5 unanswerable runs keep any passage, and 4 of those slip through. The "1 of 6" fresh result was the hardest slice, not the typical case.
- Three stricter JEV checks were probed on every kept set ($0.04): quote-level per passage, quote-level for the whole set, and a stated / hinted / other choice. None separates the 4 misses from answerable runs. Catching them needs a threshold that wrongly refuses 4% to 15% of answerable runs (strict per passage below 0.8: 35 of 36 flagged, 6 of 144 wrongly flagged).
- Decision: keep the current answerability rule. The weak spot sits upstream, where the relevance judge scores an off-topic passage high (0.97 for Tommy in Kent on the school question). Stage 05 measures whether the answering model still says "not in the documents" from such a kept set.
- Details: answer-probe.md.

## Caveats

- k 50 was chosen from secret-adversary results only.
- The moonstone and way-we-live-now gold review (key v2) happened after the first rotation run. It applies to every arm equally.
- The end-to-end answers bar waits for stage 05.

## Spend

JEV judging and checks this stage: $5.79 (judging $4.58, noise $0.64, second rubric $0.57), plus answerability calls of about $0.03. Answerability follow-up: holdout judging $0.37, probe $0.04. Stage total $6.23.
