# Timings

Every run logs three times, in milliseconds, into the results store next to its scores. No run is complete without them.

| Timing | Starts | Ends | Covers |
|--------|--------|------|--------|
| access | Prompt received | Candidates in hand | Reading files, loading a volume, vector and keyword search |
| analysis | Candidates in hand | Budget filled | Embedding (if done at query time), JEV scoring, metadata, answerability, rollup |
| response | Budget filled | Final output written | Claude's answer, or the "not in the documents" reply |

## Rules

- Measure with a monotonic clock (`time.perf_counter_ns`), never wall-clock time.
- Log per question and per arm, plus the volume size in tokens.
- Report median and slowest 10% in every stage report.
- Index build time is logged separately as `index_build`, not inside access.
- No speed bars until real numbers exist after stage 03.

## Memory

Every run also logs `peak_rss_mb`: the highest memory the process used during the run, read from the operating system (psutil). Index builds log their own peak. Report median and highest per stage, next to the timings. No memory bars until real numbers exist after stage 03.
