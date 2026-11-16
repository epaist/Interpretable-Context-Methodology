<file path="stage-contracts.md">
# Stage Contracts: Podcast Episode Pipeline

Formal Inputs/Process/Outputs contracts for the five stages of the podcast workspace. Source: `../01-discovery/output/workflow-map.md`. Stage 03 scaffolding builds the workspace from this file.

Note on file names: output artifacts follow `[topic-slug]-[artifact-type].md`. The topic slug for this workspace is the **episode slug**, built from the guest name and recording date (for example `jane-doe-2025-06-12`). Stage 01 sets it and every later stage reuses it. In the tables below it is written `[episode-slug]`.

---

## Dependency Diagram

```
                 brand-vault/show-identity.md ----+------+------+------+
                 brand-vault/voice-rules.md ------|------+------+------+
                 brand-vault/sponsor-read.md -----|------|------+      |   (optional)
                 shared/platform-specs.md --------|------|------|------+
                                                  v      v      v      v
 user: guest, topic, date
        |
        v
 [01-research] --guest-brief--> [02-outline] --interview-outline--+
        |                         (checkpoint)                    |
        |                                                         |
        |                    [recording, outside workspace]       |
        |                                                         |
        |      user: Descript transcript                          |
        |              |                                          |
        |              v                                          v
        |         stages/03-cut-list/input/ ---------------> [03-cut-list] --cut-list--+
        |              |                                                               |
        |              +-------------------------------------------+                   |
        |                                                          v                   v
        +--------------------------guest-brief--------------> [04-show-notes] <--------+
                                                                   |   (checkpoint)
                                                                   v
                                                              show-notes
                                                                   |
                                                                   v
                                                             [05-social]  (checkpoint)
                                                                   |
                                                                   v
                                                          social-posts (FINAL)
```

All arrows run from a lower stage number to a higher one, or from Layer 3 shared files into stages. Shared files never point at stages. No stage points back at an earlier stage's folder for anything except reading its `output/` (or, for stage 04, stage 03's `input/`; see Cross-References).

---

## Stage 01: Research

**Responsibility:** Turn a guest name and topic into a one-page guest brief.

### Inputs

| Source | File/Location | Section/Scope | Why |
|--------|--------------|---------------|-----|
| User (per episode) | Conversation at stage start | Guest name, topic, recording date, sponsor yes/no | Run inputs for this episode |
| Show identity | `../../brand-vault/show-identity.md` | "Show" and "Audience" sections | Frame research for the show's listeners |
| Brief format | `references/brief-format.md` | Full file | Fixed sections, one-page length, citation rule |
| Research sources guide | `references/research-sources.md` | Full file | Source types to cover: past interviews, book or company, public statements on the topic |

### Process

1. Collect guest name, topic, recording date and whether this episode has a sponsor. Build the episode slug.
2. Record these in the brief's "Episode" header so later stages read them from one place.
3. Research the guest's bio, book or company, past interviews and public statements on the topic.
4. Note the guest's most common past questions and answers.
5. Draft the brief in the fixed sections from `brief-format.md`, with a source link for every claim.
6. Propose three to five possible interview angles.
7. **[Checkpoint]** Present the draft brief. The user corrects or adds facts.
8. Run the audit and save.

### Checkpoints

| After Step | Agent Presents | Human Decides |
|------------|---------------|---------------|
| 6 | Draft guest brief with sources and angles | Which facts to correct, add or drop; which angles to keep |

### Audit

| Check | Pass Condition |
|-------|---------------|
| One page | Brief fits the length limit in `brief-format.md` |
| Sections | Every section from `brief-format.md` is present |
| Citations | Every factual claim has a source link |
| Episode header | Guest, topic, date, slug and sponsor yes/no are filled in |

### Outputs

| Artifact | Location | Format |
|----------|----------|--------|
| Guest brief | `output/[episode-slug]-guest-brief.md` | Markdown: Episode header, Bio, Book or Company, Past Interviews (incl. common questions), Public Positions on the Topic, Possible Angles, Sources |

---

## Stage 02: Outline

**Responsibility:** Turn the guest brief into an interview outline the host records from.

### Inputs

