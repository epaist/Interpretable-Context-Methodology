# Stage 03 Audit: Secret Adversary

| Check | Result |
|-------|--------|
| All arms ran | Pass. RAG only 300 runs, RAG + JEV 300, JEV on everything 50, judge pass 50; every question has every arm, variant, shape and k |
| Budget | Pass. Largest context 6,000 tokens (RAG only at the limit); JEV arms median under 1,100 |
| Manifests | Pass with a limit. 25 manifests show kept and cut with scores for RAG + JEV at k 50 and JEV on everything; cut passages under 0.25 in the JEV-on-everything arm are counted, not listed. Every decision for every run is in `results.db` (50,926 rows) |
| Timings | Pass. Every run row has access, analysis and response plus peak memory |
| Retrieval misses | Pass. Counted per variant and k in `rag-only.json` and the run report |
| Embedder bake-off | Pass. Lowest cosine, throughput and peak memory for both engines in `embedder-bakeoff.md` |
| JEV failures | 0 of 16,925 judge requests; 0 answerability failures |

## Found by the audit

- **The answer key is too narrow for some real-text questions.** For q10 (how the pair planned to earn money), passage c002/p0010 ("a joint venture... Young Adventurers, Ltd.") also answers it, but only c002/p0011 is marked gold. JEV on everything scored strong non-gold passages (fact p 0.8 or more, score 0.85 or more) for 9 of 12 answerable real-text questions, e.g. q12 (Albert is named in 11 more passages) and q04 (the cousin link is repeated 7 times). Needles had none: the needle numbers are clean.
- **Analysis time for JEV arms is derived.** The judge pass judged every passage once; each arm's analysis time is that pass's time scaled to its candidate count, plus its own fill and answerability time. Noted in every run's notes.
- **Arm costs are attributed, not extra spend.** Actual JEV spend for the stage was $0.64 for judging plus under $0.05 for 192 answerability calls (estimated: `JevJudge.answerable` does not yet record billed tokens; fix before stage 04).
