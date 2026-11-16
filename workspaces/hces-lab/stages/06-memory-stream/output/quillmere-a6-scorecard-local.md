# Quillmere Phase A Scorecard (run a6)

57 dated questions, each asked when the replay reached its date. 103 facts from 122 records; 55 fact groups.

| Bar | Result | Pass |
|-----|--------|------|
| Current fact correct, at least 95% | 42 of 57 (74%) | FAIL |
| Superseded fact returned as current: never | 2 | FAIL |
| Wrongly merged facts: none | 4 groups | FAIL |

| Question kind | Correct | Stale | Wrong | Abstained |
|---|---|---|---|---|
| contradiction | 4 of 5 | 0 | 0 | 1 |
| current | 30 of 40 | 2 | 0 | 8 |
| hot | 5 of 6 | 0 | 1 | 0 |
| stable | 3 of 6 | 0 | 1 | 2 |

## Misses

| Question | As of | Expected | Verdict | Reason |
|---|---|---|---|---|
| qa-q03 email_support | 2026-02-19 | support@quillmere.example | abstained | The answer explicitly states 'Not in memory,' indicating the model does not know the information rather than providing an incorrect or outdated value. |
| qa-q06 refund_window | 2026-02-25 | 14 days | abstained | The answer explicitly states 'Not in memory,' indicating the model does not know the information rather than providing an incorrect or outdated value. |
| qa-q10 id_check | 2026-03-14 | Last 4 of SSN | abstained | The answer explicitly states 'Not in memory,' indicating that the model does not know the information rather than providing an incorrect or outdated value. |
| qa-q19 big_credit_approver | 2026-05-11 | Supervisor approves outage credits over $100 | abstained | The answer explicitly states 'Not in memory,' indicating that the model does not know the information rather than providing an incorrect or outdated fact. |
| qa-q22 payment_methods | 2026-05-18 | Card, bank debit | abstained | The answer explicitly states 'Not in memory,' indicating the model does not know the information rather than providing an incorrect or outdated value. |
| qa-q23 maintenance_window | 2026-05-19 | Tuesday 1 to 4 am | abstained | The answer explicitly states 'Not in memory,' indicating the model does not know the information rather than providing an incorrect or outdated value. |
| qa-q31 extender_model | 2026-06-30 | QX-1 | abstained | The answer explicitly states 'Not in memory,' indicating the model does not know the information rather than providing an incorrect or outdated value. |
| qa-q37 contract_terms | 2026-08-24 | 12 or 24 months | stale | The answer provides '12 months only', which corresponds to the 'Other values at other times' rather than the 'Expected' value of '12 or 24 months'. |
| qa-q42 router_brand | 2026-10-09 | Customer router is the Q-Box | wrong | The answer states that customers get a 'standard router,' whereas the expected value specifies the 'Q-Box.' Since the Q-Box is a specific product and 'standard  |
| qa-q43 senior_discount | 2026-10-20 | $8/mo | stale | The answer provides the value '$5/mo', which corresponds to the 'Other values at other times' rather than the 'Expected' value of '$8/mo' for the specific date  |
| qa-q45 hq | 2026-10-30 | Head office in Alder | abstained | The answer explicitly states 'Not in memory,' indicating that the model does not know the information rather than providing an incorrect or outdated fact. |
| qa-q47 payment_methods | 2026-11-07 | Adds PayPal | abstained | The answer explicitly states 'Not in memory,' indicating that the model does not know the information rather than providing an incorrect or outdated value. |
| qa-q49 agent_refund_limit | 2026-11-22 | $75 | wrong | The answer provided ($100) does not match the expected value ($75). While $100 is listed as one of the 'other values at other times', the specific fact requeste |
| qa-q52 tier2_sla | 2026-12-04 | Within 24 h | abstained | The answer explicitly states 'Not in memory,' indicating the model does not know the information rather than providing an incorrect or outdated value. |
| qa-q55 grace_period | 2026-12-15 | 21 days | abstained | The answer explicitly states 'Not in memory,' indicating the model does not know the information rather than providing an incorrect or outdated value. |

Wrong merges: firmware+redlight_fix+router_brand, agent_refund_limit+missed_appt_credit+outage_credit, retention_offer+senior_discount, big_credit_approver+outage_credit.

Answer time median 304 ms. Spend: answer $0.00, extract $0.00, grade $0.00, jev $0.00.
