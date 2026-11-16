# Rubric Guide

Claude writes one rubric per task. JEV answers it; code decides.

## Shape

| Part | JEV question type | Example |
|------|------------------|---------|
| Relevance | Score 1 to 5 | "How directly does this passage help answer: {question}?" |
| Critical flag | Noul (probability) | "Does this passage contain the specific fact asked for?" |
| Metadata | Choice | speaker, place, time period, topic |
| Answerability | Noul, once per request | "Is the kept evidence enough to answer: {question}?" |

## Rules

- The prompt is the shared state; each candidate passage is judged against it.
- Anchors for each score level, one line each.
- Version every rubric (`rubric_id`, `version`); store it with the results.
- Keep the state under 32k tokens; split candidates across requests if needed.
- When unsure, keep: the cutoff errs toward recall.
