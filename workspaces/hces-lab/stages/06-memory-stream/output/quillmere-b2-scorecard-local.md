# Quillmere Phase B Scorecard (run b2)

58 dated questions, each asked when the replay reached its date. 559 facts from 222 records; 213 fact groups.

| Bar | Result | Pass |
|-----|--------|------|
| Current fact correct, at least 95% | 52 of 58 (90%) | FAIL |
| Superseded fact returned as current: never | 4 | FAIL |
| Wrongly merged facts: none | 1 groups | FAIL |

| Question kind | Correct | Stale | Wrong | Abstained |
|---|---|---|---|---|
| doc version | 7 of 7 | 0 | 0 | 0 |
| sop key | 26 of 27 | 1 | 0 | 0 |
| stable | 5 of 6 | 0 | 0 | 1 |
| stale citation | 4 of 5 | 1 | 0 | 0 |
| ticket key | 10 of 13 | 2 | 0 | 1 |

## Misses

| Question | As of | Expected | Verdict | Reason |
|---|---|---|---|---|
| qb-q22 contract_none | 2026-04-17 | Month-to-month is available on every plan | abstained | The answer explicitly states 'Not in memory,' indicating that the model does not know the information rather than providing a specific incorrect or stale value. |
| qb-q29 tier2_sla | 2026-06-24 | Callback within 48 h | abstained | The answer explicitly states 'Not in memory,' indicating the model does not know the information rather than providing an incorrect or outdated value. |
| qb-q32 reconnect_fee | 2026-07-02 | Waived | stale | The answer provides the value '$25', which corresponds to the 'Other values at other times' rather than the 'Expected' value of 'Waived' for the specific date 2 |
| qb-q41 firmware | 2026-09-10 | 4.3 | stale | The answer provides '4.2', which is listed as one of the 'Other values at other times' rather than the expected value of '4.3'. |
| qb-q44 agent_refund_limit | 2026-10-05 | $100 | stale | The answer provides '$50', which corresponds to one of the 'Other values at other times' rather than the expected value of '$100'. |
| qb-q53 paperless_credit | 2026-11-08 | Ended | stale | The answer provides the value '$2/mo', which corresponds to the 'Other values at other times'. However, the 'Expected' value for the fact as of 2026-11-08 is 'E |

Wrong merges: contract_none+contract_terms.

Answer time median 565 ms. Spend: answer $0.00, extract $0.00, grade $0.00, jev $0.03.
