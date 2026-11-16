# Stage 04 Scorecard

Exam questions only (fresh set is in confirm.md). Both shapes, budget 6000, frozen cutoffs (0.75, 0.75, 0.9), retrieval hybrid k 50, judge jev-1.14.0. Gold caught = at least one gold passage kept. Lookalikes kept counts real lookalikes and needle decoys. Timings are per question per shape: access + analysis + response, analysis including the judge time scaled to the arm's candidates.

| Volume | Arm | Gold caught | Needles | Misses | Lookalikes kept | Gold share | Unanswerable flagged | Wrongly flagged | Median tokens | Max tokens | Median ms | Slowest 10% ms | Cost per question |
|--------|-----|-------------|---------|--------|-----------------|------------|----------------------|-----------------|---------------|------------|-----------|----------------|-------------------|
| secret-adversary | rag | 100% | 100% | 0 | 5 | 0.07 | n/a | n/a | 5926 | 5999 | 11 | 17 | $0.0000 |
| secret-adversary | rag+jev | 100% | 100% | 0 | 4 | 0.67 | 100% | 0% | 630 | 2920 | 894 | 966 | $0.0020 |
| secret-adversary | jev-all | 100% | 100% | 0 | 5 | 0.66 | 100% | 0% | 630 | 4797 | 5481 | 5772 | $0.0129 |
| moonstone | rag | 85% | 80% | 7 | 0 | 0.07 | n/a | n/a | 5945 | 6000 | 13 | 17 | $0.0000 |
| moonstone | rag+jev | 96% | 100% | 2 | 1 | 0.66 | 100% | 0% | 474 | 4367 | 884 | 950 | $0.0021 |
| moonstone | jev-all | 100% | 100% | 0 | 1 | 0.61 | 100% | 2% | 474 | 5992 | 11713 | 12673 | $0.0289 |
| way-we-live-now | rag | 82% | 90% | 8 | 10 | 0.10 | n/a | n/a | 5959 | 5999 | 17 | 22 | $0.0000 |
| way-we-live-now | rag+jev | 100% | 100% | 0 | 4 | 0.72 | 100% | 0% | 371 | 5966 | 872 | 971 | $0.0021 |
| way-we-live-now | jev-all | 100% | 100% | 0 | 5 | 0.69 | 100% | 0% | 371 | 5978 | 20589 | 21939 | $0.0507 |
| all | rag | 89% | 90% | 15 | 15 | 0.08 | n/a | n/a | 5946 | 6000 | 13 | 19 | $0.0000 |
| all | rag+jev | 99% | 100% | 2 | 9 | 0.68 | 100% | 0% | 474 | 5966 | 881 | 959 | $0.0020 |
| all | jev-all | 100% | 100% | 0 | 11 | 0.65 | 100% | 1% | 474 | 5992 | 11713 | 21277 | $0.0308 |

Answerability calls for this scorecard: 563,983 tokens billed ($0.0237).
