# Test Arms

Every comparison uses the same questions and the same token budget.

| Arm | What happens | What it tells us |
|-----|-------------|------------------|
| RAG only | Retrieval keeps top matches until the budget is full | Baseline: is JEV worth adding? |
| RAG + JEV | Retrieval pulls a wider candidate set; JEV scores each against the rubric, tags metadata, judges answerability; code fills the budget | The system |
| JEV on everything | JEV scores every passage, no retrieval | The ceiling, and how often retrieval misses |

## Retrieval Variants (inside the RAG arms)

| Variant | Meaning |
|---------|---------|
| vector | Embedding search only |
| hybrid | Embedding search plus keyword search (FTS5), merged |
| k | Candidate count, from the sweep in `constants.md` |

## Rules

- Retrieval sets the ceiling: JEV cannot rescue a passage that was never retrieved.
- Answerability is asked in the same JEV request. Below the cutoff, reply "not in the documents".
- Clustering (DBSCAN) only groups near-duplicates. It never drops a passage.
