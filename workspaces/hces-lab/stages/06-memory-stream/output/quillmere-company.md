# Quillmere Broadband: Company Sheet

Made-up regional home-internet provider for the stage 06 memory test. Every fact below is invented. The stream runs 2026-01-05 to 2026-12-18, about 300 dated records. One memory store for this workspace (Bee, 2026-11-02).

## Stable Facts (never change: control set)

| Key | Value |
|-----|-------|
| hq | Head office in Alder |
| founded | 2009 |
| glide_cap | Glide 500 has no data cap |
| torrent_download | Torrent 1G downloads at 1,000 Mbps |
| router_brand | Customer router is the Q-Box |
| billing_day | Bills issue on the 1st of each month |
| email_support | support@quillmere.example |
| contract_none | Month-to-month is available on every plan |

## Changing Facts (40 planted changes)

Dates are the official start of the new value. Phase A shows each change only through what tickets and call logs say; phase B adds the SOP or rule that made it official.

| # | Key | Old value | New value (from date) | Later value (from date) |
|---|-----|-----------|-----------------------|-------------------------|
| 1 | spark_price | $39/mo | $42 (03-01) | $44 (09-01) |
| 2 | glide_price | $59/mo | $55 (06-01) | |
| 3 | torrent_price | $79/mo | $85 (03-01) | |
| 4 | torrent_upload | 50 Mbps | 200 Mbps (07-15) | |
| 5 | spark_cap | 1.2 TB | No cap (05-01) | |
| 6 | lite_plan | Lite 25 at $25/mo, open to new signups | Closed to new signups (08-01) | Existing Lite moved to Spark (11-01) |
| 7 | overage_fee | $10 per 50 GB | $15 per 50 GB (04-01) | |
| 8 | modem_fee | $10/mo | $12/mo (03-01) | $0 for Torrent, $12 others (10-01) |
| 9 | install_fee | $99 | Free with 12-month contract (02-15) | $49 for everyone (08-01) |
| 10 | etf | $150 flat | $10 per remaining month (06-01) | |
| 11 | senior_discount | $5/mo | $8/mo (07-01) | |
| 12 | paperless_credit | $2/mo | Ended (04-15) | |
| 13 | refund_window | 14 days | 30 days (04-01) | 21 days (10-15) |
| 14 | outage_credit | 1 day per full 24 h down | Hourly, after 4 h down (06-15) | |
| 15 | late_fee | $5 | $8 (03-01) | |
| 16 | grace_period | 30 days before suspension | 21 days (09-01) | |
| 17 | reconnect_fee | $25 | Waived (02-01) | |
| 18 | price_lock | 12 months | 24 months for new signups (05-15) | |
| 19 | support_hours | 8 am to 8 pm | 24/7 (07-01) | |
| 20 | support_phone | 1-800-555-0142 | 1-888-555-0177 (04-20) | |
| 21 | tier2_sla | Callback within 48 h | Within 24 h (08-15) | |
| 22 | tech_visit_fee | $75 (customer-caused fault) | $95 (03-01) | |
| 23 | move_fee | $50 | Free (11-01) | |
| 24 | payment_methods | Card, bank debit | Adds PayPal (06-01) | |
| 25 | autopay_discount | $3/mo | $5/mo (02-01) | |
| 26 | redlight_fix | Power-cycle the Q-Box | Firmware 4.2 update (03-10) | Replace unit if batch QB-2 (06-05) |
| 27 | firmware | 4.1 | 4.2 (03-10) | 4.3 (08-20) |
| 28 | status_page | status.quillmere.example | quillmere.example/status (05-05) | |
| 29 | fiber_towns | Alder, Brook | Adds Calder (04-01) | Adds Dunmore (10-01) |
| 30 | maintenance_window | Tuesday 1 to 4 am | Sunday 2 to 5 am (07-01) | |
| 31 | extender_model | QX-1 | QX-2 (09-01) | |
| 32 | mesh_max | 3 extenders | 5 extenders (09-01) | |
| 33 | agent_refund_limit | Up to $50 without approval | $100 (05-01) | $75 (10-15) |
| 34 | retention_offer | 3 months at 25% off | 2 months at 30% off (08-01) | |
| 35 | recording_consent | Script v1 | Script v2 (06-01) | |
| 36 | recording_retention | 90 days | 60 days (09-01) | |
| 37 | id_check | Last 4 of SSN | Account PIN (03-15) | |
| 38 | missed_appt_credit | $20 | $30 (07-01) | |
| 39 | big_credit_approver | Supervisor approves outage credits over $100 | Billing team lead (06-15) | |
| 40 | contract_terms | 12 or 24 months | 12 months only (12-01) | |

