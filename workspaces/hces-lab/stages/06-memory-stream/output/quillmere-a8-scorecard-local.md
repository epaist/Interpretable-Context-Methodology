# Quillmere Phase A Scorecard (run a8)

57 dated questions, each asked when the replay reached its date. 139 facts from 122 records; 87 fact groups.

| Bar | Result | Pass |
|-----|--------|------|
| Current fact correct, at least 95% | 48 of 57 (84%) | FAIL |
| Superseded fact returned as current: never | 1 | FAIL |
| Wrongly merged facts: none | 4 groups | FAIL |

| Question kind | Correct | Stale | Wrong | Abstained |
|---|---|---|---|---|
| contradiction | 5 of 5 | 0 | 0 | 0 |
| current | 34 of 40 | 1 | 2 | 3 |
| hot | 5 of 6 | 0 | 0 | 1 |
| stable | 4 of 6 | 0 | 1 | 1 |

## Misses

| Question | As of | Expected | Verdict | Reason |
|---|---|---|---|---|
| qa-q10 id_check | 2026-03-14 | Last 4 of SSN | abstained | The answer explicitly states 'Not in memory,' indicating that the model does not know the information rather than providing an incorrect or outdated value. |
| qa-q13 redlight_fix | 2026-04-22 | Firmware 4.2 update | abstained | The answer explicitly states 'Not in memory,' indicating that the model does not know the information rather than providing an incorrect or outdated specific va |
| qa-q22 payment_methods | 2026-05-18 | Card, bank debit | wrong | The answer states that 'PayPal' is the accepted payment method, but the expected value is 'Card, bank debit'. The answer fails to include the expected methods a |
| qa-q25 redlight_fix | 2026-06-03 | Firmware 4.2 update | abstained | The answer explicitly states 'Not in memory,' indicating the model does not know the information rather than providing an incorrect or outdated specific value. |
| qa-q34 torrent_download | 2026-08-06 | Torrent 1G downloads at 1,000 Mbps | abstained | The answer explicitly states 'Not in memory,' indicating the model does not know the information rather than providing an incorrect or stale value. |
| qa-q37 contract_terms | 2026-08-24 | 12 or 24 months | wrong | The answer states that no long contract is required, which contradicts the expected value of '12 or 24 months' and the other value of '12 months only'. It does  |
| qa-q42 router_brand | 2026-10-09 | Customer router is the Q-Box | wrong | The answer states that customers get a 'standard router' included with installation, whereas the expected value specifies that the customer router is the 'Q-Box |
| qa-q52 tier2_sla | 2026-12-04 | Within 24 h | abstained | The answer explicitly states 'Not in memory,' indicating the model does not know the information rather than providing an incorrect or outdated value. |
| qa-q57 move_fee | 2026-12-18 | Free | stale | The answer provides the value '$50', which corresponds to the 'Other values at other times' rather than the 'Expected' value of 'Free' for the specified date (2 |

Wrong merges: missed_appt_credit+tech_visit_fee, autopay_discount+contract_none, contract_none+contract_terms, firmware+redlight_fix.

Answer time median 407 ms. Spend: answer $0.00, extract $0.00, grade $0.00, jev $0.00.
