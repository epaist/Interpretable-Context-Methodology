# Memory Stream Spec

Books do not change; memory does. This test material is a dated stream of records that the memory store learns from in order.

## The Company

Quillmere Broadband: a made-up regional home-internet provider. Its facts keep changing (plan prices, outage fixes, refund rules), which is what memory has to handle. Everything is generated, so nothing private is involved.

## Phases (isolate first, then mix)

| Phase | Records | What it tests |
|-------|---------|---------------|
| A | Customer tickets and call logs only | Old vs new facts, merging duplicates, questions pinned to a date |
| B | A plus versioned SOPs and governance rules | Which rule applied on which date; tickets that cite or break a rule get flagged |
| C | B plus noise: meeting notes, announcements | What mixing costs (the drop from B to C) |

A failure in A points to one cause. Starting with variety would hide which part broke.

## Size and Plants (whole stream)

- About 300 dated records, about 200k tokens.
- About 40 facts that change partway through (superseded facts).
- The same fact written several different ways (rephrased duplicates).
- About 10 records that contradict each other.
- Facts asked about often, which should be summarized one layer up (promotion).
- Facts never asked about again, which should move to a cold tier.
- Time-stamped questions, such as "as of record 120, what is the refund window?"

## Optional Real-World Check

Replay this project's own decisions as a second stream. Local judge only, unless the user approves the cloud.

## Store Scope

One memory store per workspace (Bee, 2026-11-02). Sharing across ICM is tested only after the per-workspace store passes.