| Source | File/Location | Section/Scope | Why |
|--------|--------------|---------------|-----|
| Previous stage | `../01-research/output/[episode-slug]-guest-brief.md` | Full file | Guest facts, angles, common past questions |
| Show identity | `../../brand-vault/show-identity.md` | "Show" and "Host" sections | Host name and show name for the opening and closing |
| Voice rules | `../../brand-vault/voice-rules.md` | "Hard Constraints" through "What the Voice Is NOT" | Tone of the opening and closing |
| Outline format | `references/outline-format.md` | Full file | Opening, 8 to 12 questions in three blocks, closing |
| Question rules | `references/question-rules.md` | Full file | Open-ended, grounded in the brief, no repeats of common past questions |

### Process

1. Read the brief and pick the angles to carry into the three blocks.
2. Draft 8 to 12 questions across three blocks, each tied to a brief section.
3. Check each question against the guest's common past questions and replace repeats.
4. **[Checkpoint]** Present the three blocks. The user reviews, reorders, adds or cuts questions.
5. Write the opening and closing in the show's voice around the approved questions.
6. Run the audit and save.

### Checkpoints

| After Step | Agent Presents | Human Decides |
|------------|---------------|---------------|
| 3 | Three question blocks with the brief source of each question | Order, additions, cuts and block assignment (required every episode) |

### Audit

| Check | Pass Condition |
|-------|---------------|
| Question count | 8 to 12 questions in exactly three blocks |
| Open-ended | No question can be answered yes or no |
| Grounded | Each question points to a fact or angle in the brief |
| No repeats | No question matches a common past question listed in the brief |
| User order kept | Final order matches what the user approved at the checkpoint |
| Voice | Opening and closing break none of the hard constraints |

### Outputs

| Artifact | Location | Format |
|----------|----------|--------|
| Interview outline | `output/[episode-slug]-interview-outline.md` | Markdown: Opening, Block 1, Block 2, Block 3 (numbered questions), Closing |

**Handoff:** Recording happens outside the workspace. The user then places the Descript transcript in `stages/03-cut-list/input/`.

---

## Stage 03: Cut List

**Responsibility:** Mark tangents, false starts and ad breaks in the transcript for the Descript edit.

### Inputs

| Source | File/Location | Section/Scope | Why |
|--------|--------------|---------------|-----|
| User (per episode) | `input/[episode-slug]-transcript.txt` | Full file | Descript text export with timestamps |
| Previous stage | `../02-outline/output/[episode-slug]-interview-outline.md` | Block 1 to Block 3 | Tell planned material from tangents |
| Cut categories | `references/cut-categories.md` | Full file | Definitions of tangent, false start, ad break |
| Descript export format | `references/descript-export-format.md` | "Timestamp Format" section | How to read timestamps in the export |
| Descript setup guide | `references/descript-setup.md` | "Exporting a Transcript" section | Only if the transcript is missing or has no timestamps |
| {{?AUDIO_CLIPS}}ffmpeg setup guide | `references/ffmpeg-setup.md` | "Clip Command" section | Write clip commands for candidates{{/AUDIO_CLIPS}} |

### Process

1. Confirm the transcript is in `input/` and has timestamps. If not, point the user to `descript-setup.md` and stop.
2. Map transcript sections to outline questions.
3. Mark false starts and ad breaks.
4. Mark tangents: material that matches no outline question and adds nothing to the topic.
5. Give each entry a start, end, category and one-line reason.
6. {{?AUDIO_CLIPS}}List 3 to 5 clip candidates with timestamps and an ffmpeg command for each.{{/AUDIO_CLIPS}}
7. Run the audit and save.

### Checkpoints

None. This is a linear marking stage. The user reviews the cut list while editing in Descript and may edit the output file before stage 04.

### Audit

| Check | Pass Condition |
|-------|---------------|
| Complete entries | Every row has start, end, category and reason |
| Valid categories | Every category is one of those in `cut-categories.md` |
| Valid timestamps | Start is before end, both exist in the transcript, no overlapping rows |
| Planned material kept | No row cuts the main answer to an outline question |

### Outputs

| Artifact | Location | Format |
|----------|----------|--------|
| Cut list | `output/[episode-slug]-cut-list.md` | Markdown table: Start, End, Category, Reason. {{?AUDIO_CLIPS}}Plus a Clip Candidates table: Start, End, Why, ffmpeg command.{{/AUDIO_CLIPS}} |

---

## Stage 04: Show Notes

**Responsibility:** Write publish-ready show notes from the edited episode.

### Inputs

