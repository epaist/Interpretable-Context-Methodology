# Quillmere Phase A Scorecard (run a5)

57 dated questions, each asked when the replay reached its date. 66 facts from 122 records; 31 fact groups.

| Bar | Result | Pass |
|-----|--------|------|
| Current fact correct, at least 95% | 30 of 57 (53%) | FAIL |
| Superseded fact returned as current: never | 0 | PASS |
| Wrongly merged facts: none | 4 groups | FAIL |

| Question kind | Correct | Stale | Wrong | Abstained |
|---|---|---|---|---|
| contradiction | 4 of 5 | 0 | 0 | 1 |
| current | 19 of 40 | 0 | 0 | 21 |
| hot | 5 of 6 | 0 | 0 | 1 |
| stable | 2 of 6 | 0 | 0 | 4 |

## Misses

| Question | As of | Expected | Verdict | Reason |
|---|---|---|---|---|
| qa-q01 reconnect_fee | 2026-01-23 | $25 | abstained | The answer explicitly states 'Not in memory,' indicating the model does not know the fact rather than providing an incorrect or outdated value. |
| qa-q03 email_support | 2026-02-19 | support@quillmere.example | abstained | The answer explicitly states 'Not in memory,' indicating the model does not know the information rather than providing an incorrect or outdated value. |
| qa-q05 outage_credit | 2026-02-23 | 1 day per full 24 h down | abstained | The answer explicitly states 'Not in memory,' indicating the model does not know the information rather than providing an incorrect or outdated value. |
| qa-q06 refund_window | 2026-02-25 | 14 days | abstained | The answer explicitly states 'Not in memory,' indicating the model does not know the information rather than providing an incorrect or outdated value. |
| qa-q09 fiber_towns | 2026-03-11 | Alder, Brook | abstained | The answer explicitly states 'Not in memory,' indicating the model does not know the information rather than providing an incorrect or outdated value. |
| qa-q10 id_check | 2026-03-14 | Last 4 of SSN | abstained | The answer explicitly states 'Not in memory,' indicating that the model does not know the information rather than providing an incorrect or outdated value. |
| qa-q15 glide_price | 2026-04-29 | $59/mo | abstained | The answer explicitly states 'Not in memory,' indicating the model does not know the fact rather than providing an incorrect or stale value. |
| qa-q16 lite_plan | 2026-05-06 | Lite 25 at $25/mo, open to new signups | abstained | The answer explicitly states 'Not in memory,' indicating the model does not know the information rather than providing a specific incorrect or stale value. |
| qa-q19 big_credit_approver | 2026-05-11 | Supervisor approves outage credits over $100 | abstained | The answer explicitly states 'Not in memory,' indicating that the model does not know the information rather than providing an incorrect or outdated fact. |
| qa-q21 torrent_upload | 2026-05-16 | 50 Mbps | abstained | The answer explicitly states 'Not in memory,' indicating the model does not know the information rather than providing an incorrect or outdated value. |
| qa-q22 payment_methods | 2026-05-18 | Card, bank debit | abstained | The answer explicitly states 'Not in memory,' indicating the model does not know the information rather than providing an incorrect or outdated value. |
| qa-q23 maintenance_window | 2026-05-19 | Tuesday 1 to 4 am | abstained | The answer explicitly states 'Not in memory,' indicating the model does not know the information rather than providing an incorrect or outdated value. |
| qa-q24 tech_visit_fee | 2026-05-24 | $95 | abstained | The answer explicitly states 'Not in memory,' indicating the model does not know the value rather than providing an incorrect or outdated specific number. |
| qa-q27 mesh_max | 2026-06-14 | 3 extenders | abstained | The answer explicitly states 'Not in memory,' indicating the model does not know the fact rather than providing an incorrect or outdated value. |
| qa-q28 support_hours | 2026-06-21 | 8 am to 8 pm | abstained | The answer explicitly states 'Not in memory,' indicating the model does not know the information rather than providing an incorrect or outdated value. |
| qa-q30 agent_refund_limit | 2026-06-30 | $100 | abstained | The answer explicitly states 'Not in memory,' indicating that the model does not know the information rather than providing an incorrect or outdated value. |
| qa-q31 extender_model | 2026-06-30 | QX-1 | abstained | The answer explicitly states 'Not in memory,' indicating the model does not know the information rather than providing an incorrect or outdated value. |
| qa-q34 torrent_download | 2026-08-06 | Torrent 1G downloads at 1,000 Mbps | abstained | The answer explicitly states 'Not in memory,' indicating the model does not know the information rather than providing an incorrect or stale value. |
| qa-q42 router_brand | 2026-10-09 | Customer router is the Q-Box | abstained | The answer explicitly states 'Not in memory,' indicating the model does not know the information rather than providing an incorrect or stale value. |
| qa-q45 hq | 2026-10-30 | Head office in Alder | abstained | The answer explicitly states 'Not in memory,' indicating that the model does not know the information rather than providing an incorrect or outdated fact. |
| qa-q47 payment_methods | 2026-11-07 | Adds PayPal | abstained | The answer explicitly states 'Not in memory,' indicating that the model does not know the information rather than providing an incorrect or outdated value. |
| qa-q49 agent_refund_limit | 2026-11-22 | $75 | abstained | The answer explicitly states 'Not in memory,' indicating that the model does not know the information rather than providing an incorrect or outdated value. |
| qa-q51 status_page | 2026-12-02 | quillmere.example/status | abstained | The answer explicitly states 'Not in memory,' indicating the model does not know the information rather than providing an incorrect or outdated URL. |
| qa-q52 tier2_sla | 2026-12-04 | Within 24 h | abstained | The answer explicitly states 'Not in memory,' indicating the model does not know the information rather than providing an incorrect or outdated value. |
| qa-q54 recording_retention | 2026-12-14 | 60 days | abstained | The answer explicitly states 'Not in memory,' indicating the model does not know the information rather than providing an incorrect or outdated value. |
| qa-q55 grace_period | 2026-12-15 | 21 days | abstained | The answer explicitly states 'Not in memory,' indicating the model does not know the information rather than providing an incorrect or outdated value. |
| qa-q57 move_fee | 2026-12-18 | Free | abstained | The answer explicitly states 'Not in memory,' indicating the model does not know the information rather than providing an incorrect or outdated value. |

Wrong merges: firmware+redlight_fix, agent_refund_limit+missed_appt_credit, agent_refund_limit+modem_fee, agent_refund_limit+big_credit_approver.

Answer time median 276 ms. Spend: answer $0.00, extract $0.00, grade $0.00, jev $0.00.
