# hces

Shared Python package for the ICM + HCES gate. Values come from `workspaces/hces-lab/shared/constants.md`; `config.py` parses that table at load, so there is no second copy of any value.

Run from the home root (`D:\0001_LOCAL_RAG`) as `.venv\Scripts\python.exe -m hces.<module>`. Tests run with `.venv\Scripts\python.exe -m pytest` (settings in `pytest.ini`; set `HCES_SKIP_SLOW=1` to skip the real-model test).

## How to Run (v1)

Setup once: Python 3.12, then `python -m venv .venv` and `.venv\Scripts\python.exe -m pip install -r hces/requirements.txt`. Set the JEV key (`TYPESAFE_API_KEY`) as a user environment variable. For the memory commands, start the local model: `tools\llama.cpp\llama-server.exe -m models\Qwen3.5-9B-Q4_K_M.gguf --port 11435 --alias qwen9b --n-gpu-layers 99 --ctx-size 16384 --parallel 1 --jinja --reasoning off` (about 6 GB of GPU). Without it, pass `--claude --yes` and set `ANTHROPIC_API_KEY`.

| Command | What it does | Cost |
|---------|--------------|------|
| `python -m hces gate <stage folder> --task "..." --out <stage>/output/gate-kept.md --yes` | Picks the reference sections a stage task needs (Pattern 16); the agent reads `gate-kept.md` instead of the whole files | JEV, under a cent per task; judgments are stored and reused |
| `python -m hces remember --store memory.sqlite --file note.md --date 2026-11-15 --yes` | Adds one dated record to a memory store (Pattern 17); prints the facts it found | JEV, about a tenth of a cent; local model free |
| `python -m hces recall --store memory.sqlite "question" --as-of 2026-11-15 --notes` | Answers from memory as of a date, with the notes it used | Local model free |

Record ids decide rank: `--id sop-02-v6` (or `gov-...`) marks an official document version, `--id ann-...` an announcement; anything else ranks as an ordinary record. Memory is insert-only: a correction is a new, later record.

## Module Layout

Built from scratch: HTES is the idea, not the template. Each module is created by the stage that first needs it, after stage 01's design checkpoint. Nothing is written ahead of its stage.

| Module | Job | Built in |
|--------|-----|----------|
| `__init__.py` | Package marker, version | Stage 01 |
| `config.py` | Reads the constants table; fails loudly on a missing or `{{...}}` value | Stage 01 |
| `store.py` | Insert-only SQLite results store (`data/results.db`), keyed by passage ID, source hash, parent ID | Stage 01 |
| `timing.py` | access, analysis, response and index_build spans with `perf_counter_ns` | Stage 01 |
| `judge.py` | Judge interface with a JEV implementation first: typed Score, Noul and Choice questions, 32k state split, cost estimate | Stage 01 |
| `units.py` | The Unit record, the 512-token passage cap, approximate token counts | Stage 01 |
| `embed.py` | Embedder interface; fastembed at batch 1 (fasttextembed lost the stage 03 bake-off) | Stage 01 |
| `rubric.py` | Versioned rubrics built from the task (weights, anchors, critical flags) | Stage 01 |
| `passages.py` | Strips Gutenberg text, finds chapters (skips contents lists, keeps PERIOD and NARRATIVE groups), packs whole paragraphs into passages of about 300 and at most 512 bge tokens, both shapes; `load_passages` and `locate` | Stage 02 |
| `planter.py` | The one needle planter: inserts needle and decoy paragraphs at paragraph breaks by book position | Stage 02 |
| `answer_key.py` | Rebuilds volumes with needles, turns evidence quotes into gold IDs for both shapes, audits, writes the key | Stage 02 |
| `retrieve.py` | Index build, vector search, FTS5 keyword search (Porter stemming), hybrid merge by reciprocal rank fusion | Stage 01 (toy index), Stage 03 (real volumes) |
| `build_index.py` | Builds one volume's index per shape; logs index_build time and peak memory | Stage 03 |
| `rag.py` | RAG-only arm over both shapes, vector and hybrid, every k; budget fill by rank | Stage 03 |
| `judge_all.py` | Judges every passage once per question (resumable, cost cap; `--repeat` for noise, `--second-rubric`); all arms reuse it | Stage 03 |
| `rollup.py` | Code-owned rollup and budget fill: critical, above cutoff, unsure band | Stage 03 |
| `arms.py` | Builds RAG + JEV and JEV-on-everything from stored judgments, asks answerability, writes manifests | Stage 03 |
| `manifest.py` | Kept/cut manifests with scores and reasons | Stage 03 |
| `gate.py` | The Pattern 16 entry point: retrieve, judge, roll up, write manifest | Stage 03 |
| `exam.py` | Rotation, cutoff grid search, frozen-cutoff confirmation, run-to-run noise | Stage 04 |
| `report.py` | Scorecard per arm, variant and k, with misses and timings (markdown now; HTML in stage 04) | Stage 03 |
| `exam.py` | Cutoff rotation (tune on two volumes, test on the third), freeze, run-to-run noise, second-rubric overlap, fresh-set confirmation | Stage 04 |
| `scorecard.py` | Every arm on all three volumes with the frozen cutoffs: gold, needles, lookalikes, answerability, tokens, timings, cost | Stage 04 |
| `smoke.py` | Stage 01 smoke test: toy index, cost estimate, one JEV call (needs `--yes`) | Stage 01 |
| `memory.py` | The memory store: extract, key, link, current value as of a date, source rank; the stage 06 replay and grading | Stage 06 |
| `stream.py` | The Quillmere test stream: ledger, record plans for phases A to C, questions, record writer | Stage 06 |
| `local_llm.py` | Claude-shaped client for a local llama.cpp server, so every step can run at no cost | Stage 06 |
| `gate.py`, `pilot.py` | The stage gate on an ICM stage's Inputs table, and the stage 07 pilot that measured it | Stage 07 |
| `__main__.py` | The v1 command: `gate`, `remember`, `recall` | v1 |
| `data/` | Local databases and indexes; `*.db` is gitignored | Stage 01 |
| `tests/` | One `test_<module>.py` per module, written with the module | Stage 01 onward |

## Rules

- JEV makes typed judgments; code owns every rollup and decision.
- No UPDATE or DELETE on result tables.
- A module without tests is not done.