| Source | File/Location | Section/Scope | Why |
|--------|--------------|---------------|-----|
| User (per episode, read-only) | `../03-cut-list/input/[episode-slug]-transcript.txt` | Full file | Summary, chapters, links mentioned, verbatim pull quote |
| Previous stage | `../03-cut-list/output/[episode-slug]-cut-list.md` | Cut table | Shift chapter timestamps to the edited timeline and skip cut material |
| Earlier stage | `../01-research/output/[episode-slug]-guest-brief.md` | "Episode" header, "Bio", "Sources" | Guest bio, guest links, sponsor yes/no |
| Show identity | `../../brand-vault/show-identity.md` | "Show" and "Host" sections | Names in the notes |
| Voice rules | `../../brand-vault/voice-rules.md` | "Hard Constraints" through "What the Voice Is NOT" | Tone of the summary |
| {{?SPONSOR}}Sponsor read | `../../brand-vault/sponsor-read.md` | Full file | Sponsor section text and link, only if this episode has a sponsor{{/SPONSOR}} |
| Show notes format | `references/show-notes-format.md` | Full file | Section order, chapter rules, timestamp math |

### Process

1. Read the cut list and compute the edited timeline (each timestamp minus the total length of cuts before it).
2. Write the summary in the show's voice.
3. Build chapter markers from uncut sections, with edited-timeline timestamps.
4. List every link or resource mentioned in the transcript, plus the guest links from the brief.
5. Pick one pull quote verbatim from uncut material.
6. {{?SPONSOR}}If the brief says this episode has a sponsor, add the sponsor section from `sponsor-read.md`. Otherwise skip it.{{/SPONSOR}}
7. **[Checkpoint]** Present the draft notes. The user approves or edits the summary, chapters and pull quote.
8. Run the audit and save.

### Checkpoints

| After Step | Agent Presents | Human Decides |
|------------|---------------|---------------|
| 6 | Draft show notes with chapters and pull quote | Summary edits, chapter titles, which pull quote to use |

### Audit

| Check | Pass Condition |
|-------|---------------|
| Sections | Summary, chapters, links and pull quote are present, in the order set by `show-notes-format.md` |
| Chapter timestamps | Every chapter falls on the edited timeline, outside cut ranges, in ascending order |
| Verbatim quote | The pull quote matches the transcript word for word and is not in a cut range |
| Links | Every link listed was mentioned in the transcript or is in the brief's Sources |
| Sponsor | Sponsor section appears only when the episode has a sponsor, with the exact read text |
| Voice | Summary breaks none of the hard constraints |

### Outputs

| Artifact | Location | Format |
|----------|----------|--------|
| Show notes | `output/[episode-slug]-show-notes.md` | Markdown: Title, Summary, Chapters (timestamp + title), Links Mentioned, Pull Quote, {{?SPONSOR}}Sponsor,{{/SPONSOR}} About the Guest |

---

## Stage 05: Social

**Responsibility:** Write one promotion post each for LinkedIn, X and Instagram.

### Inputs

| Source | File/Location | Section/Scope | Why |
|--------|--------------|---------------|-----|
| Previous stage | `../04-show-notes/output/[episode-slug]-show-notes.md` | Title, Summary, Pull Quote, About the Guest | Post content |
| Show identity | `../../brand-vault/show-identity.md` | "Show" and "Audience" sections | Who the posts speak to |
| Voice rules | `../../brand-vault/voice-rules.md` | Full file | Show voice for all three posts |
| Platform specs | `../../shared/platform-specs.md` | LinkedIn, X and Instagram sections | Length limits, hashtag and link rules |

### Process

1. Pick one hook per platform from the summary or pull quote.
2. Draft the LinkedIn post.
3. Draft the X post.
4. Draft the Instagram caption.
5. **[Checkpoint]** Present all three posts. The user approves or edits.
6. Run the audit and save.

### Checkpoints

| After Step | Agent Presents | Human Decides |
|------------|---------------|---------------|
| 4 | Three draft posts | Edits per post, hook choice |

### Audit

| Check | Pass Condition |
|-------|---------------|
| Three platforms | Exactly one post each for LinkedIn, X and Instagram |
| Length limits | Each post is within its limit in `platform-specs.md` |
| Link and hashtag rules | Each post follows its platform's rules in `platform-specs.md` |
| Voice | No post breaks a hard constraint or matches a "wrong" example pattern |
| Facts | Every claim and quote appears in the show notes |

