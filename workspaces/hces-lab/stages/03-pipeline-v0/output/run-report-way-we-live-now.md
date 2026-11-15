# Stage 03 Run Report: way-we-live-now

25 questions (22 answerable), token budget 6000, judge jev-1.14.0. Gold kept = at least one gold passage in the final context, scored from stored decisions against the current answer key.

Judge pass: 50 runs, 60,172,099 tokens billed, $2.5272, 1045 s of judging, peak 75.0 MB.

## Scorecard

| Arm | Variant | k | Gold kept | Needles kept | Real kept | Low overlap kept | Decoys kept | Unanswerable flagged | Wrongly flagged | Median tokens | Median analysis ms | Cost USD |
|-----|---------|---|-----------|--------------|-----------|------------------|-------------|-----------------------|-----------------|---------------|--------------------|----------|
| rag | hybrid/chaptered | 20 | 91% | 100% | 83% | 100% | 4 | n/a | n/a | 5850 | 0 | 0.0000 |
| rag | hybrid/chaptered | 50 | 82% | 90% | 75% | 100% | 5 | n/a | n/a | 5948 | 0 | 0.0000 |
| rag | hybrid/chaptered | 100 | 82% | 80% | 83% | 100% | 4 | n/a | n/a | 5969 | 0 | 0.0000 |
| rag | hybrid/plain | 20 | 91% | 100% | 83% | 100% | 4 | n/a | n/a | 5916 | 0 | 0.0000 |
| rag | hybrid/plain | 50 | 82% | 90% | 75% | 100% | 5 | n/a | n/a | 5960 | 0 | 0.0000 |
| rag | hybrid/plain | 100 | 82% | 80% | 83% | 100% | 4 | n/a | n/a | 5969 | 0 | 0.0000 |
| rag | vector/chaptered | 20 | 59% | 40% | 75% | 0% | 3 | n/a | n/a | 5903 | 0 | 0.0000 |
| rag | vector/chaptered | 50 | 64% | 50% | 75% | 0% | 3 | n/a | n/a | 5962 | 0 | 0.0000 |
| rag | vector/chaptered | 100 | 64% | 50% | 75% | 0% | 3 | n/a | n/a | 5976 | 0 | 0.0000 |
| rag | vector/plain | 20 | 59% | 40% | 75% | 100% | 3 | n/a | n/a | 5915 | 0 | 0.0000 |
| rag | vector/plain | 50 | 59% | 40% | 75% | 100% | 3 | n/a | n/a | 5955 | 0 | 0.0000 |
| rag | vector/plain | 100 | 59% | 40% | 75% | 100% | 3 | n/a | n/a | 5961 | 0 | 0.0000 |
| rag+jev | hybrid/chaptered | 20 | 95% | 100% | 92% | 100% | 1 | 67% | 0% | 990 | 404 | 0.0215 |
| rag+jev | hybrid/chaptered | 50 | 100% | 100% | 100% | 100% | 2 | 67% | 0% | 990 | 856 | 0.0510 |
| rag+jev | hybrid/chaptered | 100 | 100% | 100% | 100% | 100% | 3 | 67% | 0% | 1587 | 1630 | 0.0990 |
| rag+jev | hybrid/plain | 20 | 95% | 100% | 92% | 100% | 1 | 67% | 0% | 705 | 395 | 0.0218 |
| rag+jev | hybrid/plain | 50 | 100% | 100% | 100% | 100% | 2 | 67% | 0% | 990 | 850 | 0.0515 |
| rag+jev | hybrid/plain | 100 | 100% | 100% | 100% | 100% | 2 | 67% | 0% | 1266 | 1623 | 0.1000 |
| rag+jev | vector/chaptered | 20 | 68% | 50% | 83% | 0% | 1 | 67% | 18% | 700 | 392 | 0.0214 |
| rag+jev | vector/chaptered | 50 | 77% | 60% | 92% | 100% | 2 | 67% | 14% | 803 | 859 | 0.0507 |
| rag+jev | vector/chaptered | 100 | 77% | 60% | 92% | 100% | 3 | 67% | 18% | 1124 | 1630 | 0.0988 |
| rag+jev | vector/plain | 20 | 73% | 50% | 92% | 100% | 2 | 67% | 18% | 705 | 395 | 0.0216 |
| rag+jev | vector/plain | 50 | 77% | 60% | 92% | 100% | 2 | 67% | 14% | 803 | 845 | 0.0512 |
| rag+jev | vector/plain | 100 | 77% | 60% | 92% | 100% | 2 | 67% | 18% | 803 | 1616 | 0.0997 |
| jev-all | all/chaptered | all | 100% | 100% | 100% | 100% | 3 | 33% | 0% | 1921 | 20984 | 1.2777 |
| jev-all | all/plain | all | 100% | 100% | 100% | 100% | 2 | 33% | 0% | 1600 | 20322 | 1.2576 |

## Questions never kept by some runs

| Question | Runs that missed |
|----------|------------------|
| n01 | 12 of 26 |
| n02 | 6 of 26 |
| n03 | 14 of 26 |
| n05 | 12 of 26 |
| n07 | 6 of 26 |
| n09 | 16 of 26 |
| q05 | 16 of 26 |
| q06 | 3 of 26 |
| q08 | 4 of 26 |
| q09 | 4 of 26 |
| q11 | 14 of 26 |
