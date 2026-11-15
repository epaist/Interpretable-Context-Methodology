<file path="stage-contracts.md">
# Stage Contracts: Podcast Episode Pipeline

Workspace: `podcast-episode/` (booking to published show notes and social posts)
Source: `../01-discovery/output/workflow-map.md`
Rules applied: Pattern 1 (Stage Contracts), Pattern 3 (One-Way Cross-References), Pattern 5 (Canonical Sources), Pattern 11 (Checkpoints), Pattern 12 (Audits), naming conventions.

---

## Dependency Diagram

```
                 USER (per episode)
       guest name + topic + recording date
                        |
                        v
             +---------------------+
             |    01-research      |<---- brand-vault/show-identity.md
             | [slug]-guest-brief  |<---- 01/references/brief-format.md
             +---------------------+
                |              |
                v              |
   +-------------------------+ |
   |      02-outline         |<---- brand-vault/show-identity.md
   | [slug]-interview-outline|<---- brand-vault/voice-rules.md
   +-------------------------+<---- 02/references/outline-format.md
                |              |
       [RECORDING happens outside the workspace]
                |              |
   USER: Descript transcript   |
   (03-cut-list/input/)        |
                |              |
                v              |
   +-------------------------+ |
   |      03-cut-list        |<---- 03/references/cut-categories.md
   |    [slug]-cut-list      |<---- 03/references/descript-export-format.md
   +-------------------------+<---- {{?AUDIO_CLIPS}} 03/references/ffmpeg-setup.md {{/AUDIO_CLIPS}}
                |              |
                v              v
   +---------------------------------+
   |         04-show-notes           |<---- 03-cut-list/input/ transcript
   |       [slug]-show-notes         |<---- brand-vault/show-identity.md, voice-rules.md
   +---------------------------------+<---- {{?SPONSOR}} brand-vault/sponsor-read.md {{/SPONSOR}}
                |                    <---- 04/references/show-notes-format.md
                v
   +---------------------------------+
   |           05-social             |<---- brand-vault/show-identity.md, voice-rules.md
   |      [slug]-social-posts        |<---- shared/platform-specs.md
   +---------------------------------+
                |
                v
          FINAL DELIVERABLES
   (show notes from 04 + social posts from 05)
```

**Edges, all pointing downstream or to Layer 3 references:**

| From (reader) | Reads | Direction check |
|---------------|-------|-----------------|
| 02 | 01 output | forward |
| 03 | 02 output | forward |
| 04 | 03 output, 03 input (transcript), 01 output | forward |
| 05 | 04 output | forward |
| 01 to 05 | brand-vault/, shared/, own references/ | Layer 3, which references nothing |

No stage reads a later stage. `brand-vault/` and `shared/` reference no stage. The graph is acyclic.

---

## Canonical Sources (one home per fact)

| Information | Canonical home | Readers (point, do not copy) |
|-------------|---------------|------------------------------|
| Show name, host name, audience, show format | `brand-vault/show-identity.md` | 01, 02, 04, 05 |
| Voice rules (hard constraints, right/wrong pairs, what the voice is NOT) | `brand-vault/voice-rules.md` | 02, 04, 05 |
| Sponsor name, read text, link (conditional) | `brand-vault/sponsor-read.md` | 04 |
| LinkedIn, X and Instagram length, hashtag and link rules | `shared/platform-specs.md` | 05 |
| Guest brief sections, one-page limit, citation rule | `stages/01-research/references/brief-format.md` | 01 |
| Outline structure (opening, 8 to 12 questions in 3 blocks, closing) and question quality rules | `stages/02-outline/references/outline-format.md` | 02 |
| Cut categories and entry rule (start, end, category, reason) | `stages/03-cut-list/references/cut-categories.md` | 03 |
| Descript text export timestamp format and export steps | `stages/03-cut-list/references/descript-export-format.md` | 03, and 04 reads only the "Timestamp format" section |
| ffmpeg install and clip commands (optional) | `stages/03-cut-list/references/ffmpeg-setup.md` | 03 |
| Show notes sections (summary, chapters, links, pull quote, sponsor) | `stages/04-show-notes/references/show-notes-format.md` | 04 |
| Guest facts and links for this episode | `01-research/output/[slug]-guest-brief.md` | 02, 04 |
| Final question order | `02-outline/output/[slug]-interview-outline.md` | 03 |
| Episode transcript | `03-cut-list/input/[slug]-transcript.txt` | 03, 04 |
| Cut segments | `03-cut-list/output/[slug]-cut-list.md` | 04 |
| Episode summary, chapters, pull quote | `04-show-notes/output/[slug]-show-notes.md` | 05 |