### Outputs

| Artifact | Location | Format |
|----------|----------|--------|
| Social posts | `output/[episode-slug]-social-posts.md` | Markdown: LinkedIn, X, Instagram sections (final deliverable) |

---

## Cross-References

| Reader | Reads From | Direction |
|--------|-----------|-----------|
| 02 | 01 output | forward |
| 03 | 02 output, 03 input | forward |
| 04 | 01 output, 03 output, 03 input | forward |
| 05 | 04 output | forward |
| 01, 02, 04, 05 | `brand-vault/show-identity.md` | shared to stage |
| 02, 04, 05 | `brand-vault/voice-rules.md` | shared to stage |
| 04 | `brand-vault/sponsor-read.md` (optional) | shared to stage |
| 05 | `shared/platform-specs.md` | shared to stage |

No earlier stage reads a later stage. Shared files reference no stage.

## Canonical Sources

| Fact | One Home |
|------|----------|
| Show name, host name, audience | `brand-vault/show-identity.md` |
| Voice rules | `brand-vault/voice-rules.md` |
| Sponsor name, read text, link | `brand-vault/sponsor-read.md` |
| Platform limits and conventions | `shared/platform-specs.md` |
| Guest, topic, recording date, episode slug, sponsor yes/no (per episode) | Episode header of `01-research/output/[episode-slug]-guest-brief.md` |
| Brief format | `stages/01-research/references/brief-format.md` |
| Research source types | `stages/01-research/references/research-sources.md` |
| Outline structure | `stages/02-outline/references/outline-format.md` |
| Question quality rules | `stages/02-outline/references/question-rules.md` |
| Cut categories | `stages/03-cut-list/references/cut-categories.md` |
| Descript timestamp format | `stages/03-cut-list/references/descript-export-format.md` |
| Descript export steps | `stages/03-cut-list/references/descript-setup.md` |
| ffmpeg install and clip command (optional) | `stages/03-cut-list/references/ffmpeg-setup.md` |
| Transcript (per episode) | `stages/03-cut-list/input/[episode-slug]-transcript.txt` |
| Show notes format and timestamp math | `stages/04-show-notes/references/show-notes-format.md` |

## Audit Results

| Check | Result |
|-------|--------|
| No circular references | Pass. Every edge runs from a lower stage to a higher stage, or from a shared file into a stage. |
| Output consumption | Pass. 01 is read by 02 and 04; 02 by 03; 03 by 04; 04 by 05; 05 is the final deliverable. |
| Contract completeness | Pass. All five stages have Inputs, Process and Outputs with every field filled. |
| Canonical sources | Pass. Each fact has one home (table above). Per-episode facts live only in the brief header; the sponsor yes/no moved there from a per-stage question so stage 04 does not ask again. |

## Assumptions

- **Step 7 checkpoint:** No live review was possible. The diagram and contracts are approved as written, because they follow the discovery map and the user's stated order.
- **Transcript location:** The transcript lives in `stages/03-cut-list/input/` (the discovery map's placement). Stage 04 reads it there read-only. This is a forward reference (04 reads 03), so it does not break one-way flow. The `input/` folder needs a `.gitkeep` and must be named in stage 03's scaffold.
- **Episode slug:** Added as `[guest-name]-[recording-date]` so outputs meet the `[topic-slug]-[artifact-type].md` naming rule and so several episodes can sit side by side.
- **Per-episode facts in one place:** Guest, topic, date and sponsor yes/no are collected once at stage 01 and stored in the brief's Episode header. Later stages read them from there, not from the user again.
- **Checkpoints:** Stage 02's checkpoint is required (user always reorders). Checkpoints were also added to 01 (fact corrections, per the discovery handoff), 04 (pre-publish review) and 05 (creative). Stage 03 runs straight through, since the user reviews it in Descript.
- **Timestamp shift:** Chapter timestamps are assumed to need converting to the edited timeline. The method belongs in `show-notes-format.md`, not in the CONTEXT.md.
- **Audience placeholder** `{{SHOW_AUDIENCE}}` is kept, since stages 01 and 05 use it.
- **Value validation (Pattern 13)** was not added. The user did not ask for it and the outline checkpoint already covers the creative steering. Stage 03 can add it if wanted.
- **Section names** in Inputs tables (for example "Hard Constraints", "Episode" header) are proposals. Stage 03 must create reference files with exactly these headings.
</file>