# Quillmere Phase A Scorecard

57 dated questions, each asked when the replay reached its date. 192 facts from 122 records; 73 fact groups.

| Bar | Result | Pass |
|-----|--------|------|
| Current fact correct, at least 95% | 50 of 57 (88%) | FAIL |
| Superseded fact returned as current: never | 2 | FAIL |
| Wrongly merged facts: none | 4 groups | FAIL |

| Question kind | Correct | Stale | Wrong | Abstained |
|---|---|---|---|---|
| contradiction | 4 of 5 | 1 | 0 | 0 |
| current | 36 of 40 | 1 | 1 | 2 |
| hot | 6 of 6 | 0 | 0 | 0 |
| stable | 4 of 6 | 0 | 0 | 2 |

## Misses

| Question | As of | Expected | Verdict | Reason |
|---|---|---|---|---|
| qa-q08 retention_offer | 2026-03-02 | 3 months at 25% off | abstained | The answer says the information is not in memory, so it gives no value and declines to answer. |
| qa-q18 price_lock | 2026-05-09 | 12 months | abstained | The answer says the information is not in memory, which is a refusal to give any value. |
| qa-q22 payment_methods | 2026-05-18 | Card, bank debit | stale | The answer names PayPal, which matches the other-time value "Adds PayPal". It does not give the expected card and bank debit. |
| qa-q35 firmware | 2026-08-12 | 4.2 | stale | The answer gives 4.3, which is one of the fact's values at another time, not the expected 4.2 for this date. It also claims 4.3 replaced 4.2, which is not the c |
| qa-q37 contract_terms | 2026-08-24 | 12 or 24 months | wrong | The answer gives month-to-month with an optional 12-month term. That is neither the expected 12 or 24 months nor the earlier value of 12 months only. |
| qa-q42 router_brand | 2026-10-09 | Customer router is the Q-Box | abstained | The answer says the information is not in memory, which is a statement of not knowing rather than an attempt to name the router. |
| qa-q48 glide_cap | 2026-11-22 | Glide 500 has no data cap | abstained | The answer says the information is not in memory, which is a statement of not knowing rather than an answer about the data cap. |

Wrong merges: glide_cap+overage_fee+spark_cap, firmware+redlight_fix, agent_refund_limit+big_credit_approver+outage_credit, contract_none+contract_terms+price_lock.

Answer time median 1726 ms. Spend: answer $0.18, extract $0.80, grade $0.16, jev $0.08.

## Audit (2026-11-02)

Spend: Claude $2.34 (writing $1.12, of which $0.07 was a batch that failed the quote check and was rerun; extraction $0.80; answers $0.18; grading $0.16). JEV $0.08 for about 3,700 link requests. Machine time about 25 minutes.

Every miss traced to the record, the stored facts and the notes the answer saw:

| Cause | Misses | Detail |
|---|---|---|
| Wrong merge | q18, q37, q48 | Union of every same_attribute link chains groups together. Price lock and contract terms joined the stable month-to-month fact, so "month-to-month" became their current value. Glide 500 cap joined the Spark cap and overage group, and the Glide fact dropped out of the notes. |
| Early claim taken as current | q22, q35 | A record states the next value before it starts (PayPal on 05-12, firmware 4.3 on 08-10), with no effective date. The reversion guard only blocks rollbacks. Predicted before the run. |
| Extraction skipped a fact | q08 | The only record before the question offers a customer the retention deal; the extractor read it as customer-specific and kept no fact. |
| Retrieval | q42 | The Q-Box fact is stored, but it was not among the 4 groups nearest the question. |

Hot facts 6 of 6 and the stale-quote contradictions (refund window, support phone, outage credit) all passed: the reversion guard works.

Fixes to test, in order: join a new fact to the group of its single best same_attribute match instead of chaining every link; give the answer 8 groups instead of 4; tell the extractor that offers and terms an agent gives a customer are company facts. Early claims need a source with authority (phase B SOP effective dates) or a confirmation rule, and stay open.