**Episode slug.** Stage 01 sets `[slug]` as `YYYY-MM-DD-guest-lastname` from the recording date and the guest's last name. Its canonical home is the header line of the guest brief. Later stages copy it into their file names and use it to find files. They do not redefine it.

---

## Stage 01: Research

**Purpose:** Turn the guest name and topic into a one-page guest brief with sources.
**Type:** Creative/research. Audit: yes. Checkpoint: yes (fact review).

### Inputs

| Source | File/Location | Section/Scope | Why |
|--------|--------------|---------------|-----|
| User (per episode) | Chat or `input/episode.md` | Guest name, topic, recording date | Subject of the episode, and the source of the slug |
| Brand vault | `../../brand-vault/show-identity.md` | Show name, audience | Frames which angles matter to listeners |
| Stage reference | `references/brief-format.md` | Full file | Sections, one-page limit, citation rule |
| Web or provided material | Public sources | Past interviews, book or company, public statements on the topic | Raw research |

### Process

1. Take the guest name, topic and recording date. Build the slug `YYYY-MM-DD-guest-lastname`.
2. Research past interviews (note the questions the guest is asked most often), the guest's book or company, and public statements on the topic.
3. Draft the brief in the sections from `brief-format.md`: bio, book or company, past interviews, public positions on the topic, possible angles, sources.
4. Attach a source link to every factual claim.
5. **[Checkpoint]** Show the draft. The user corrects or adds facts.
6. Run the audit. Revise if any check fails.
7. Save to output.

### Checkpoints

| After Step | Agent Presents | Human Decides |
|------------|---------------|---------------|
| 4 | Draft brief with sources | Corrections, added facts, angles to drop |

### Audit

| Check | Pass Condition |
|-------|---------------|
| One page | Brief stays at or under the length limit in `brief-format.md` |
| Sections present | Every section from `brief-format.md` is present and filled |
| Cited | Every factual claim has a source link |
| Topic coverage | At least one public position on the episode topic, or the brief states that none was found |
| Common questions noted | The past interviews section lists the guest's most-asked questions |

### Outputs

| Artifact | Location | Format |
|----------|----------|--------|
| Guest brief | `output/[slug]-guest-brief.md` | Markdown with the slug, guest, topic and date in the header, then the fixed sections |

**Consumed by:** 02 (full file), 04 (bio and links).

---

## Stage 02: Outline

**Purpose:** Write the interview outline from the guest brief.
**Type:** Creative. Audit: yes. Checkpoint: required.

### Inputs

| Source | File/Location | Section/Scope | Why |
|--------|--------------|---------------|-----|
| Previous stage | `../01-research/output/[slug]-guest-brief.md` | Full file | Grounds the questions. Supplies the common questions to avoid. |
| Brand vault | `../../brand-vault/show-identity.md` | Show name, host name, format | Opening and closing |
| Brand vault | `../../brand-vault/voice-rules.md` | Full file | Voice for the opening and closing |
| Stage reference | `references/outline-format.md` | Full file | Structure and question rules |

### Process

1. Read the brief and pick three themes for the question blocks.
2. Write 8 to 12 open-ended questions across the three blocks. Ground each one in a fact or angle from the brief.
3. Remove or rework any question that repeats one of the guest's most common past questions.
4. **[Checkpoint]** Present the blocks. The user reorders, adds or cuts questions.
5. Apply the user's changes. Write the opening and the closing in the show's voice.
6. Run the audit. Revise if any check fails.
7. Save to output.

### Checkpoints

| After Step | Agent Presents | Human Decides |
|------------|---------------|---------------|
| 3 | Three question blocks, with the brief source for each question | Order, additions, cuts, block names |

### Audit

| Check | Pass Condition |
|-------|---------------|
| Structure | Opening, three blocks, closing, all present |
| Question count | 8 to 12 questions in total, after the user's edits |
| Open-ended | No question can be answered with yes or no |
| Grounded | Each question traces back to the brief |
| No repeats | No question duplicates a most-asked question from the brief |
| Voice | Opening and closing follow every hard constraint in `voice-rules.md` |
| User review done | The checkpoint ran and the user's changes are applied |

### Outputs

| Artifact | Location | Format |
|----------|----------|--------|
| Interview outline | `output/[slug]-interview-outline.md` | Markdown: opening, Block 1 to 3 with numbered questions, closing |

**Consumed by:** 03 (to tell planned material from tangents). Recording takes place after this stage, outside the workspace.

---

## Stage 03: Cut List

**Purpose:** Mark the transcript segments to remove or handle in the Descript edit.
**Type:** Analytical. Audit: yes. Checkpoint: none (the user adjusts the cut list in Descript afterwards).

