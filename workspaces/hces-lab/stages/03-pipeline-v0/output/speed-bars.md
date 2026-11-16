# Speed Bars Proposal

From the stage 03 runs on Secret Adversary (109k tokens; 332 to 345 passages per shape), on the PC (i9-14900K, Windows). These are proposals for stage 04, not pass marks yet.

## Measured

| Step | Measured | Notes |
|------|---------|-------|
| Embedder load | 1.9 to 2.4 s | Once per process |
| Index build, one shape | 28 s, 253 MB peak | 12 passages/s at batch 1 |
| Retrieval, vector or hybrid | 11 ms median | Query embedding included |
| JEV judging, 6 workers | about 61 passages/s; 5.5 s for a whole shape | 900 tokens per request, 0 failures in 16,925 |
| Answerability call | 98 ms median, 126 ms p90 | One call per distinct kept set |
| Budget fill and rollup | under 1 ms | |
| Peak memory, judging and arms | 69 MB | Embedder not loaded |
| Peak memory, retrieval runs | 212 MB | Embedder loaded |

## Proposed Bars

| Bar | Proposal | Why |
|-----|---------|-----|
| Access (retrieval) | 50 ms at p95 | 4 times the measured median, room for larger volumes |
| Analysis, RAG + JEV at k 50 | 2 s at p95 | Measured 0.9 s median; JEV time grows linearly with k |
| Analysis, JEV on everything | 10 s per 100k tokens of source | Measured 5.5 s for 109k tokens; it is the ceiling arm, not the product path |
| Response | 50 ms | Measured 3 to 8 ms |
| Peak memory, query path | 300 MB | 212 MB measured with the embedder loaded |
| Peak memory, index build | 400 MB | 253 MB measured at batch 1; batch 64 hit 2 GB, which this bar would catch |
| Cost per question, RAG + JEV at k 50 | $0.005 | Measured about $0.002 |
