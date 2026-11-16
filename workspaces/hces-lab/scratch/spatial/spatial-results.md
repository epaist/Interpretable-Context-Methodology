# Spatial Vector Layer: Results (2026-11-09)

Question: does placing passages "in space" make retrieval over very large, verbose text faster or cheaper without losing the answer?

Data: the three books (146 answerable question x shape runs, stage 02 key v2) and the 1911 Britannica (210,592 passages, 40 answerable questions from voice stage 07). Same bge-small vectors as the live indexes; questions embedded on the PC with `hces.embed.FastEmbedder`. All timings are CPU in the cloud sandbox (4 cores), one query at a time.

## Verdict

Do not route by space. Every form of partitioning tested lost gold passages before it saved meaningful time. The real win is simpler: keep the vectors as one flat float32 matrix in RAM and scan it with numpy. Same results as sqlite-vec, 27 times faster.

## 1. Placing passages by text position (chapter, neighbours)

Each passage vector blended with its chapter centre and/or its neighbours; also a "region" re-rank that boosts passages whose neighbours score well.

| Corpus | Flat gold@20 | Best blend gold@20 | Region gold@20 |
|--------|--------------|--------------------|----------------|
| Books | 0.72 | 0.71 | 0.69 |
| Britannica | 0.93 | 0.93 | 0.95 (gold@50 equal) |

No gain; neighbour blending hurts needles (one planted passage gets averaged into its neighbours). Dropped.

## 2. Placing passages by meaning (cells, `hces/spatial.py`)

Spherical k-means cells, passages stored contiguously by cell as int8 codes, query opens the nearest `nprobe` cells and re-scores the best 200+ with float32.

Britannica, 1,835 cells (about 111 passages each), top 150:

| Path | Median ms | Same as exact @150 | Gold@20 | Gold@50 | Gold@150 |
|------|-----------|--------------------|---------|---------|----------|
| sqlite-vec flat (what `retrieve.Index` does) | 184.4 | 1.000 | 0.925 | 0.975 | 0.975 |
| numpy flat float32, in RAM | 6.7 | 1.000 | 0.925 | 0.975 | 0.975 |
| spatial nprobe 16 | 0.9 | 0.679 | 0.775 | 0.775 | 0.775 |
| spatial nprobe 32 | 1.6 | 0.800 | 0.825 | 0.825 | 0.825 |
| spatial nprobe 128 | 3.9 | 0.957 | 0.900 | 0.925 | 0.925 |

With 459 bigger cells, nprobe 64 (14% of the data scanned) still lost 2 of 40 at 10 ms, slower than the flat scan.

Books (all under 3 ms either way, k 50):

| Path | Gold@10 | Gold@50 |
|------|---------|---------|
| sqlite-vec vector (current) | 0.58 | 0.80 |
| spatial nprobe 8 | 0.47 | 0.64 |
| hybrid sqlite-vec + FTS (current) | 0.78 | 0.99 |
| hybrid flat numpy + FTS | 0.78 | 0.99 |

Gold loss is much steeper than overall overlap with exact search. Detail questions ("the wall creeper's range") have gold passages that sit far from the question in vector space, so any routing step, by article summary (stage 07 summary-first, 8 of 40 lost) or by meaning (this test), cuts exactly those. Keyword search is what rescues them, not geometry.

## 3. What is cheap, measured

- **Search speed:** flat numpy matrix, 6.7 ms at 210k passages vs 184 ms for sqlite-vec on the same machine, identical top 150. No GPU needed. Linear, so roughly 30 ms at 1M passages and 300 ms at 10M (estimate, not measured). Cells only pay off past a few million passages, and then only with keyword search alongside.
- **Memory:** int8 codes are 77 MB for Britannica vs 308 MB float32, if RAM ever binds.
- **Judge cost:** on Britannica, vector gold@50 equals gold@150 (39 of 40). Sending JEV 50 candidates instead of 150 would cut the judge bill by about two thirds for the same recall on this set. Needs a check with hybrid search and the books before changing.

## Files

- `src/hces/spatial.py` (new, nothing existing changed) and `src/hces/tests/test_spatial.py` (3 pass)
- `spatial/` bench scripts: `exp1.py` (test 1), `bench_eb.py`, `bench_eb2.py`, `bench_books.py`, `data.py`, `embed_queries.py`

## 4. Follow-up (2026-11-14, Bran chose "swap it, then check JEV k 50")

**Swap done on the PC.** `hces/retrieve.py`: sqlite-vec stays the store; `Index.vector_search` now scans a normalised numpy copy of the vectors, loaded on the first search and dropped on `build()`. Returns the same `(unit_id, cosine distance)` pairs. Two new tests in `tests/test_retrieve.py` (matches sqlite-vec MATCH; rebuild refreshes the matrix). Full suite on the PC: 126 passed.

| Index | Same top 150 set as sqlite-vec | sqlite-vec | numpy | First-search load |
|-------|-------------------------------|------------|-------|-------------------|
| Britannica, PC (`eb1911.db`) | 48 of 48 questions | 366 ms | 7.3 ms | 13.0 s |
| Six book indexes, sandbox | all 182 question x index runs | 0.8 to 1.9 ms | 0.13 to 0.27 ms | 15 to 180 ms |

Order differs only where two distances are within 1e-6 (float rounding or exact ties): 11 of 230 lists swap two neighbours somewhere below rank 35, never changing membership.

Catch: the first search on a big index pays the load (13 s for Britannica out of SQLite). Anything live, like the voice bot, should call a search at launch, as stage 07 already does for the GPU copy.

**JEV candidate count, hybrid search.** Per-passage judgments do not depend on k, so "gold kept at k" for Britannica = stage 07's stored flat result (k 150) with gold also in the top k. My hybrid rebuild matched stage 07's gold-in-candidates on 40 of 40.

| Corpus | k 20 | k 50 | k 100 | k 150 |
|--------|------|------|-------|-------|
| Britannica, gold kept by JEV (of 40) | 37 | 37 | 37 | 37 |
| Books, gold in candidates (146 runs) | 0.870 | 0.973 | 1.000 | 1.000 |

- Britannica: the deepest gold sits at rank 10, so even k 20 loses nothing; unanswerables cannot get worse with fewer candidates.
- Books: k 50 drops 4 runs: moonstone/n07 (needle, rank 51 and 52) and way-we-live-now/q17 (rank 67 and 69). Novels bury needles deeper than encyclopedia lookups.

Recommendation: k 100 as the one default. Britannica's JEV bill falls by a third (150 to 100) with no loss on either corpus. k 50 would save two thirds on Britannica but loses 2 book questions; I would not tune k per corpus on 40 questions.