### Inputs

| Source | File/Location | Section/Scope | Why |
|--------|--------------|---------------|-----|
| User (per episode) | `input/[slug]-transcript.txt` | Full file | Descript text export with timestamps |
| Previous stage | `../02-outline/output/[slug]-interview-outline.md` | Question blocks | Separates planned material from tangents |
| Stage reference | `references/cut-categories.md` | Full file | Categories and the entry rule |
| Stage reference | `references/descript-export-format.md` | Timestamp format | Parses the timestamps correctly |
| {{?AUDIO_CLIPS}} Stage reference | `references/ffmpeg-setup.md` | Clip command | Clip candidate format {{/AUDIO_CLIPS}} |

### Process

1. Parse the transcript timestamps as described in `descript-export-format.md`.
2. Match each transcript section to an outline question, or mark it as unplanned.
3. Flag tangents (unplanned material off the topic), false starts and ad breaks.
4. For each flag, record the start, end, category and a one-line reason.
5. {{?AUDIO_CLIPS}}List 3 to 5 clip candidates with timestamps and the ffmpeg command for each.{{/AUDIO_CLIPS}}
6. Run the audit. Revise if any check fails.
7. Save to output.

### Audit

| Check | Pass Condition |
|-------|---------------|
| Entry completeness | Every row has a start, end, category and reason |
| Valid categories | The category is one of tangent, false start or ad break |
| Valid timestamps | Start is earlier than end, both fall within the transcript, and they match the export format |
| No overlaps | Cut segments do not overlap |
| Planned material kept | No segment that answers an outline question is cut unless the reason says why |

### Outputs

| Artifact | Location | Format |
|----------|----------|--------|
| Cut list | `output/[slug]-cut-list.md` | Table: start, end, category, reason. Optional clip candidates section. |

**Consumed by:** 04 (to adjust chapter timestamps). The user also uses it in Descript.

---

## Stage 04: Show Notes

**Purpose:** Write publish-ready show notes.
**Type:** Creative. Audit: yes. Checkpoint: yes (the user reviews before publishing).

### Inputs

| Source | File/Location | Section/Scope | Why |
|--------|--------------|---------------|-----|
| User transcript | `../03-cut-list/input/[slug]-transcript.txt` | Full file | Summary, chapters, links, verbatim pull quote |
| Previous stage | `../03-cut-list/output/[slug]-cut-list.md` | Cut table | Chapters skip cut material and use post-edit timing |
| Earlier stage | `../01-research/output/[slug]-guest-brief.md` | Bio, book or company, sources | Guest bio and links |
| Brand vault | `../../brand-vault/show-identity.md` | Show name, host name | Header |
| Brand vault | `../../brand-vault/voice-rules.md` | Full file | Voice |
| {{?SPONSOR}} Brand vault | `../../brand-vault/sponsor-read.md` | Full file | Sponsor section {{/SPONSOR}} |
| User (per episode) | Chat | Sponsor yes or no | Decides whether the sponsor section goes in |
| Stage reference | `references/show-notes-format.md` | Full file | Sections and order |

### Process

1. Ask whether this episode has a sponsor (only if the `SPONSOR` block exists).
2. Remove the cut segments from the timeline and recompute the post-edit timestamps.
3. Write the summary in the show's voice.
4. Build chapter markers from the post-edit timeline.
5. Collect every link or resource mentioned in the episode, and add the guest's links from the brief.
6. Choose a pull quote, copied word for word from a segment that was not cut.
7. {{?SPONSOR}}If this episode has a sponsor, insert the sponsor section from `sponsor-read.md`.{{/SPONSOR}}
8. **[Checkpoint]** Present the draft for user review.
9. Run the audit. Revise if any check fails.
10. Save to output.

### Checkpoints

| After Step | Agent Presents | Human Decides |
|------------|---------------|---------------|
| 7 | Full show notes draft | Edits to the summary, chapters and quote, and approval to publish |

### Audit

| Check | Pass Condition |
|-------|---------------|
| Sections | Summary, chapters, links and pull quote are present, plus the sponsor section only when there is a sponsor |
| Chapter timing | No chapter starts inside a cut segment. Timestamps go up in order. |
| Verbatim quote | The pull quote matches the transcript exactly and comes from material that was not cut |
| Links | Every link mentioned in the transcript is listed. Guest links match the brief. |
| Voice | Follows every hard constraint in `voice-rules.md` |
| Sponsor correctness | The sponsor text matches `sponsor-read.md` word for word, or is absent when there is no sponsor |

### Outputs

