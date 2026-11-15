# HCES Core Design (stage 01 complete; updated after every run)

Built from scratch on the HTES idea: a cheap judge answers typed questions about each unit of text, and code makes every decision. No code is written until this design is approved.

## 1. Data Model

| Thing | Fields | Lives in |
|-------|--------|----------|
| Unit | `id`, `source` (volume or file), `level` (volume, chapter, passage; or file, heading, subheading), `parent_id`, `start_char`, `end_char`, `tokens`, `source_hash` | `kb/volumes/<slug>/passages.jsonl` (written once, never edited) |
| Rubric | `rubric_id`, `version`, `task` (the prompt), `questions` (list), `hash` | `results.db`, table `rubrics` |
| Question | `key`, `type` (Score, Noul or Choice), `instructions`, `criteria` or `options`, `weight`, `critical` (yes/no) | Inside its rubric |
| Run | `run_id`, `arm`, `variant`, `k`, `question_id`, `budget`, `judge_model`, `access_ms`, `analysis_ms`, `response_ms`, `peak_rss_mb`, `tokens_in`, `cost_usd`, `started_at` | `results.db`, table `runs` |
| Judgment | `run_id`, `unit_id`, `rubric_id`, `rubric_version`, `question_key`, `value`, `model`, `tokens_in`, `created_at` | `results.db`, table `judgments` |
| Decision | `run_id`, `unit_id`, `kept`, `final_score`, `rank`, `reason` | `results.db`, table `decisions`; also the manifest |

Units are the hierarchy. A passage's parent is its chapter, a chapter's parent is its volume. For structured files (stage 05) the same shape holds: heading sections nest under their parent heading and file.

## 2. Judge Interface

One interface, so a local judge can be added later without touching anything else:

```
judge(task, rubric, units) -> judgments
answerable(task, kept_units) -> probability
estimate_cost(task, rubric, units) -> dollars
model_id
```

JEV is the first implementation (`typesafe-sdk` on PyPI, `TypeSafeClient().system_one(state=..., questions=...)`).

- One request per unit: the state holds the task and the unit's text; the questions are the rubric's.
- Requests run in parallel (`Judge workers` in constants), and a failed request is retried, then recorded as failed. It is never silently skipped.
- Answerability is one extra request per task, with the kept evidence as state. Over 32k tokens, the evidence is split and the highest answer counts.
- Open to check in step 4: whether the SDK can judge several units in one request. If it can, batching cuts the number of calls, but the interface stays the same.

## 3. Rollup and Budget Fill (all in code)

1. **Unit score:** the weighted mean of its Score answers, scaled 0 to 1.
2. **Critical keep:** if a critical Noul question passes its cutoff, the unit is kept whatever its score (recall first).
3. **Parent score:** the highest child score, plus a count of children that passed. Used to report which chapters or files mattered, and to break ties (a passage from a strong chapter wins).
4. **Budget fill:** sort by critical keep, then score, then retrieval rank. Add whole units until the token budget is full. Never cut a unit in half.
5. **Unsure band:** units just under the cutoff are kept if budget remains.
6. **Not in the documents:** if no unit passes, or answerability is below its cutoff, the gate returns that reply instead of padding the context.

Cutoffs in stages 01 to 03 are provisional and stored with each run. Real ones are tuned and frozen in stage 04.

## 4. Store

- `hces/data/results.db` (SQLite). Tables: `rubrics`, `runs`, `judgments`, `decisions`.
- Insert-only is enforced by the database itself: triggers abort any UPDATE or DELETE. A unit test proves it.
- A rerun gets a new `run_id`; nothing is overwritten.

## 5. Indexes

- One file per volume: `kb/index/<slug>.db`, holding a sqlite-vec table (bge-small vectors, 384 dimensions) and an FTS5 keyword table.
- Hybrid search merges the two ranked lists by reciprocal rank fusion. It is simple, has no weights to tune, and is well understood.
- Index build time is logged as `index_build`.

## 6. Config and Timing

- `config.py` parses the table in `shared/constants.md` and stops with a clear error on a missing value.
- `timing.py` gives three spans (access, analysis, response) on `perf_counter_ns`, plus peak memory (`peak_rss_mb`), written to the run row.
- The embedder sits behind its own small interface (`embed(texts) -> vectors`, `model_id`), like the judge, so a leaner engine can replace fastembed without touching the rest.
- Passages are cut at 512 tokens or fewer, because bge-small reads no further than that; longer text would be silently cut off.

