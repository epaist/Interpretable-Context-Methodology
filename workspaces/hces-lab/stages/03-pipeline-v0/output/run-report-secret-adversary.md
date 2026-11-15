# Stage 03 Run Report: secret-adversary

25 questions (22 answerable), token budget 6000, judge jev-1.14.0. Gold kept = at least one gold passage in the final context, scored from stored decisions against the current answer key.

Judge pass: 50 runs, 15,155,304 tokens billed, $0.6365, 275 s of judging, peak 69.2 MB.

## Scorecard

| Arm | Variant | k | Gold kept | Needles kept | Real kept | Low overlap kept | Decoys kept | Unanswerable flagged | Wrongly flagged | Median tokens | Median analysis ms | Cost USD |
|-----|---------|---|-----------|--------------|-----------|------------------|-------------|-----------------------|-----------------|---------------|--------------------|----------|
| rag | hybrid/chaptered | 20 | 95% | 100% | 92% | 67% | 4 | n/a | n/a | 5834 | 0 | 0.0000 |
| rag | hybrid/chaptered | 50 | 100% | 100% | 100% | 100% | 3 | n/a | n/a | 5969 | 0 | 0.0000 |
| rag | hybrid/chaptered | 100 | 100% | 100% | 100% | 100% | 4 | n/a | n/a | 5970 | 0 | 0.0000 |
| rag | hybrid/plain | 20 | 95% | 100% | 92% | 67% | 3 | n/a | n/a | 5816 | 0 | 0.0000 |
| rag | hybrid/plain | 50 | 100% | 100% | 100% | 100% | 2 | n/a | n/a | 5829 | 0 | 0.0000 |
| rag | hybrid/plain | 100 | 100% | 100% | 100% | 100% | 3 | n/a | n/a | 5865 | 0 | 0.0000 |
| rag | vector/chaptered | 20 | 86% | 80% | 92% | 100% | 1 | n/a | n/a | 5852 | 0 | 0.0000 |
| rag | vector/chaptered | 50 | 86% | 80% | 92% | 100% | 1 | n/a | n/a | 5928 | 0 | 0.0000 |
| rag | vector/chaptered | 100 | 86% | 80% | 92% | 100% | 1 | n/a | n/a | 5945 | 0 | 0.0000 |
| rag | vector/plain | 20 | 68% | 50% | 83% | 100% | 1 | n/a | n/a | 5803 | 0 | 0.0000 |
| rag | vector/plain | 50 | 68% | 50% | 83% | 100% | 1 | n/a | n/a | 5803 | 0 | 0.0000 |
| rag | vector/plain | 100 | 68% | 50% | 83% | 100% | 1 | n/a | n/a | 5878 | 0 | 0.0000 |
| rag+jev | hybrid/chaptered | 20 | 95% | 100% | 92% | 67% | 2 | 100% | 0% | 676 | 414 | 0.0203 |
| rag+jev | hybrid/chaptered | 50 | 100% | 100% | 100% | 100% | 2 | 100% | 0% | 934 | 875 | 0.0491 |
| rag+jev | hybrid/chaptered | 100 | 100% | 100% | 100% | 100% | 3 | 100% | 0% | 934 | 1639 | 0.0961 |
| rag+jev | hybrid/plain | 20 | 95% | 100% | 92% | 67% | 1 | 100% | 0% | 645 | 415 | 0.0205 |
| rag+jev | hybrid/plain | 50 | 100% | 100% | 100% | 100% | 2 | 100% | 0% | 1058 | 893 | 0.0497 |
| rag+jev | hybrid/plain | 100 | 100% | 100% | 100% | 100% | 2 | 100% | 0% | 1058 | 1678 | 0.0975 |
| rag+jev | vector/chaptered | 20 | 91% | 80% | 100% | 100% | 0 | 100% | 9% | 644 | 398 | 0.0201 |
| rag+jev | vector/chaptered | 50 | 100% | 100% | 100% | 100% | 3 | 100% | 0% | 934 | 865 | 0.0488 |
| rag+jev | vector/chaptered | 100 | 100% | 100% | 100% | 100% | 3 | 100% | 0% | 934 | 1646 | 0.0960 |
| rag+jev | vector/plain | 20 | 77% | 60% | 92% | 100% | 0 | 100% | 23% | 618 | 396 | 0.0203 |
| rag+jev | vector/plain | 50 | 86% | 80% | 92% | 100% | 2 | 100% | 9% | 630 | 851 | 0.0494 |
| rag+jev | vector/plain | 100 | 100% | 100% | 100% | 100% | 2 | 100% | 0% | 1058 | 1674 | 0.0974 |
| jev-all | all/chaptered | all | 100% | 100% | 100% | 100% | 3 | 100% | 0% | 934 | 5505 | 0.3251 |
| jev-all | all/plain | all | 100% | 100% | 100% | 100% | 2 | 100% | 0% | 1058 | 5437 | 0.3174 |

## Questions never kept by some runs

| Question | Runs that missed |
|----------|------------------|
| n01 | 5 of 26 |
| n03 | 3 of 26 |
| n06 | 8 of 26 |
| n07 | 8 of 26 |
| n09 | 5 of 26 |
| q01 | 6 of 26 |
| q02 | 5 of 26 |
| q06 | 4 of 26 |
