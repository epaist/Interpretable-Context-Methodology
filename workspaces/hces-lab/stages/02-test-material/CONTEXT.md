# Stage 02: Knowledge-Base Test Material

Build the volumes, questions and answer key the exam runs on. The user approves the key before any scoring.

## Inputs

| Source | File/Location | Section/Scope | Why |
|--------|--------------|---------------|-----|
| Constants | `../../shared/constants.md` | Full file | Budget, store |
| Knowledge base rules | `../../kb/CONTEXT.md` | Full file | Folder layout, passage records |
| Question rules | `references/question-rules.md` | Full file | How to write questions and needles |

## Process

1. Propose three Project Gutenberg volumes of about 100k, 250k and 500k tokens, with title, size and why each fits.
2. **[Checkpoint]** Wait for the user to approve or swap volumes.
3. Download each into `kb/volumes/<slug>/`, strip Gutenberg headers, write `plain.txt` and `chaptered.txt`, record the source URL.
4. Cut passages with stable IDs into `passages.jsonl`; log `index_build` time later in stage 03, not here.
5. Write about 15 questions per volume, about 3 of them unanswerable from the text.
6. Mark gold passages for each answerable question.
7. Plant about 10 needles per volume with the one planter; record each needle's ID, text and question.
8. Add hard cases: low word overlap with the question, and lookalike passages.
9. Run `.venv\Scripts\python.exe -m hces.answer_key`: it plants needles, rebuilds passages, audits, and writes the key only if every check passes.
10. **[Checkpoint]** Present the key for approval.

## Checkpoints

| After Step | Agent Presents | Human Decides |
|------------|---------------|---------------|
| 1 | Three candidate volumes | Approve or swap |
| 10 | Questions, gold passages, needles | Approve before scoring |

## Audit

| Check | Pass Condition |
|-------|---------------|
| Sizes | Each volume within 20% of its target |
| Questions | About 15 per volume, about 3 unanswerable |
| Gold | Every answerable question has at least one gold passage ID |
| Needles | Each needle is the only answer to its question |
| IDs | Every ID in the key exists in `passages.jsonl` |

## Outputs

| Artifact | Location | Format |
|----------|----------|--------|
| Question spec | `output/questions.jsonl` | Real-text questions with evidence quotes or absent terms |
| Needle spec | `output/needles.jsonl` | Needles with their questions, plus lookalike decoys |
| Answer key | `output/answer-key.jsonl` | question, volume, answerable, gold IDs per shape, needle ID, decoy IDs, hard-case tag |
| Audit | `output/audit.md` | Every audit check with its result |
| Review copy | `output/answer-key-review.md` | The key as tables, for the step 10 checkpoint |
| Volume summary | `output/volumes.md` | Title, URL, tokens, passages, shapes |