## 7. Setup on the PC

- A project environment at `D:\0001_LOCAL_RAG\.venv`, made with uv on Python 3.12 (already gitignored).
- Packages: `typesafe-sdk`, `sqlite-vec`, `fastembed`, `psutil`, `pytest`. Nothing else for stage 01.
- `TYPESAFE_API_KEY` is already set in your user environment.

## What Is Not Decided Here

Retrieval variant and k (stage 03), cutoffs (stage 04), the memory store (stage 06).

## Results So Far (measured on the PC)

| Date | Run | Result |
|------|-----|--------|
| 2026-11-01 | Unit tests, all stage 01 modules | 41 passed in 2.5 s |
| 2026-11-01 | Toy index, 3 passages, fastembed bge-small | 1,710 ms build (model load included), 231 MB peak |
| 2026-11-01 | Hybrid search on the toy task | Answering passage ranked first, after the tie fix below |
| 2026-11-01 | JEV smoke call, 1 passage, 1 question (run 20261101-060830-dce13ab0) | Level 3.0 of 3, confidence 1.0; 380 tokens billed, $0.000016; access 1,817 ms, analysis 1,665 ms, response 5 ms; 237 MB peak |
| 2026-11-01 | Stage 02 cut: three books, both shapes | Secret Adversary 109,231 tokens, 29 chapters, 344 chaptered / 327 plain passages; Moonstone 255,954, 60 chapters, 759 / 726; Way We Live Now 462,269, 100 chapters, 1,334 / 1,298. Median about 340 tokens, max 512 |
| 2026-11-01 | Stage 02 answer key build and audit | 76 questions (46 real, 9 of them unanswerable; 30 needles; 9 lookalike decoys), 0 audit failures; 42 s, 58 MB peak; identical output on Linux and Windows |
| 2026-11-01 | Unit tests after stage 02 | 53 passed in 3.4 s |
| 2026-11-01 | Stage 03 index build, Secret Adversary, both shapes (first try, batch 64) | 49 s and 38 s; 1,495 MB and 2,030 MB peak; 7 to 9 passages/s |
| 2026-11-01 | Same build after the batch fix (batch 1) | 28 s each; 243 MB and 253 MB peak; 12 passages/s; 2.3 MB per index file |
| 2026-11-01 | RAG only, 25 questions x 2 shapes x 2 variants x 3 k (300 runs) | Hybrid keeps a gold passage for 91% of answerable questions at k 50 or 100, vector 55% to 77%; hybrid catches all 10 needles, vector misses up to 4; q10 (low overlap) missed everywhere; 11 ms median retrieval, 212 MB peak |
| 2026-11-01 | Embedder bake-off in WSL (332 passages) | fastembed 14.2 passages/s, 285 MB; fasttextembed 5.9 passages/s, 249 MB; cosine median 0.947, lowest 0.880. Stay on fastembed |
| 2026-11-01 | JEV judge pass, 25 questions x every passage x 2 shapes | 16,925 requests, 0 failures, 15.2M tokens, $0.64; about 61 passages/s at 6 workers; 69 MB peak |
| 2026-11-01 | RAG + JEV, hybrid, k 100 | Gold kept 95%, needles 100%, unanswerable flagged 100%, wrongly flagged 0%; median context about 1,000 tokens (RAG only fills about 5,900); 1.7 s analysis |
| 2026-11-01 | JEV on everything | Gold kept 100% in both shapes, 1 decoy kept; 5.5 s per question per shape |
| 2026-11-01 | Unit tests after stage 03 | 61 passed in 3.9 s |
| 2026-11-01 | Gold review, answer key v2 (Secret Adversary) | 27 gold passages added to 6 questions, 2 lookalikes marked as decoys; audit 0 failures |
| 2026-11-01 | Stage 03 rescored against key v2 (stored decisions, no new JEV calls) | Gold kept at k 50: hybrid RAG only 100%, RAG + JEV 100%, JEV on everything 100%; vector RAG only 68% to 86%. Lookalikes kept: RAG + JEV keeps q12's "William" passage (chaptered) and q07's false accusation (plain); JEV on everything keeps both |
| 2026-11-01 | Unit tests after key v2 | 63 passed in 3.6 s |
| 2026-11-01 | Stage 04 index builds, Moonstone and Way We Live Now | 81 to 83 s per Moonstone shape, 262 MB peak, 9 passages/s |
| 2026-11-01 | JEV judge pass, Moonstone and Way We Live Now | 104,585 requests, 0 failures, $4.02 ($1.49 and $2.53); about 920 tokens per request |
| 2026-11-01 | Gold review, key v2 for Moonstone and Way We Live Now | 96 gold passages added to 19 questions, 5 lookalikes marked as decoys |
| 2026-11-01 | Cutoff rotation (tune on two books, test on the third) | Pooled test: gold caught 97% (130 of 134), needles 100%, gold share 0.69. Frozen cutoffs: keep at score 0.75, no unsure band, critical at fact p 0.9 |
| 2026-11-01 | Scorecard, exam questions, frozen cutoffs, k 50 | RAG + JEV gold 99%, needles 100%, unanswerable flagged 100%, wrongly flagged 0%, median 474 tokens, 0.9 s per question; RAG only gold 89%, needles 90%, 5,946 tokens |
| 2026-11-01 | Fresh confirmation set (9 questions written after the freeze) | Answerable 12 of 12 runs right; unanswerable flagged in 1 of 6 runs |
| 2026-11-01 | Run-to-run noise, Secret Adversary judged twice | Mean kept-set overlap 0.98, 47 of 50 identical, gold outcome identical in all 44 answerable cases; $0.62 |
| 2026-11-01 | Second rubric, 10 questions reworded, both shapes | Mean kept-set overlap 0.87 (noise 0.98), 11 of 20 identical, gold outcome identical in all 20; $0.57 |
| 2026-11-01 | Stage 04 audit | Bars: needles 100% pass, gold 97% pooled pass, RAG + JEV vs RAG only pass, budget pass (max 5,992), fresh unanswerables 1 of 6 FAIL, end-to-end not run (stage 05). Speed bars all pass. Stage spend $5.82 |
| 2026-11-02 | Answerability follow-up: 6 holdout unanswerables, 3 stricter JEV checks probed | Holdout 12 of 12 flagged (nothing kept). All 36 unanswerable runs: 32 flagged, 0 of 144 answerable wrongly flagged. No stricter check catches the 4 misses without wrongly refusing 4% or more; current rule kept. $0.41 |
| 2026-11-02 | Stage 05 end to end, Opus 5.5 answers from gated context vs the whole book, blind graded, 91 questions | Answerable 96% gated vs 95% full; unanswerable abstained 18 of 18 in both; 0 wrong gated vs 1 full. Answer time 1.7 s vs 2.8 s median (11.3 s slowest 10% full). Answering $0.86 vs $13.00. Bar PASS. $15.35 |
| 2026-11-02 | Instruction files cut into sections: 34 files, 201 sections, 32,807 tokens, 30 questions (24 answerable, 6 not) | Frozen cutoffs unchanged. Gold kept 24 of 24 by every arm at 2000 and 6000 tokens; RAG + JEV median 570 tokens; unanswerables kept nothing 6 of 6 (RAG only 0 of 6). JEV $0.17 |
| 2026-11-02 | Instruction files end to end, gated sections vs all files, blind graded | Answerable 23 of 24 gated (2 partial) vs 24 of 24; 0 wrong; abstained 6 of 6 in both. Median 1.5 s vs 1.8 s; 1,042 vs 37,486 input tokens. Both partials add true details from non-gold sections the grader could not see. Strict bar miss by one point. $0.98 |
| 2026-11-02 | Stage 07 pilot: workspace-builder stages 01 to 05, 2 made-up domains, arms whole / hand scope / gate (2000 tokens), blind graded with all references | Audit checks passed: whole 48 of 50, hand 48 of 50 (hand = whole on 8 of 10), gate 45 of 50. Quality bar FAIL. Gate loads 44% fewer reference tokens in total. Lost checks trace to the 2000 budget cutting critical rule sections (no em dashes, whole-section conditionals, Pattern 1), not to cutoffs. $7.86 |
| 2026-11-02 | Stage 07 rerun: gate-open (frozen cutoffs, no token budget) on the 4 tasks whose kept set changed | gate-open 47 of 50 vs hand 48 of 50: stage 01 back to 5 of 5 in both domains; remaining gap is one stage 05 call-accuracy judgment whole also failed once. 31% fewer reference tokens than hand in total, 49% fewer than whole. $1.44, pilot total $9.30 |
| 2026-11-02 | Voice stage 2: live gate + streamed spoken answer, 23 questions (20 answerable, 3 not); local voice pipeline and echo bot | Gate 0.83 s median (RAG 13 ms, JEV 813 ms; 50 JEV workers about 0.21 s warm). First sentence: Haiku 5.5 0.9 s, Opus 5.5 1.9 s. Answerable right: Opus 19 of 20, Haiku 18 of 20; unanswerable declined 3 of 3. Echo bot: transcript 0.16 s, first audio 0.53 s on fast turns. $0.26 |
| 2026-11-02 | Voice stage 3: talking to the books, 22 spoken questions; gate searches every source with generic rubric wording | Generic rubric kept gold 20 of 20; unanswerables kept nothing 14 of 18, Haiku declined the other 4. Gate 0.49 s for 150 candidates. First audio 3.6 s median on Claude turns, 1.05 s for instant refusals. No memory broke follow-ups. $0.42 |
| 2026-11-02 | Voice stage 4: eager gate, early Haiku, follow-up rewrite, filler, barge-in, corpus hotwords; 17 spoken questions | First sound 0.95 s median (bar under 1 s: PASS). First answer words about 3.0 s spoken (bar 2.5 s: FAIL; Haiku first token 1.5 s). Zero cut-offs on thinking pauses. Follow-up rewrite 12 of 12 offline; source boost added nothing. JEV keep-alive about $1 an hour idle. $0.25 |
| 2026-11-02 | Stage 06 phase A: Quillmere memory stream, 122 tickets and call logs replayed in date order, 57 dated questions asked at their date, blind graded | 50 of 57 correct (88%, bar 95% FAIL); 2 stale (both early claims); 4 wrong merges (FAIL); hot facts 6 of 6; stale-quote contradictions all held. 192 facts in 73 groups; answer 1.7 s median. Claude $2.34, JEV $0.08 |
| 2026-11-02 | Voice stage 5: free JEV keep-warm, rewrite only when no name is said, rewrite keeps named sources, attribution prompt, barge-in test, 18 spoken questions | Keep-warm: idle cost $0 (models.list rounds); first-question gate 3,968 ms to 468 ms with one $0.001 judge round at launch. Answer words to the voice 2.3 s median (about 2.6 s spoken, bar 2.5 s: still just over); Haiku first token 0.82 s. Barge-in: audio stops 0.40 s after speech starts (5 of 6). Rewrite tests 5 of 5. Mr. Brown attributed in 1 of 3, the gate still keeps the false accusation. $0.28, voice total $1.21 |
| 2026-11-02 | Voice stage 6: labelled story-order passages, shorter answers, small talk path, spoken numbers, bot-decided barge-in; Sonnet 5.5 answering live, 16 turns | Diagnosis: the Mr. Brown and royalty misses were answer misses (gate kept the reveal and 11 Emperor passages). 38 known questions with the new prompt: 14 correct vs 12, 0 wrong, 18 of 18 declined. Mr. Brown: Haiku wrong at low and medium effort, Sonnet right at the same speed (about 50x cost). Live: barge-in 0.70 s (7 of 9), mm-hm ignored 3 of 3, thanks answered with no gate, years spoken right, Mr. Brown right; answer words 2.2 s median. A gate after a 4-minute break took 14.8 s. $0.38, voice total $1.59 |
| 2026-11-02 | Stage 06 phase A reruns on stored facts: best-match grouping at link 0.5 (a2) and 0.9 (a3), 8 groups in notes | a2 51 of 57, 2 stale, 4 wrong merges; a3 50 of 57, 2 stale, 0 wrong merges but the support number split into two groups and answers hedged 3 times. $0.40 Claude each |
| 2026-11-02 | Stage 06 phase A run a4: canonical keys at extraction (extractor reuses or names a key), JEV checks the key | 51 of 57 (89%, bar fail); 2 stale (early claims); 2 wrong merges, both lookalikes the extractor put under one key. Fixed retention offer, price lock, Glide cap, support number. $1.61 Claude, JEV $0.004; phase A total $4.75 |
| 2026-11-06 | Stage 06 phase A on a local model at $0: Qwen3.5-9B on llama.cpp (native Windows, about 6 GB of GPU) grades, extracts (a5, a6) and answers | Local grader on the a4 Claude answers: 52 of 57, agrees with Claude grades 42 of 44. a5 fully local: 30 of 57, the 9B returned no facts for 61 of 122 records. a6 adds one prompt line (most records state one to four facts): 103 facts, 42 of 57 (74%), 2 stale, 4 wrong merges, 11 abstained. $0 Claude |
| 2026-11-06 | Stage 06 phase A local extraction tuning at $0: exact values plus a second pass for missed facts (a7), then extract without the held key list and name keys in a separate call (a8) | a7 41 of 57, 113 facts: no gain, because the held key list in the prompt halves what the 9B lists (8 vs 17 facts on 13 probe records). a8 139 facts, 48 of 57 (84%), 1 stale, 4 wrong merges, 5 abstained. Same local grader gives Claude extraction (a4) 52 of 57. $0 Claude |
| 2026-11-07 | Stage 06 phase B fully local at $0: 33 SOP and governance versions written by code, 67 tickets citing them written by the 9B, phases A and B replayed together (222 records), source rank, 58 questions | 47 of 58 (81%); stale citations 5 of 5, SOP-owned facts 23 of 27, ticket-only facts 11 of 13, document version in force 3 of 7. 3 stale, 4 wrong merges (worst: five SOP-04 facts under one key). 500 facts. JEV $0.02, Claude $0 |
| 2026-11-09 | Stage 06 phase B rerun (b2) with SOP reading fixed: version as a fact, numbered lines as label and value, keys with the source line in view, no two facts of one record under one key; merge count no longer counts a ticket citing a version | 52 of 58 (90%, up from 47); document version 7 of 7 (was 3), SOP-owned facts 26 of 27, stale citations 4 of 5, ticket-only facts 10 of 13. Wrong merges 1 (month-to-month vs contract terms; b1 recounted: 7). 4 stale. JEV $0.03, Claude $0 |
| 2026-11-09 | Stage 06 phase C fully local at $0: 15 staff announcements (Calder fiber announced for 03-15, then moved to 04-01), 21 meeting notes (20 changes decided ahead, one floated $46 Spark price that never ships), 24 newsletters, 40 off-topic chatter threads, written by the 9B; replayed on the phase B memory; rank SOP over announcement over ticket; a later notice that moves a start date wins | 53 of 58 (91%); early announcement 1 of 1, never valid 1 of 1, announced but not yet in force 9 of 10, SOP-owned 26 of 27, ticket-only 11 of 13. 1 stale (paperless credit), 1 wrong merge (month-to-month vs contract terms, unchanged). 5 of 100 records never passed the writing checks. JEV $0.04 total, Claude $0 |
| 2026-11-05 | Voice stage 7: 1911 Britannica (37,048 articles, 37.1M words, 210,592 passages), GPU index, GPU vector search, 40 random-article questions plus 8 unanswerables, flat vs summary-first | Index on GPU 1,503 passages/s (2 min 50 s; CPU would take about 5 h). Vector search 367 ms to 2 ms on the GPU via a hand-written ONNX graph, no installs; flat search 882 to 189 ms. Gate flat: gold in top 150 39 of 40, kept 37 of 40, unanswerables empty 8 of 8, 0.56 s median. Summary-first: kept 32 of 40, 0.29 s. Sonnet: 31 correct, 7 partial, 0 wrong, 2 abstained (the gate misses), 8 of 8 declined. Projected first audio 2.9 s median. $0.48, voice total $2.07 |
| 2026-11-15 | Voice stage 8: turn-taking by sound. 116 recorded turns (409 boundaries, 293 pauses), stock Smart Turn baseline, prosody cues, Smart Turn v3.2 fine-tuned on Bee's voice plus 20,000 public clips | Stock (the int8 file the bot loads) on held-out turns: 82%, 9 false cut-offs, 8 missed ends of 93. Tuned: 86%, 5 cut-offs, 8 missed ends; other speakers 93% before and after. Hand-measured prosody added about 1 point on top of Smart Turn. Training 2 min on the 4090 from the v3.2 weights converted out of Pipecat's ONNX file. Tuned model 109 ms per decision vs 75 ms stock. $0 |
| 2026-11-15 | Voice stage 8 live turn test: stock vs Bee-tuned Smart Turn, 22 alternating questions, both models scoring every silence (171 silences, 15 real endings) | Every silence: bee 87% right vs stock 82%, cut-offs on pauses 13 vs 20, missed endings 9 vs 10 of 15. Reply after a caught ending 384 ms bee vs 352 ms stock. Small sample. Both miss most endings, so the 2.5 s fallback stays. Recommend bee as default. $0 |

