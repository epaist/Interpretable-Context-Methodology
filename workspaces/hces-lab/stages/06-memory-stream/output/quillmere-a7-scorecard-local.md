# Quillmere Phase A Scorecard (run a7)

57 dated questions, each asked when the replay reached its date. 113 facts from 122 records; 59 fact groups.

| Bar | Result | Pass |
|-----|--------|------|
| Current fact correct, at least 95% | 41 of 57 (72%) | FAIL |
| Superseded fact returned as current: never | 3 | FAIL |
| Wrongly merged facts: none | 3 groups | FAIL |

| Question kind | Correct | Stale | Wrong | Abstained |
|---|---|---|---|---|
| contradiction | 4 of 5 | 1 | 0 | 0 |
| current | 28 of 40 | 2 | 2 | 8 |
| hot | 5 of 6 | 0 | 1 | 0 |
| stable | 4 of 6 | 0 | 1 | 1 |

## Misses

| Question | As of | Expected | Verdict | Reason |
|---|---|---|---|---|
| qa-q05 outage_credit | 2026-02-23 | 1 day per full 24 h down | abstained | The answer explicitly states 'Not in memory,' indicating the model does not know the information rather than providing an incorrect or outdated value. |
| qa-q06 refund_window | 2026-02-25 | 14 days | abstained | The answer explicitly states 'Not in memory,' indicating the model does not know the information rather than providing an incorrect or outdated value. |
| qa-q09 fiber_towns | 2026-03-11 | Alder, Brook | abstained | The answer explicitly states 'Not in memory,' indicating the model does not know the information rather than providing an incorrect or outdated value. |
| qa-q10 id_check | 2026-03-14 | Last 4 of SSN | abstained | The answer explicitly states 'Not in memory,' indicating that the model does not know the information rather than providing an incorrect or outdated value. |
| qa-q19 big_credit_approver | 2026-05-11 | Supervisor approves outage credits over $100 | abstained | The answer explicitly states 'Not in memory,' indicating that the model does not know the information rather than providing an incorrect or outdated fact. |
| qa-q22 payment_methods | 2026-05-18 | Card, bank debit | wrong | The answer states that 'PayPal' is the accepted payment method, but the expected value is 'Card, bank debit'. The answer fails to include the expected methods a |
| qa-q23 maintenance_window | 2026-05-19 | Tuesday 1 to 4 am | abstained | The answer explicitly states 'Not in memory,' indicating the model does not know the information rather than providing an incorrect or outdated value. |
| qa-q31 extender_model | 2026-06-30 | QX-1 | abstained | The answer explicitly states 'Not in memory,' indicating the model does not know the information rather than providing an incorrect or outdated value. |
| qa-q35 firmware | 2026-08-12 | 4.2 | stale | The answer provides '4.3', which is listed as one of the 'Other values at other times' rather than the expected value of '4.2'. |
| qa-q42 router_brand | 2026-10-09 | Customer router is the Q-Box | wrong | The answer states that customers get a 'standard router,' whereas the expected value specifies the 'Q-Box.' Since the Q-Box is a specific product and 'standard  |
| qa-q43 senior_discount | 2026-10-20 | $8/mo | stale | The answer provides the value '$5/mo', which corresponds to the 'Other values at other times' rather than the 'Expected' value of '$8/mo' for the specific date  |
| qa-q45 hq | 2026-10-30 | Head office in Alder | abstained | The answer explicitly states 'Not in memory,' indicating that the model does not know the information rather than providing an incorrect or outdated fact. |
| qa-q49 agent_refund_limit | 2026-11-22 | $75 | wrong | The answer provided ($100) does not match the expected value ($75). While $100 is listed as one of the 'other values' from different times, it is incorrect for  |
| qa-q51 status_page | 2026-12-02 | quillmere.example/status | wrong | The answer provides 'status.quillmere.example' (the value from other times), whereas the expected value for the date 2026-12-02 is 'quillmere.example/status'. T |
| qa-q52 tier2_sla | 2026-12-04 | Within 24 h | abstained | The answer explicitly states 'Not in memory,' indicating the model does not know the information rather than providing an incorrect or outdated value. |
| qa-q55 grace_period | 2026-12-15 | 21 days | stale | The answer provides '30 days', which corresponds to the 'Other values at other times' rather than the 'Expected' value of '21 days' for the specific date 2026-1 |

Wrong merges: firmware+redlight_fix, install_fee+tech_visit_fee, extender_model+mesh_max.

Answer time median 451 ms. Spend: answer $0.00, extract $0.00, grade $0.00, jev $0.00.