| Artifact | Location | Format |
|----------|----------|--------|
| Show notes | `output/[slug]-show-notes.md` | Markdown in the order set by `show-notes-format.md` |

**Consumed by:** 05. It is also a final deliverable (published).

---

## Stage 05: Social

**Purpose:** Write one promotional post each for LinkedIn, X and Instagram.
**Type:** Creative. Audit: yes. Checkpoint: yes.

### Inputs

| Source | File/Location | Section/Scope | Why |
|--------|--------------|---------------|-----|
| Previous stage | `../04-show-notes/output/[slug]-show-notes.md` | Summary, pull quote, guest name, links | Post content |
| Brand vault | `../../brand-vault/show-identity.md` | Show name, host name, audience | Framing |
| Brand vault | `../../brand-vault/voice-rules.md` | Full file | Voice |
| Shared | `../../shared/platform-specs.md` | Full file | Length limits, hashtag and link rules |

### Process

1. Pull the hook, the pull quote and the guest details from the show notes.
2. Draft the LinkedIn post to its platform spec.
3. Draft the X post to its platform spec.
4. Draft the Instagram caption to its platform spec.
5. **[Checkpoint]** Present all three posts. The user edits them.
6. Run the audit. Revise if any check fails.
7. Save to output.

### Checkpoints

| After Step | Agent Presents | Human Decides |
|------------|---------------|---------------|
| 4 | Three draft posts | Edits, choice of hook, approval |

### Audit

| Check | Pass Condition |
|-------|---------------|
| Three posts | LinkedIn, X and Instagram sections are all present |
| Platform limits | Each post is within the length limit and follows the hashtag and link rules in `platform-specs.md` |
| Voice | Each post follows every hard constraint in `voice-rules.md` |
| Accuracy | Any quote matches the show notes pull quote. Guest name and topic match the show notes. |

### Outputs

| Artifact | Location | Format |
|----------|----------|--------|
| Social posts | `output/[slug]-social-posts.md` | Three H2 sections: LinkedIn, X, Instagram |

**Consumed by:** None. Final deliverable.

---

## Output Consumption Check

| Stage output | Consumed by |
|--------------|-------------|
| 01 guest brief | 02, 04 |
| 02 interview outline | 03 |
| 03 cut list | 04 |
| 04 show notes | 05, plus final deliverable |
| 05 social posts | Final deliverable |

---

## Audit Results (Stage 02)

| Check | Result |
|-------|--------|
| No circular references | **Pass.** All stage edges point forward (01 to 02, 02 to 03, 03 to 04, 01 to 04, 04 to 05). Layer 3 files reference no stage. |
| Output consumption | **Pass.** 01 through 04 are each read downstream. 04 and 05 are final deliverables. |
| Contract completeness | **Pass.** All five stages have Inputs, Process and Outputs with no empty fields. Audit and Checkpoint sections are included where they apply. |
| Canonical sources | **Pass.** Each fact has one home, listed in the canonical table. The transcript lives only in `03-cut-list/input/`, and 04 points there. The slug is defined only in the guest brief. |

---

## Assumptions

- **Step 7 checkpoint:** A live review was not possible. The diagram and contracts are approved as drafted, because they follow the user's stated sequence and the discovery map without changes in structure.
- **Transcript home:** The transcript has one canonical location, `03-cut-list/input/`. Stage 04 reads it there instead of keeping a second copy, which follows Pattern 5. Reading another stage's input folder still flows forward, so it is allowed.
- **03 to 04 timestamps:** Stage 04 recomputes post-edit timestamps by removing the cut segments. It assumes the user applies the cut list in Descript more or less as written. If the user changes the cuts, they should edit the cut-list output before running stage 04 (Pattern 2).
- **Checkpoints added beyond the user's explicit one:** The outline checkpoint is required by the user. Fact review (01), show notes review (04) and social review (05) were added because they are creative stages (Pattern 11) and the discovery map names them as handoff points. Stage 03 has no checkpoint because the user adjusts the cuts in Descript.
- **Slug format** `YYYY-MM-DD-guest-lastname` was chosen to meet the `[topic-slug]-[artifact].md` naming convention for a weekly show.
- **`{{SHOW_AUDIENCE}}`** is kept, because 01 and 05 both use it.
- **Per-episode sponsor flag** is asked at stage 04 step 1 and is never stored as a placeholder.
- **Clip candidates** are limited to 3 to 5 as a proposed default, and only when `AUDIO_CLIPS` is enabled.
- **Reference file names** (`brief-format.md`, `outline-format.md`, `cut-categories.md`, `descript-export-format.md`, `ffmpeg-setup.md`, `show-notes-format.md`) are proposed for stage 03 scaffolding to create.
</file>