## Rubrics In Use

| Rubric | Task | Questions |
|--------|------|-----------|
| smoke-relevance v1 | Why does the lighthouse keeper leave the island? | relevance (Score, 4 levels from "Unrelated to the task" to "Directly answers the task") |
| per-question v1 (85 questions), v2 (10 reworded) | Each exam question | relevance (Score, 5 levels), contains_fact (Noul, critical), evidence_form (Choice), answerability (Noul) |
| memory-link v1 | New statement vs a stored statement (top 20 by embedding) | related (Score, 3 levels), same_attribute (Noul, critical, links at 0.5), same_value (Noul) |

## Design Changes Forced by Real Runs

- Search ties: two passages tied in the hybrid merge and the tie went to alphabetical order, ranking the wrong one first. Ties now go to the vector ranking.
- Keyword search uses the Porter stemmer, so word variants match.
- Unit records and the 512-token cap live in `hces/units.py`; token counts are approximate until stage 02 stores real ones.
- pytest's default temp folder is locked on this PC; tests use `hces/data/pytest-tmp` (gitignored) via `pytest.ini`.
- Cost estimate: 4 characters per token undercounted a real JEV request by 3.4 times (113 estimated, 380 billed). The estimator gets calibrated on real calls before any stage 03 batch.
- Access time is dominated by a cold embedder load (about 1.7 s). Stage 03 keeps one embedder loaded across questions.
- One JEV request took 1.7 s; batching several passages per request is tested in stage 03.
- Token counts are now real: bge-small's own tokenizer, special tokens included, so the 512 cap means what the embedder means.
- Gutenberg contents lists repeat every chapter heading; a heading followed by under 300 characters is treated as a contents entry or a group title, never a chapter.
- The Moonstone restarts chapter numbers in each narrative, so chapters get sequential IDs (c001 on) and keep group titles such as "SECOND PERIOD / THIRD NARRATIVE / CHAPTER II".
- Passage text is not stored in `passages.jsonl`; offsets point into `plain.txt` and `load_passages` attaches text. Halves the files on disk.
- Gold passages are stored as evidence quotes and resolved to IDs by code, so gold IDs follow any re-cut and exist for both shapes.
- Needles are planted into `plain.txt` before cutting, so they sit inside ordinary passages; nine decoys repeat a needle question's words without its answer.
- fastembed's memory grows with batch size times passage length: batch 64 peaked at 1,346 MB, batch 1 at 243 MB, same speed. `embed.py` uses batch 1.
- fasttextembed's tokenizer treats curly quotes and apostrophes differently, so its vectors differ on book text (fine on plain ASCII). Not adopted.
- With a 6000-token budget and passages near 340 tokens, RAG only keeps about 18 passages, so k above 20 only changes what is retrieved, not what is kept. k matters for the JEV arm.
- Judgments do not depend on k or variant, so the JEV run judges each passage once per question and every arm reuses those judgments.
- JEV keeps far less than the budget: median context about 1,000 tokens against about 5,900 for RAG only. The 6000 budget rarely binds once JEV is in the loop.
- JEV found answer-key gaps: strong non-gold passages for 9 of 12 answerable real-text questions (e.g. q10's plan is also in c002/p0010). Needles had none. Key v2 adds the passages that answer on their own; questions can now list `decoy_evidence` for real lookalikes, and a passage holding both counts as gold.
- `report.py` scores gold from the stored decisions against the current key, so a key fix rescores old runs for free.
- With the full gold set, "at least one gold passage kept" saturates at 100% for hybrid RAG and for JEV. JEV's measured gain on this book is a 6x smaller context and correct "not in the documents" flags, not recall. Stage 04 needs a stricter score (share of kept tokens that are gold, lookalikes kept).
- JEV rates lookalikes as holding the fact (Sir James accusing Julius, Tuppence calling Albert "William"). The second rubric at stage 04 should test this.
- Answerability calls record their billed tokens (`JevJudge.last_tokens`); the old estimate is gone.
- Gold kept saturates on a 100k-token book but not on bigger ones: on Moonstone and Way We Live Now hybrid RAG alone keeps gold for 82% to 85%, RAG + JEV for 96% to 100%. JEV's recall gain grows with volume size.
- Every RAG + JEV miss at the frozen cutoffs is a gold passage retrieval never put in the top 50; JEV never cut a retrieved gold passage. Retrieval k is the ceiling.
- Frozen cutoffs are stricter than the stage 03 guesses (0.75 not 0.60, no unsure band, critical at 0.9 not 0.5): median context falls from about 1,000 to 474 tokens with no recall loss.
- Answerability is the weak spot. More kept text makes JEV say "answerable", and it rates off-topic passages as holding a missing fact (0.97 for a passage about Tommy in Kent on "which school did Tommy attend"). Unanswerable flags on fresh questions: 1 of 6.
- Rubric wording moves kept sets more than run-to-run noise (overlap 0.87 vs 0.98, lowest 0.25), but in 20 of 20 cases the gold outcome held. Wording changes which borderline passages survive, not whether the answer does.
- Most unanswerables are caught by the cutoff, not the answerability question: nothing scores 0.75, so the kept set is empty. Misses happen only when the relevance judge rates an off-topic passage high; rewording the answerability question cannot undo that, so the fix belongs in relevance judging or in the stage 05 answerer.
- End to end, the answering model is the final answerability check: on the two fresh unanswerables where JEV kept off-topic passages, Opus 5.5 still said "not in the documents". The gate does not need to be perfect at answerability; it needs to not drop the gold passage.
- The cost guard adds a fixed answerability reserve to every projection, so one-question runs need a cap above about $0.35.
- Instruction files are cut by heading (levels 1 to 3, code fences ignored); a section over the cap splits at blank lines, then at line breaks. Each unit starts with its file path and heading trail so the judge knows where it sits.
- The frozen cutoffs carried from novels to markdown instruction files with no retuning: 100% gold kept, 36x less context.
- The grader sees only gold sections, so a true detail from elsewhere in the corpus reads as unsupported. It judged the same kind of extra claim partial in one arm and correct in the other. The grader needs the full corpus (or a separate fact check) before small bar gaps mean anything.
- Layer 3 (rules) is not layer 4 (facts): a stage task needs many rule sections, so the 2000-token budget dropped short critical rule lists. Layer 3 gating should use the cutoffs with no token budget (rerun confirmed: both rule failures recovered); short global rules (quality rules) belong with layers 0 to 2.
- Where a stage author already scopes a reference by heading, hand scoping is cheaper than the gate and as good (stage 02: 385 tokens, every check passed).
- Spoken questions name no source: the voice gate searches every source together and ranks the top 150 overall with generic rubric wording ("the answer to this question"). It still kept gold 20 of 20, so the gate stays source-agnostic, with no per-source rules.
- Rewrite beats source boost: rewriting a follow-up (he or she into the name) found the right passage 12 of 12 times. A recent-source boost added nothing on top, and aimed at the wrong source it lost gold (62 vs 72 of 73), so it is off.
- Gate speed is set by candidates, not library size: search over three books takes about 24 ms; JEV time depends on how many candidates it scores, falling from 0.81 s to 0.21 s with more parallel workers. A warm pool costs about $1 an hour while idle.
- Theories read as facts: the answer model stated a character's mistaken theory (Julius is Mr. Brown) as fact. The answer prompt must attribute claims to whoever makes them in the text.
- Memory linking cannot union every same_attribute link: chains joined price lock and contract terms to the stable month-to-month fact, and Glide's cap to Spark's. Next: join a new fact to its single best match.
- The reversion guard (an old value needs 2 records to come back) stopped every stale quote. It does not stop a record that states the next value early; that needs a source with authority (SOP effective dates, phase B) or a confirmation rule.
- Warm connections, not servers: what goes cold is the pool of 50 network connections (16 s to reopen; the SDK drops one after 30 s idle), not JEV's servers. A free models.list call down every connection every 20 s keeps it open; a tiny paid judge call keeps only one. The earlier "$1 an hour" was wrong: the old ping rounds cost $0.19 an hour, and the rest was eager gates on partial transcripts.
- Lookalike accusations survive the gate: for "Who is Mr. Brown?" the gate keeps Sir James's false accusation of Julius and not the passages that reveal Sir James. The attribution prompt fixed 1 of 3 answers; the rest needs a relevance or rubric fix, not a prompt fix.
- Answer misses are not gate misses: stage 06 traced both misses: the gate kept the Mr. Brown reveal (score 0.99) and 11 Emperor passages. The fix is in what the answerer sees: passages tagged with their source and position, in story order, with "a later reveal outweighs an earlier claim". Haiku 5.5 still misreads Mr. Brown at low and medium effort; Sonnet 5.5 reads it right at the same speed for about 50 times the cost. The gate and its cutoffs are unchanged.
- The judge path goes cold too: free connection rounds kept the 50 connections open, but after about 4 minutes with no real judge call the first gate still took 14.8 s. One tiny judge round after 2.5 minutes without a real one keeps it warm, about $0.03 an hour.
- No single same_attribute cutoff works for memory linking: JEV rates lookalikes (contract term vs month-to-month 0.85) above some true changes (price lock 12 vs 24 months 0.81). At 0.9 nothing merges wrongly but changes split. Next: a canonical key per fact at extraction, checked by JEV.
- Canonical keys beat JEV-only grouping for memory: one key per attribute, reused by the extractor, fixed every split and chain failure. JEV becomes a cheap check ($0.004 a run). The extractor still puts some lookalikes under one key, and the growing key list raised extraction cost by half.
- A local model grades and nearly extracts: Qwen3.5-9B on the home GPU grades as well as Claude (42 of 44 grades agree), so grading is free. As extractor it now scores 48 of 57 against 52 for Claude extraction under the same grader, at $0. What it took: tell it most records hold facts, ask a second time for what it missed, and keep the held key list out of the extraction prompt (name keys in a separate call), since the long list halves what it lists.
- Source rank works: with an SOP version in force, memory takes its value over anything a ticket says. All 5 tickets quoting an outdated SOP version were answered with the version in force, and early ticket claims no longer win. Reading SOPs needed three prompt rules for the 9B: list the document version as a fact, read each numbered line as label and value, and never key two facts of one record alike. With them, versions in force went from 3 of 7 to 7 of 7 and phase B from 47 to 52 of 58.
- Announcements and notices: a start date in the future keeps the old value until it arrives (9 of 10 asked in between were right), a delay notice moves the start (Calder answered with the old towns between the announced and the real date), and an idea floated in meeting notes never displaced the SOP price. The 9B had to be held to writing values as digits and names: it wrote "five dollars" and a delay notice that never named Calder until the text check required them.
- Search moves to the GPU at scale: on 210,592 passages the SQLite search, not JEV, became the slow part (vector 367 ms, keyword 514 ms). Holding all vectors in GPU memory (a hand-written ONNX Gemm plus TopK on onnxruntime-gpu) made vector search 2 ms with identical results, and skipping stop words and words in over 2% of passages cut keyword search. JEV time and cost stayed set by the 150 candidates, not the library.
- Thin summaries cannot route: summary-first search (title plus the start of each article, top 10 articles) halved gate time and cost but lost 8 of 40 questions whose detail is not in the article opening. Flat search stays the default until summaries carry more (section headings, key terms, or a short generated summary).
- Speaker-tuned turn-taking beats hand cues: Bee's finished turns end higher in pitch and hesitations sag, the reverse of the textbook falling end; hand-measured prosody (pitch slope, lengthening, decay) added about 1 point on top of stock Smart Turn, while fine-tuning Smart Turn on 316 of Bee's boundaries mixed with 20,000 public clips raised held-out accuracy from 82% to 86% and halved cut-offs, without losing accuracy on other speakers.
- Compare against the model actually deployed: the fine-tune started from Pipecat's full-precision gpu file (74% on Bee), but the bot loads the int8 cpu file (82%); the honest in-bot gain is 82 to 86%. Dynamic int8 quantisation of the tuned model made it slower (160 ms vs 109), not faster.
