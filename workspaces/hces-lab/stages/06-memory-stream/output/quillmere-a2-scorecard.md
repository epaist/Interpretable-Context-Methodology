# Quillmere Phase A Scorecard (run a2)

57 dated questions, each asked when the replay reached its date. 192 facts from 122 records; 93 fact groups.

| Bar | Result | Pass |
|-----|--------|------|
| Current fact correct, at least 95% | 51 of 57 (89%) | FAIL |
| Superseded fact returned as current: never | 2 | FAIL |
| Wrongly merged facts: none | 4 groups | FAIL |

| Question kind | Correct | Stale | Wrong | Abstained |
|---|---|---|---|---|
| contradiction | 4 of 5 | 1 | 0 | 0 |
| current | 36 of 40 | 1 | 1 | 2 |
| hot | 6 of 6 | 0 | 0 | 0 |
| stable | 5 of 6 | 0 | 0 | 1 |

## Misses

| Question | As of | Expected | Verdict | Reason |
|---|---|---|---|---|
| qa-q08 retention_offer | 2026-03-02 | 3 months at 25% off | abstained | The answer says the information is not in memory, so it declines to give any value for the retention offer. |
| qa-q18 price_lock | 2026-05-09 | 12 months | abstained | The answer says the information is not in memory, so it gives no value for the price lock. |
| qa-q22 payment_methods | 2026-05-18 | Card, bank debit | stale | The answer presents PayPal as the current payment method, which is the value from another time. It treats card and bank debit, the expected value for this date, |
| qa-q35 firmware | 2026-08-12 | 4.2 | stale | The answer gives 4.3. That is one of the fact's values at another time, not the expected 4.2 as of 2026-08-12. |
| qa-q37 contract_terms | 2026-08-24 | 12 or 24 months | wrong | The answer says the plans are month-to-month only. That matches neither the expected value (12 or 24 months) nor the other recorded value (12 months only). |
| qa-q42 router_brand | 2026-10-09 | Customer router is the Q-Box | abstained | The answer says the information is not in memory, which is a statement of not knowing. It does not give the expected value (Q-Box) or any other value. |

Wrong merges: firmware+redlight_fix, firmware+redlight_fix, contract_none+contract_terms+price_lock, agent_refund_limit+big_credit_approver.

Answer time median 1788 ms. Spend: answer $0.23, extract $0.80, grade $0.17, jev $0.08.

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
