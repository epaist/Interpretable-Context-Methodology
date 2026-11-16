# Quillmere Phase C Scorecard (run c1)

58 dated questions, each asked when the replay reached its date. 609 facts from 317 records; 232 fact groups.

| Bar | Result | Pass |
|-----|--------|------|
| Current fact correct, at least 95% | 53 of 58 (91%) | FAIL |
| Superseded fact returned as current: never | 1 | FAIL |
| Wrongly merged facts: none | 1 groups | FAIL |

| Question kind | Correct | Stale | Wrong | Abstained |
|---|---|---|---|---|
| announced, not yet | 9 of 10 | 0 | 0 | 1 |
| early announcement | 1 of 1 | 0 | 0 | 0 |
| never valid | 1 of 1 | 0 | 0 | 0 |
| sop key | 26 of 27 | 0 | 1 | 0 |
| stable | 5 of 6 | 0 | 1 | 0 |
| ticket key | 11 of 13 | 1 | 1 | 0 |

## Misses

| Question | As of | Expected | Verdict | Reason |
|---|---|---|---|---|
| qc-q20 paperless_credit | 2026-07-29 | Ended | stale | The answer provides the value '$2/mo', which corresponds to the 'Other values at other times'. However, the 'Expected' value for the fact as of the question dat |
| qc-q23 tier2_sla | 2026-08-06 | Callback within 48 h | abstained | The answer explicitly states 'Not in memory,' indicating the model does not know the information rather than providing an incorrect or outdated value. |
| qc-q31 contract_none | 2026-09-17 | Month-to-month is available on every plan | wrong | The answer directly contradicts the expected value. The expected value states that month-to-month service is available on every plan, while the answer claims it |
| qc-q52 payment_methods | 2026-11-30 | Adds PayPal | wrong | The answer states that 'PayPal is the accepted payment method' (singular), implying it is the only one. However, the expected value indicates that PayPal was ad |
| qc-q56 contract_terms | 2026-12-07 | 12 months only | wrong | The answer states that the offered terms are '12 or 24 months', which contradicts the expected value of '12 months only'. Although the answer mentions a note ab |

Wrong merges: contract_none+contract_terms.

Answer time median 532 ms. Spend: answer $0.00, extract $0.00, grade $0.00, jev $0.04.
