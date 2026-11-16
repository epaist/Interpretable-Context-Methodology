# Onboarding Questionnaire: HCES Lab

Read this file when the user types "setup". Ask ALL questions in one pass; the user answers in one message. Every answer goes into `shared/constants.md`. Defaults come from the test plan agreed on 2026-11-01, so the user can skip any question.

### Q1: Which JEV model?
- Placeholder: `{{JEV_MODEL}}`
- Files: `shared/constants.md`
- Type: free text
- Default: jev-1.14.0 (pinned; cutoffs re-checked on it)

### Q2: Which local vector store?
- Placeholder: `{{VECTOR_STORE}}`
- Files: `shared/constants.md`
- Type: selection
- Options: sqlite-vec plus SQLite FTS5 (default), Chroma

### Q3: Which local embedding model?
- Placeholder: `{{EMBEDDER}}`
- Files: `shared/constants.md`
- Type: selection
- Options: bge-small-en-v1.5 (default), nomic-embed-text

### Q4: Context budget per task, in tokens?
- Placeholder: `{{TOKEN_BUDGET}}`
- Files: `shared/constants.md`
- Type: free text
- Default: 6000 (inside ICM's 2k to 8k stage range)

### Q5: Candidate counts to test?
- Placeholder: `{{TOP_K_SWEEP}}`
- Files: `shared/constants.md`
- Type: free text
- Default: 20, 50, 100

### Q6: Python command on this PC?
- Placeholder: `{{PYTHON}}`
- Files: `shared/constants.md`
- Type: free text
- Default: python

---

## After Onboarding

Tell the user what was filled in, then scan the workspace for remaining `{{` patterns and ask for anything missing. Next step: stage 01.
