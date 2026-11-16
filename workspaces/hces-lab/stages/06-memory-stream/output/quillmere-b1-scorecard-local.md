# Quillmere Phase B Scorecard (run b1)

58 dated questions, each asked when the replay reached its date. 500 facts from 222 records; 203 fact groups.

| Bar | Result | Pass |
|-----|--------|------|
| Current fact correct, at least 95% | 47 of 58 (81%) | FAIL |
| Superseded fact returned as current: never | 3 | FAIL |
| Wrongly merged facts: none | 7 groups | FAIL |

| Question kind | Correct | Stale | Wrong | Abstained |
|---|---|---|---|---|
| doc version | 3 of 7 | 1 | 2 | 1 |
| sop key | 23 of 27 | 1 | 0 | 3 |
| stable | 5 of 6 | 0 | 1 | 0 |
| stale citation | 5 of 5 | 0 | 0 | 0 |
| ticket key | 11 of 13 | 1 | 0 | 1 |

## Misses

| Question | As of | Expected | Verdict | Reason |
|---|---|---|---|---|
| qb-q13 big_credit_approver | 2026-02-21 | Supervisor approves outage credits over $100 | abstained | The answer explicitly states that the information is not specified in the provided notes, whereas the expected answer confirms a specific authority ('Supervisor |
| qb-q14 sop_01_version | 2026-02-21 | v2 | wrong | The answer states that version one (v1) is in force, but the expected value is v2. Since v1 is listed as one of the 'other values at other times' and not the ex |
| qb-q15 redlight_fix | 2026-02-28 | Power-cycle the Q-Box | abstained | The answer explicitly states 'Not in memory,' indicating the model does not know the information rather than providing an incorrect or outdated specific value. |
| qb-q19 gov_01_version | 2026-04-02 | v2 | abstained | The answer explicitly states 'Not in memory,' indicating the model does not know the fact rather than providing an incorrect or stale value. |
| qb-q25 sop_04_version | 2026-05-13 | v3 | stale | The answer provides 'v1', which is listed in the 'Other values at other times' rather than the expected value 'v3'. |
| qb-q29 tier2_sla | 2026-06-24 | Callback within 48 h | abstained | The answer explicitly states 'Not in memory,' indicating the model does not know the information rather than providing an incorrect or outdated value. |
| qb-q43 torrent_download | 2026-10-01 | Torrent 1G downloads at 1,000 Mbps | wrong | The answer provides a specific value (200 Mbps) that contradicts the expected value (1,000 Mbps). Since the expected value is the only known fact provided, the  |
| qb-q44 agent_refund_limit | 2026-10-05 | $100 | stale | The answer provides '$50', which corresponds to one of the 'Other values at other times' rather than the expected value of '$100'. |
| qb-q47 id_check | 2026-10-18 | Account PIN | abstained | The answer explicitly states 'Not in memory,' indicating that the model does not know the information rather than providing an incorrect or outdated value. |
| qb-q50 sop_02_version | 2026-10-21 | v6 | wrong | The answer states that version 5 is in force, but the expected value is version 6. Since version 5 is listed as one of the 'other values at other times' and not |
| qb-q53 paperless_credit | 2026-11-08 | Ended | stale | The answer provides the value '$2/mo', which corresponds to the 'Other values at other times'. However, the 'Expected' value for the fact as of 2026-11-08 is 'E |

Wrong merges: firmware+redlight_fix, sop_02_version+sop_03_version, sop_01_version+sop_04_version, install_fee+lite_plan+sop_04_version, late_fee+sop_01_version, modem_fee+sop_01_version, modem_fee+sop_01_version.

Answer time median 569 ms. Spend: answer $0.00, extract $0.00, grade $0.00, jev $0.02.
