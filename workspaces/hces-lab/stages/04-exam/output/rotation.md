# Stage 04 Cutoff Rotation

Arm: RAG + JEV, hybrid, k 50, both shapes, budget 6000. 55 cutoff settings searched. Cutoffs are 1.01 when switched off.

## Rotation

| Set | Cutoff | Unsure low | Critical at | Gold caught | Needles | Gold share | Decoys kept | Median tokens |
|-----|--------|------------|-------------|-------------|---------|------------|-------------|---------------|
| tune without secret-adversary | 0.75 | 0.75 | 0.9 | 98% | 100% | 0.68 | 5 | 448 |
| test on secret-adversary | 0.75 | 0.75 | 0.9 | 100% | 100% | 0.67 | 4 | 630 |
| tune without moonstone | 1 | 1.01 | 0.7 | 100% | 100% | 0.76 | 6 | 356 |
| test on moonstone | 1 | 1.01 | 0.7 | 91% | 100% | 0.70 | 1 | 422 |
| tune without way-we-live-now | 0.75 | 0.75 | 0.9 | 98% | 100% | 0.66 | 5 | 514 |
| test on way-we-live-now | 0.75 | 0.75 | 0.9 | 100% | 100% | 0.72 | 4 | 371 |

## Pooled test result

Gold caught 97% (130 of 134), needles 100%, mean gold share 0.69, decoys kept 9.

## Frozen cutoffs (chosen by the same rule on all three volumes)

| Set | Cutoff | Unsure low | Critical at | Gold caught | Needles | Gold share | Decoys kept | Median tokens |
|-----|--------|------------|-------------|-------------|---------|------------|-------------|---------------|
| all volumes | 0.75 | 0.75 | 0.9 | 99% | 100% | 0.68 | 9 | 474 |
