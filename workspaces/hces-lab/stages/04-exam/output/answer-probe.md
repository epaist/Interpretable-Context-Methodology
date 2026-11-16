# Answerability Probe

Kept sets from RAG + JEV at the frozen cutoffs. Design set: exam + fresh (170 cases). Holdout: 12 cases from 6 unanswerable questions written before the probe ran.

## Best threshold per signal, design set

| Set | Signal | Flag below | Unanswerable flagged | Answerable wrongly flagged | Right |
|-----|--------|------------|----------------------|----------------------------|-------|
| design | base | 0.5 | 20 of 24 | 0 of 144 | 164 of 168 |
| design | strict_set | 0.05 | 19 of 24 | 0 of 144 | 163 of 168 |
| design | strict_unit | 0.05 | 19 of 24 | 0 of 144 | 163 of 168 |
| design | choice_stated | 0.05 | 19 of 24 | 0 of 144 | 163 of 168 |
| design, current rule | base | 0.5 | 20 of 24 | 0 of 144 | 164 of 168 |

## Picked: base, flag below 0.5

| Set | Signal | Flag below | Unanswerable flagged | Answerable wrongly flagged | Right |
|-----|--------|------------|----------------------|----------------------------|-------|
| design | base | 0.5 | 20 of 24 | 0 of 144 | 164 of 168 |
| holdout | base | 0.5 | 12 of 12 | 0 of 0 | 12 of 12 |
| holdout, current rule | base | 0.5 | 12 of 12 | 0 of 0 | 12 of 12 |

## Holdout cases, every signal

| Question | Shape | Kept | base | strict_set | strict_unit | choice |
|----------|-------|------|------|------------|-------------|--------|
| secret-adversary/q19 | chaptered | 0 | 0.00 | 0.00 | 0.00 | none 0.00 |
| secret-adversary/q20 | chaptered | 0 | 0.00 | 0.00 | 0.00 | none 0.00 |
| secret-adversary/q19 | plain | 0 | 0.00 | 0.00 | 0.00 | none 0.00 |
| secret-adversary/q20 | plain | 0 | 0.00 | 0.00 | 0.00 | none 0.00 |
| moonstone/q20 | chaptered | 0 | 0.00 | 0.00 | 0.00 | none 0.00 |
| moonstone/q21 | chaptered | 0 | 0.00 | 0.00 | 0.00 | none 0.00 |
| moonstone/q20 | plain | 0 | 0.00 | 0.00 | 0.00 | none 0.00 |
| moonstone/q21 | plain | 0 | 0.00 | 0.00 | 0.00 | none 0.00 |
| way-we-live-now/q19 | chaptered | 0 | 0.00 | 0.00 | 0.00 | none 0.00 |
| way-we-live-now/q20 | chaptered | 0 | 0.00 | 0.00 | 0.00 | none 0.00 |
| way-we-live-now/q19 | plain | 0 | 0.00 | 0.00 | 0.00 | none 0.00 |
| way-we-live-now/q20 | plain | 0 | 0.00 | 0.00 | 0.00 | none 0.00 |
