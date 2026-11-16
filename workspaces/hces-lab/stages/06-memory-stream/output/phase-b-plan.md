# Quillmere Phase B Plan

Phase B adds the documents that make a change official. Phase A memory took every ticket at face value, so a record that stated the next value early (firmware 4.3 on 08-10) became current. Phase B tests whether memory can rank sources: a dated SOP or governance version outranks what a ticket says.

## Records (about 90 new, written by Opus from a code plan, as in phase A)

| Kind | Count | Content |
|------|-------|---------|
| SOP and governance versions | 33 | SOP-01 to SOP-04 and GOV-01 to GOV-03, every version in the company sheet. Each version states all the facts its document owns, with the version's effective date. About 450 words. |
| Tickets that cite an SOP | about 57 | Agents quote a rule and name the SOP and version. Most cite the version in force; planted ones cite a stale version (contradiction c: SOP-02 v5 cited on 10-20 while v6 is live) or paraphrase it wrongly. |

27 keys belong to an SOP. The other 13 (support phone, payment methods, fiber towns and so on) still come only from tickets in phase B, so their early claims stay unfixed until phase C announcements.

## Memory Changes (code, no spend)

- Canonical keys as in run a4.
- Source rank: each fact records its source kind (sop, governance, ticket, call log) from its record. For a key with any SOP or governance fact in force at the question date, the current value is the latest such fact by effective date. A ticket value that differs from the SOP in force is kept as history and never becomes current. Keys with no SOP keep the phase A rule (latest by date, reversion guard).
- Notes show the SOP and version behind a current value, so answers can cite it.
- Unit tests for the rank rule before any spend.

## Questions (about 60, from the ledger by code)

| Kind | About | Example |
|------|-------|---------|
| Current value, SOP-owned key | 27 | As of 2026-08-15, what is the firmware version? (4.3 starts 08-20, so 4.2) |
| Current value, ticket-only key | 13 | As of 2026-05-18, which payment methods are accepted? |
| SOP version in force | 7 | Which version of SOP-02 applies on 2026-10-20? (v6) |
| Stale citation | 5 | A ticket cites SOP-02 v5 on 10-20: what is the refund window that day? (21 days) |
| Stable control | 6 | Does Glide 500 have a data cap? |

Each question is asked when the replay reaches its date, as in phase A.

## Bars

Same as phase A: current fact correct at least 95%, superseded value returned as current never, wrong merges none. Also reported: SOP-owned keys and ticket-only keys separately, so the effect of source rank is visible.

## Replay

Recommended: replay phase A and phase B records together, in date order, into a fresh store. Then each record's extraction sees only the keys memory held at that date, and the run is a clean test.

Cheaper option: copy the run a4 store and add only the phase B records. This saves about $1.20 of extraction, but phase B records dated early in the year would see key names taken from later phase A records. That makes the test easier than real use.

## Cost and Time (from phase A actuals)

| Step | Full replay | Copy a4 |
|------|-------------|---------|
| Write about 90 records (SOPs about 650 output tokens each, tickets about 350) | $0.90 | $0.90 |
| Extract with keys (phase A ran $0.010 per record; SOP versions hold about 7 facts each, about $0.03) | $2.90 | $1.70 |
| JEV key checks | $0.05 | $0.05 |
| Answer and grade about 60 questions | $0.45 | $0.45 |
| Total Claude | about $4.25, cap $5.00 | about $3.05, cap $3.60 |

Machine time about 30 minutes for the full replay.
