# Stage 04 Confirmation on Fresh Questions

Frozen cutoffs (0.75, 0.75, 0.9), RAG + JEV, hybrid, k 50. Questions written after the cutoffs froze.

| Question | Shape | Answerable | Gold kept | Kept tokens | Answer p | Says not in docs | Right |
|----------|-------|------------|-----------|-------------|----------|------------------|-------|
| q16 secret-adversary | chaptered | yes | yes | 1224 | 0.93 | no | yes |
| q17 secret-adversary | chaptered | yes | yes | 648 | 0.88 | no | yes |
| q18 secret-adversary | chaptered | no | n/a | 631 | 0.84 | no | NO |
| q16 secret-adversary | plain | yes | yes | 1310 | 0.95 | no | yes |
| q17 secret-adversary | plain | yes | yes | 621 | 0.91 | no | yes |
| q18 secret-adversary | plain | no | n/a | 631 | 0.81 | no | NO |
| q17 moonstone | chaptered | yes | yes | 375 | 0.96 | no | yes |
| q18 moonstone | chaptered | yes | yes | 1177 | 0.97 | no | yes |
| q19 moonstone | chaptered | no | n/a | 1040 | 0.95 | no | NO |
| q17 moonstone | plain | yes | yes | 342 | 0.98 | no | yes |
| q18 moonstone | plain | yes | yes | 1404 | 0.98 | no | yes |
| q19 moonstone | plain | no | n/a | 679 | 0.93 | no | NO |
| q16 way-we-live-now | chaptered | yes | yes | 4337 | 0.99 | no | yes |
| q17 way-we-live-now | chaptered | yes | yes | 1996 | 0.98 | no | yes |
| q18 way-we-live-now | chaptered | no | n/a | 597 | 0.51 | no | NO |
| q16 way-we-live-now | plain | yes | yes | 3234 | 0.99 | no | yes |
| q17 way-we-live-now | plain | yes | yes | 1988 | 0.98 | no | yes |
| q18 way-we-live-now | plain | no | n/a | 0 | 0.00 | yes | yes |

Right: 13 of 18. Answerability tokens billed: 30,374 ($0.0013).
