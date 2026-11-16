# Quillmere Phase A Scorecard (run a3)

57 dated questions, each asked when the replay reached its date. 192 facts from 122 records; 141 fact groups.

| Bar | Result | Pass |
|-----|--------|------|
| Current fact correct, at least 95% | 50 of 57 (88%) | FAIL |
| Superseded fact returned as current: never | 2 | FAIL |
| Wrongly merged facts: none | 0 groups | PASS |

| Question kind | Correct | Stale | Wrong | Abstained |
|---|---|---|---|---|
| contradiction | 3 of 5 | 1 | 0 | 1 |
| current | 37 of 40 | 1 | 0 | 2 |
| hot | 5 of 6 | 0 | 1 | 0 |
| stable | 5 of 6 | 0 | 0 | 1 |

## Misses

| Question | As of | Expected | Verdict | Reason |
|---|---|---|---|---|
| qa-q08 retention_offer | 2026-03-02 | 3 months at 25% off | abstained | The answer says the information is not in memory, so it declines to give a value. |
| qa-q17 support_phone | 2026-05-08 | 1-888-555-0177 | abstained | The answer gives both the expected number and the older one, and never commits to either as the support number. Because it says it is unclear which is the main  |
| qa-q22 payment_methods | 2026-05-18 | Card, bank debit | stale | The answer lists cards and bank debit but also includes PayPal. PayPal matches the other-time value 'Adds PayPal', not the expected value for this date, which h |
| qa-q26 support_phone | 2026-06-04 | 1-888-555-0177 | abstained | The answer gives both the expected number and the older one, and it does not pick either as the support line. It says it cannot tell which is the main number, s |
| qa-q35 firmware | 2026-08-12 | 4.2 | stale | The answer gives 4.3, but the expected value as of 2026-08-12 is 4.2. Since 4.3 is one of the fact's values at another time, this is a stale answer, not a wrong |
| qa-q38 support_phone | 2026-09-10 | 1-888-555-0177 | wrong | The answer gives both the expected number (1-888-555-0177) and the older one (1-800-555-0142), presents both as current, and doesn't pick either. Because it hed |
| qa-q42 router_brand | 2026-10-09 | Customer router is the Q-Box | abstained | The answer says the information is not in memory, which is a statement of not knowing. It gives no router name. |

Wrong merges: none.

Answer time median 1806 ms. Spend: answer $0.23, extract $0.80, grade $0.17, jev $0.08.

## Audit (2026-11-02, reruns a2 and a3)

Both reruns reuse run a's 192 facts and JEV links; only the grouping rule, 8 groups in the notes, answers and grading are new. Each cost $0.40 Claude, no JEV.

| Run | Grouping | Correct | Stale | Wrong merges |
|---|---|---|---|---|
| a | every link at 0.5 | 50 of 57 | 2 | 4 |
| a2 | best match at 0.5 | 51 of 57 | 2 | 4 |
| a3 | best match at 0.9 (frozen critical cutoff) | 50 of 57 | 2 | 0 |

Best match alone fixed Glide's cap (q48). The other merges are not chains: JEV rates the lookalikes themselves as the same attribute (contract term vs month-to-month 0.85, firmware version vs red-light fix 0.86), while true changes can score lower (price lock 12 vs 24 months 0.81). At 0.9 nothing merges wrongly, but the old and new support numbers land in separate groups, so the answer hedges between them (q17, q26, q38). No single cutoff separates the two.

8 groups did not fix q42 (router): the Q-Box fact is stored as "Q-Box, standard equipment", which the question's embedding does not reach.

Next fix: give each fact a canonical key at extraction (the extractor sees the keys memory already holds and picks one or names a new one), and use JEV to check the key, not to find it.
