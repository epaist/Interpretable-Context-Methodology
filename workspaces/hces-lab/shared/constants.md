# Constants

Canonical values for every stage and for the code in `hces/`. Change a value here once; the code parses this table directly, so there is no second copy.

| Name | Value | Why |
|------|-------|-----|
| JEV model | jev-1.14.0 | Pinned so cutoffs stay valid |
| Vector store | sqlite-vec plus SQLite FTS5 | One local file, no server |
| Embedder | bge-small-en-v1.5 (via fastembed, CPU) | Runs locally; small enough that the GPU is not needed |
| Token budget | 6000 | Context size handed to Claude per task |
| Candidate sweep | 20, 50, 100 | Retrieval candidate counts tested in stage 03 |
| Python | .venv\Scripts\python.exe (uv, Python 3.12) | Command used to run `hces/` |
| Judge workers | 6 | Parallel JEV requests |
| Results store | `hces/data/results.db` | Insert-only SQLite |
| JEV state cap | 32k tokens per question, 64k per request | Split larger states |
| JEV price | $0.042 per million input tokens, output free | Cost estimates |

## Starting Bars (from the plan)

| Measure | Bar |
|---------|-----|
| Needle catch, RAG + JEV | 100% on the pooled exam |
| Gold catch, RAG + JEV | At least 95% |
| RAG + JEV vs RAG only | Clearly higher, or drop JEV from this step |
| Budget | Every task within budget |
| End-to-end answers | No worse than full context |
| Speed | Measured always, bars set after stage 03 |

## Memory Stream Bars (stage 06)

| Measure | Bar |
|---------|-----|
| Current fact correct | At least 95% |
| Superseded fact returned as current | Never |
| Wrongly merged facts | None |