40 keys, 9 with a second change: 49 transitions in total.

## SOPs and Governance (phase B)

| Doc | Versions (effective) | Facts it owns |
|-----|---------------------|---------------|
| SOP-01 Billing and fees | v1 (01-01), v2 (02-01), v3 (03-01), v4 (04-01), v5 (09-01), v6 (10-01) | 1, 3, 7, 8, 15, 16, 25 |
| SOP-02 Refunds and credits | v1 (01-01), v2 (04-01), v3 (05-01), v4 (06-15), v5 (07-01), v6 (10-15) | 13, 14, 33, 38, 39 |
| SOP-03 Red light and outages | v1 (01-01), v2 (03-10), v3 (05-05), v4 (06-05), v5 (07-01), v6 (08-20) | 26, 27, 28, 30 |
| SOP-04 Sales and plans | v1 (01-01), v2 (02-15), v3 (05-01), v4 (05-15), v5 (06-01), v6 (08-01), v7 (11-01), v8 (12-01) | 2, 5, 6, 9, 10, 18, 40 |
| GOV-01 Customer identity | v1 (01-01), v2 (03-15) | 37 |
| GOV-02 Call recording | v1 (01-01), v2 (06-01), v3 (09-01) | 35, 36 |
| GOV-03 Retention offers | v1 (01-01), v2 (08-01) | 34 |

Facts 4, 11, 12, 17, 19 to 24, 29, 31 and 32 (13 keys) have no SOP: tickets show them in every phase, and phase C announcements state them. Each SOP version above lines up with a change date in the table.

## Other Plants

| Plant | Count | Detail |
|-------|-------|--------|
| Rephrased duplicates | about 60 records | Same fact in different words ("two weeks to get your money back" = 14-day refund window); must merge, not count twice |
| Near-miss lookalikes | 8 pairs | Facts that must NOT merge: Spark price vs Spark cap, modem fee vs tech visit fee, refund window vs grace period, agent refund limit vs big-credit approver, support phone vs status page, install fee vs move fee, firmware vs extender model, senior vs autopay discount |
| Contradictions | 10 | (a) agent quotes old refund window after 04-01 (twice); (b) two tickets on 06-20 disagree on outage credit; (c) a ticket on 10-20 cites SOP-02 v5 (30-day refunds) while v6 is live; (d) customer claims PayPal before 06-01; (e) announcement says Calder fiber 03-15, SOP says 04-01; (f) agent waives a $95 visit fee over their limit; (g) call log says firmware 4.3 on 08-10, ten days early; (h) two call logs give different support numbers on 04-22; (i) noise memo floats a $46 Spark price that never ships |
| Hot facts (promote) | 6 | refund_window, spark_price, support_phone, outage_credit, redlight_fix, agent_refund_limit: asked about again and again |
| Cold facts | 5 | paperless_credit, senior_discount, recording_consent, mesh_max, reconnect_fee: mentioned once or twice, then never asked |

The ledger marks contradiction (i) as never valid: the right answer at every date ignores the $46 price.

## Questions (planned)

About 60 per phase, each pinned to a date or a record number, with the expected value from the ledger:

- Current value: "As of 2026-05-10, what is the refund window?" (30 days)
- Before and after a change: "What did Spark 100 cost on 2026-02-20?" ($39)
- Two changes in: "As of record 260, what is the agent refund limit?" ($75)
- Stable control: "Does Glide 500 have a data cap?" (no, at every date)
- Contradiction: "On 2026-06-20, how were outage credits calculated?" (hourly after 4 h, from 06-15)
- Lookalike: "What is the late fee as of 2026-09-15?" ($8, not the grace period)
- Never valid: "Has Spark 100 ever cost $46?" (no)

## Size Plan

| Phase | Records | Approx. tokens | Kinds |
|-------|---------|----------------|-------|
| A | about 110 | about 65k | Tickets, call logs |
| B | adds about 90 | adds about 70k | SOP and governance versions, tickets that cite them |
| C | adds about 100 | adds about 65k | Meeting notes, announcements, newsletters, off-topic chatter |
