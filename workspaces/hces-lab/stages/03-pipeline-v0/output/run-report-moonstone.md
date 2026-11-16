# Stage 03 Run Report: moonstone

26 questions (23 answerable), token budget 6000, judge jev-1.14.0. Gold kept = at least one gold passage in the final context, scored from stored decisions against the current answer key.

Judge pass: 52 runs, 35,555,120 tokens billed, $1.4933, 610 s of judging, peak 75.5 MB.

## Scorecard

| Arm | Variant | k | Gold kept | Needles kept | Real kept | Low overlap kept | Decoys kept | Unanswerable flagged | Wrongly flagged | Median tokens | Median analysis ms | Cost USD |
|-----|---------|---|-----------|--------------|-----------|------------------|-------------|-----------------------|-----------------|---------------|--------------------|----------|
| rag | hybrid/chaptered | 20 | 96% | 100% | 92% | 67% | 2 | n/a | n/a | 5912 | 0 | 0.0000 |
| rag | hybrid/chaptered | 50 | 87% | 80% | 92% | 67% | 0 | n/a | n/a | 5949 | 0 | 0.0000 |
| rag | hybrid/chaptered | 100 | 78% | 60% | 92% | 67% | 1 | n/a | n/a | 5963 | 0 | 0.0000 |
| rag | hybrid/plain | 20 | 96% | 100% | 92% | 67% | 2 | n/a | n/a | 5843 | 0 | 0.0000 |
| rag | hybrid/plain | 50 | 83% | 80% | 85% | 67% | 0 | n/a | n/a | 5940 | 0 | 0.0000 |
| rag | hybrid/plain | 100 | 83% | 70% | 92% | 67% | 0 | n/a | n/a | 5948 | 0 | 0.0000 |
| rag | vector/chaptered | 20 | 65% | 50% | 77% | 67% | 0 | n/a | n/a | 5903 | 0 | 0.0000 |
| rag | vector/chaptered | 50 | 65% | 50% | 77% | 67% | 0 | n/a | n/a | 5938 | 0 | 0.0000 |
| rag | vector/chaptered | 100 | 65% | 50% | 77% | 67% | 0 | n/a | n/a | 5950 | 0 | 0.0000 |
| rag | vector/plain | 20 | 65% | 50% | 77% | 67% | 0 | n/a | n/a | 5890 | 0 | 0.0000 |
| rag | vector/plain | 50 | 65% | 50% | 77% | 67% | 0 | n/a | n/a | 5912 | 0 | 0.0000 |
| rag | vector/plain | 100 | 65% | 50% | 77% | 67% | 0 | n/a | n/a | 5922 | 0 | 0.0000 |
| rag+jev | hybrid/chaptered | 20 | 96% | 100% | 92% | 67% | 0 | 67% | 0% | 930 | 408 | 0.0223 |
| rag+jev | hybrid/chaptered | 50 | 96% | 100% | 92% | 67% | 1 | 67% | 0% | 2425 | 877 | 0.0532 |
| rag+jev | hybrid/chaptered | 100 | 100% | 100% | 100% | 100% | 1 | 67% | 0% | 2995 | 1633 | 0.1036 |
| rag+jev | hybrid/plain | 20 | 96% | 100% | 92% | 67% | 0 | 100% | 0% | 1289 | 410 | 0.0228 |
| rag+jev | hybrid/plain | 50 | 96% | 100% | 92% | 67% | 0 | 100% | 0% | 2384 | 849 | 0.0543 |
| rag+jev | hybrid/plain | 100 | 100% | 100% | 100% | 100% | 0 | 100% | 0% | 2875 | 1626 | 0.1054 |
| rag+jev | vector/chaptered | 20 | 65% | 50% | 77% | 67% | 1 | 67% | 22% | 922 | 391 | 0.0221 |
| rag+jev | vector/chaptered | 50 | 74% | 60% | 85% | 67% | 1 | 67% | 17% | 1505 | 847 | 0.0529 |
| rag+jev | vector/chaptered | 100 | 87% | 70% | 100% | 100% | 1 | 67% | 13% | 2044 | 1630 | 0.1033 |
| rag+jev | vector/plain | 20 | 65% | 50% | 77% | 67% | 0 | 100% | 22% | 960 | 397 | 0.0225 |
| rag+jev | vector/plain | 50 | 78% | 60% | 92% | 67% | 0 | 100% | 17% | 1266 | 841 | 0.0538 |
| rag+jev | vector/plain | 100 | 87% | 70% | 100% | 100% | 0 | 100% | 13% | 1632 | 1616 | 0.1051 |
| jev-all | all/chaptered | all | 100% | 100% | 100% | 100% | 1 | 67% | 0% | 3012 | 11984 | 0.7608 |
| jev-all | all/plain | all | 100% | 100% | 100% | 100% | 0 | 100% | 0% | 3097 | 11458 | 0.7409 |

## Questions never kept by some runs

| Question | Runs that missed |
|----------|------------------|
| n01 | 14 of 26 |
| n05 | 14 of 26 |
| n06 | 8 of 26 |
| n07 | 16 of 26 |
| n09 | 13 of 26 |
| q01 | 5 of 26 |
| q05 | 20 of 26 |
| q10 | 5 of 26 |
| q11 | 8 of 26 |
