# Stage 05 End to End

Plain shape, every question. Gated: frozen RAG + JEV kept set (6000 budget). Full: the whole book. Same instructions for both. Blind grading, one answer at a time in shuffled order. Points: correct 1, partial 0.5; on unanswerable questions only an abstention scores.

| Volume | Arm | Answerable score | Correct | Partial | Wrong | Abstained on answerable | Unanswerable abstained | Median ms | Slowest 10% ms | Cost |
|--------|-----|------------------|---------|---------|-------|-------------------------|------------------------|-----------|----------------|------|
| secret-adversary | gated | 22.5 of 24 (94%) | 21 | 3 | 0 | 0 | 6 of 6 | 1731 | 2372 | $0.21 |
| secret-adversary | full | 21.5 of 24 (90%) | 20 | 3 | 1 | 0 | 6 of 6 | 2303 | 4261 | $1.79 |
| moonstone | gated | 23.5 of 25 (94%) | 23 | 1 | 0 | 1 | 6 of 6 | 1756 | 3803 | $0.31 |
| moonstone | full | 24 of 25 (96%) | 24 | 0 | 0 | 1 | 6 of 6 | 3080 | 13617 | $4.21 |
| way-we-live-now | gated | 24 of 24 (100%) | 24 | 0 | 0 | 0 | 6 of 6 | 1568 | 2306 | $0.34 |
| way-we-live-now | full | 23.5 of 24 (98%) | 23 | 1 | 0 | 0 | 6 of 6 | 2836 | 16888 | $7.00 |
| all | gated | 70 of 73 (96%) | 68 | 4 | 0 | 1 | 18 of 18 | 1725 | 2687 | $0.86 |
| all | full | 69 of 73 (95%) | 67 | 4 | 1 | 1 | 18 of 18 | 2813 | 11256 | $13.00 |

## Where the arms disagree

| Question | Gated | Full | Gated answer | Full answer |
|----------|-------|------|--------------|-------------|
| secret-adversary/q01 | partial | wrong | The passages never name the speaker as Jane Finn or mention a shipwreck. In one account, an unnamed woman shoved the oilskin packet into "a hole in the rock" on | Jane Finn didn't actually hide the oilskin packet. She filled it with blank paper, and the gang took it when they attacked her on the train. She put the real pa |
| secret-adversary/q03 | correct | partial | She died of **"an overdose of chloral"**: the doctor accepted it as accidental, and the bottle she had poured from, once "three parts full," was found empty. Si | She died in her sleep from an overdose of chloral. It was put into the brandy given to revive her after she fainted, and the little bottle on the washstand was  |
| moonstone/q16 | partial | correct | The passages name these narrators: Gabriel Betteredge (the first part and the "EIGHTH NARRATIVE"), Miss Clack ("DRUSILLA CLACK"), Franklin Blake (the "FIFTH NAR | The narrators are an unnamed cousin of John Herncastle (the prologue's family paper), Gabriel Betteredge, Miss Clack (Drusilla Clack), Mathew Bruff, Franklin Bl |
| way-we-live-now/q05 | correct | partial | When Marie reached Liverpool, she was stopped on the platform by a gentleman who addressed her as "Miss Melmotte," and she "had been sent back by the police." H | When Marie and Didon got off the train at Liverpool, a police officer met them on the platform, addressed her as "Miss Melmotte," and told her she would be arre |

Grading cost $1.49. Answering cost $13.86.

## Audit

| Check | Result | Evidence |
|-------|--------|----------|
| Blind | PASS | The grader prompt is built from the question, reference answer, gold passages and the answer text only; answers were graded one at a time in a shuffled order (seed 5) and the code refuses a prompt that carries the arm label |
| Bar: gated no worse than full context | PASS | Answerable score 70 of 73 (96%) gated vs 69 of 73 (95%) full; unanswerable abstained 18 of 18 in both; wrong answers 0 gated vs 1 full |
| Timings | DONE | Answer time per question: gated median 1.7 s, slowest 10% 2.7 s; full median 2.8 s, slowest 10% 11.3 s (with a warm cache). Gated adds the RAG + JEV time measured in stage 04 (0.9 s median) |

## Findings

- Stage 04's answerability misses do not reach the answer. secret-adversary/q18 and moonstone/q19 kept 2 off-topic passages each, and Claude still answered "not in the documents" from them.
- moonstone/n05 abstained in both arms, so the gap is in that question or its needle, not in the gate.
- The arms disagree on 4 questions, all a half point apart: gated scores higher on 3 (secret-adversary q01 and q03, way-we-live-now q05), full on 1 (moonstone q16, a list question where the gate kept only some narrators).
- Cost: gated answering $0.86 against $13.00 for the full books (15 times less), on top of about $0.002 per question for JEV.
- Model: claude-opus-5-5, effort low, server-side refusal fallback on (never triggered). Spend: answering $13.86, grading $1.49, total $15.35 of the $22 cap.
