# Knowledge Base

Large plain-text volumes for testing the bottom of the hierarchy. Agents do not read volumes directly; code does.

| Folder | Contains | Written by |
|--------|----------|-----------|
| `volumes/` | One folder per volume: `source.txt` (as downloaded), `plain.txt` (book text with needles planted), `chaptered.txt`, `chapters.jsonl`, `passages.jsonl`, `README.md` | Stage 02 |
| `index/` | Vector and keyword index per volume and shape | Stage 03 |
| `streams/` | One folder per memory stream, one subfolder per phase, `records.jsonl` | Stage 06 |

## Passage Records

Each line of `passages.jsonl` is one passage: `id`, `volume`, `shape`, `chapter`, `start_char`, `end_char`, `tokens`, `source_hash`, `parent_id`. IDs never change once written; a changed source gets a new hash and new IDs. A passage is at most 512 tokens, the embedder's limit.

## Streams

Each line of `records.jsonl` is one dated record: `id`, `stream`, `phase`, `date`, `kind` (ticket, call log, SOP, governance, noise), `text`, `version` (SOPs and rules only). Records are replayed in date order, never loaded whole.

## Rules

- Volumes: public domain only (Project Gutenberg), with the source URL in each volume's `README.md`. Streams: generated only.
- Planted needles are recorded in stage 02 output, never only in the text.
- Load passages by ID through `hces/`, not by opening files into context.
