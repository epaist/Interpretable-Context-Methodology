# Instruction Files: Retrieval

201 sections from 34 files, 32,807 tokens. Frozen book cutoffs (0.75, 0.75, 0.9), unchanged. Hybrid k 50. Gold caught = at least one gold section kept. Every quote = a section kept for each evidence quote. Loading every file costs 32,807 tokens and catches all gold by definition.

| Arm | Budget | Gold caught | Every quote | Misses | Unanswerable kept nothing | Answerable kept nothing | Median tokens | Max tokens |
|-----|--------|-------------|-------------|--------|---------------------------|-------------------------|---------------|------------|
| rag | 2000 | 24 of 24 | 24 of 24 | none | 0 of 6 | 0 of 24 | 1984 | 2000 |
| rag+jev | 2000 | 24 of 24 | 24 of 24 | none | 6 of 6 | 0 of 24 | 570 | 1951 |
| jev-all | 2000 | 24 of 24 | 24 of 24 | none | 6 of 6 | 0 of 24 | 762 | 1969 |
| rag | 6000 | 24 of 24 | 24 of 24 | none | 0 of 6 | 0 of 24 | 5976 | 6000 |
| rag+jev | 6000 | 24 of 24 | 24 of 24 | none | 6 of 6 | 0 of 24 | 570 | 5377 |
| jev-all | 6000 | 24 of 24 | 24 of 24 | none | 6 of 6 | 0 of 24 | 762 | 5875 |
