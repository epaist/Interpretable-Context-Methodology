# Quillmere Phase A Scorecard (run a4)

57 dated questions, each asked when the replay reached its date. 184 facts from 122 records; 96 fact groups.

| Bar | Result | Pass |
|-----|--------|------|
| Current fact correct, at least 95% | 51 of 57 (89%) | FAIL |
| Superseded fact returned as current: never | 2 | FAIL |
| Wrongly merged facts: none | 2 groups | FAIL |

| Question kind | Correct | Stale | Wrong | Abstained |
|---|---|---|---|---|
| contradiction | 4 of 5 | 1 | 0 | 0 |
| current | 37 of 40 | 1 | 2 | 0 |
| hot | 5 of 6 | 0 | 1 | 0 |
| stable | 5 of 6 | 0 | 0 | 1 |

## Misses

| Question | As of | Expected | Verdict | Reason |
|---|---|---|---|---|
| qa-q10 id_check | 2026-03-14 | Last 4 of SSN | wrong | The answer names 'name and service address' as the current method. That is neither the expected value (Last 4 of SSN) nor the other known value (Account PIN). I |
| qa-q22 payment_methods | 2026-05-18 | Card, bank debit | stale | The answer presents PayPal as the current method and treats card and bank debit as possibly outdated. PayPal is the value from another time, and the expected va |
| qa-q35 firmware | 2026-08-12 | 4.2 | stale | The answer gives 4.3 as the current version. 4.3 is one of the values the fact held at another time, not the expected 4.2. The answer also treats 4.2 as older. |
| qa-q36 refund_window | 2026-08-14 | 30 days | wrong | The answer gives "one full month" for the main refund window, which is not the same as the expected 30 days. It only mentions 30 days as a separate window for a |
| qa-q37 contract_terms | 2026-08-24 | 12 or 24 months | wrong | The answer says plans are month-to-month with no long contract. That matches neither the expected '12 or 24 months' nor the earlier '12 months only'. It explici |
| qa-q42 router_brand | 2026-10-09 | Customer router is the Q-Box | abstained | The answer says the information is not in memory, which is a statement of not knowing. It does not name any router, so it neither matches the expected Q-Box nor |

Wrong merges: contract_none+contract_terms, agent_refund_limit+big_credit_approver.

Answer time median 1624 ms. Spend: answer $0.22, extract $1.23, grade $0.16, jev $0.00.

## Audit (2026-11-02, run a4: canonical keys)

New extraction: the extractor sees the keys memory holds and reuses one or names a new one; JEV only checks the new fact against earlier facts of its key (veto below 0.5). Also told that offers made to a customer are company facts. Spend $1.61 Claude (extraction $1.23, $0.40 over estimate because the key list grows each record; answers $0.22; grading $0.16), JEV $0.004. Phase A total $4.75 Claude across runs a to a4.

| Run | Grouping | Correct | Stale | Wrong merges |
|---|---|---|---|---|
| a | every link at 0.5 | 50 of 57 | 2 | 4 |
| a2 | best match at 0.5 | 51 of 57 | 2 | 4 |
| a3 | best match at 0.9 | 50 of 57 | 2 | 0 |
| a4 | canonical keys, JEV check | 51 of 57 | 2 | 2 |

Fixed by keys: retention offer (q08), price lock (q18), Glide cap (q48), and the support number no longer splits (q17, q26, q38 right).

Remaining misses:

| Cause | Misses | Detail |
|---|---|---|
| Early claim | q22, q35 | Same as every run: PayPal and firmware 4.3 stated before they start. Phase B SOP dates. |
| Lookalike under one key | q37 | The extractor put month-to-month (stable) and contract term options under one key; JEV did not veto. Agent refund limit and big-credit approver also share a key (no question missed). |
| Side fact | q10 | A written record also says agents check name and service address; the extractor keyed it as the identity check, so it replaced last 4 of SSN. |
| Grader | q36 | Memory answered "one full month" (the record's own wording for 30 days) and also named a 30-day add-on window; the grader marked it wrong. |

Keys removed the grouping failures that came from JEV alone. What is left is the extractor's judgment on lookalikes, early claims, and one grading call.
