# Quillmere Phase A Scorecard (run a4)

57 dated questions, each asked when the replay reached its date. 184 facts from 122 records; 96 fact groups.

| Bar | Result | Pass |
|-----|--------|------|
| Current fact correct, at least 95% | 52 of 57 (91%) | FAIL |
| Superseded fact returned as current: never | 0 | PASS |
| Wrongly merged facts: none | 2 groups | FAIL |

| Question kind | Correct | Stale | Wrong | Abstained |
|---|---|---|---|---|
| contradiction | 4 of 5 | 0 | 1 | 0 |
| current | 37 of 40 | 0 | 3 | 0 |
| hot | 6 of 6 | 0 | 0 | 0 |
| stable | 5 of 6 | 0 | 0 | 1 |

## Misses

| Question | As of | Expected | Verdict | Reason |
|---|---|---|---|---|
| qa-q10 id_check | 2026-03-14 | Last 4 of SSN | wrong | The answer states that agents use 'name and service address' and explicitly claims the SSN method was replaced in February 2026. However, the expected value for |
| qa-q22 payment_methods | 2026-05-18 | Card, bank debit | wrong | The answer explicitly states that PayPal is accepted and implies that cards and bank debit are outdated or not the primary focus, whereas the expected value for |
| qa-q35 firmware | 2026-08-12 | 4.2 | wrong | The answer states the firmware version is 4.3, but the expected value is 4.2. The model incorrectly selected one of the 'other values' instead of the expected v |
| qa-q37 contract_terms | 2026-08-24 | 12 or 24 months | wrong | The answer states that plans are available 'month-to-month with no long contract required,' which contradicts the expected value of '12 or 24 months.' While the |
| qa-q42 router_brand | 2026-10-09 | Customer router is the Q-Box | abstained | The answer explicitly states 'Not in memory,' indicating the model does not know the information rather than providing an incorrect or stale value. |

Wrong merges: contract_none+contract_terms, agent_refund_limit+big_credit_approver.

Answer time median 1624 ms. Spend: answer $0.22, extract $1.23, grade $0.16, jev $0.00.
