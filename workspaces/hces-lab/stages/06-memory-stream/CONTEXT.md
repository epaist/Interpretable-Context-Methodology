# Stage 06: Memory Stream (Phase 4, not started)

Test self-learning memory: replay dated records from the made-up company Quillmere Broadband in order, and check the store keeps current facts current.

## Inputs

| Source | File/Location | Section/Scope | Why |
|--------|--------------|---------------|-----|
| Constants | `../../shared/constants.md` | "Memory Stream Bars" and the model rows | Pass conditions, judge, budget |
| Timings | `../../shared/timings.md` | Full file | What to log |
| Stream spec | `references/memory-stream.md` | Full file | Company, phases A to C, what to plant |
| Frozen cutoffs | `../04-exam/output/cutoffs.json` | Full file | Gate settings carried into memory |
| Knowledge base rules | `../../kb/CONTEXT.md` | "Streams" | Where the stream is stored |

## Process

1. Confirm stages 01 to 05 are done or the user has started Phase 4 anyway.
2. Write the Quillmere company sheet: plans, prices, SOP list, governance rules, and the timeline of every planned change.
3. **[Checkpoint]** Present the company sheet and the planted-change list.
4. Generate phase A (tickets and call logs only) into `kb/streams/quillmere/a/`, with the fact ledger and as-of questions.
5. **[Checkpoint]** State the JEV cost of the replay and wait for OK.
6. Replay phase A in date order through `hces/memory/`; ask each question at its timestamp; log the three timings.
7. Score against the ledger, then run the audit and write the phase A scorecard.
8. **[Checkpoint]** Present the scorecard. Phase B starts only on the user's go.
9. Repeat steps 4 to 8 for phase B (add versioned SOPs and governance) and phase C (mix everything, add noise).

## Checkpoints

| After Step | Agent Presents | Human Decides |
|------------|---------------|---------------|
| 3 | Company sheet and planted changes | Approve or edit |
| 5 | Replay cost estimate | Go or stop |
| 8 | Phase scorecard | Next phase, fix, or stop |

## Audit

| Check | Pass Condition |
|-------|---------------|
| Ledger | Every planted change, duplicate and contradiction has a ledger row with valid-from and valid-to dates |
| Questions | Every question has an as-of date and an expected answer from the ledger |
| Bars | Each memory bar marked pass or fail with its number |
| Timings | Three timings on every question |
| Private data | None: all records generated |

## Outputs

| Artifact | Location | Format |
|----------|----------|--------|
| Company sheet | `output/quillmere-company.md` | Plans, prices, rules, change timeline |
| Fact ledger | `output/quillmere-ledger.jsonl` | fact, value, valid_from, valid_to, source record IDs, kind |
| Questions | `output/quillmere-questions.jsonl` | question, as_of, expected, ledger row, phase |
| Scorecard | `output/quillmere-<phase>-scorecard.md` | Bars, misses, wrong merges, cost, timings |
| Stream records | `../../kb/streams/quillmere/<phase>/records.jsonl` | One dated record per line |
