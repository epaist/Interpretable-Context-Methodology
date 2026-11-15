<file path="workflow-map.md">
# Workflow Map: Podcast Episode Pipeline (Booking to Published Show Notes)

## Overview

- **Starts with:** a guest name, an episode topic and a recording date (new every episode)
- **Ends with:** a cut list, published show notes and three social posts (LinkedIn, X, Instagram)
- **Cadence:** weekly, one run per episode
- **Human-in-the-loop moments:** question review and reorder before recording (required), the recording itself, the Descript transcript export

## Stages

### 01-research: Guest and Topic to Guest Brief
- **Single responsibility:** Research the guest and write a one-page brief
- **Inputs:** `{{GUEST_NAME}}`, `{{EPISODE_TOPIC}}`, `{{RECORDING_DATE}}` (per-run, from user); any links or notes the user supplies
- **Agent needs to know:** brief format (one page, fixed sections), research checklist (past interviews, book or company, public statements on the topic), source citation rules
- **Process notes:** gather past interviews, their book or company, and their public statements on the topic. Every claim cites a source.
- **Output artifact:** `output/guest-brief.md` (one page: bio, book/company, past interviews, stated positions on topic, angles not yet covered, sources)
- **Human edit surface:** the brief. User can add private context or remove angles.

### 02-outline: Guest Brief to Interview Outline
- **Single responsibility:** Turn the brief into a structured interview outline
- **Inputs:** `../01-research/output/guest-brief.md`; show voice rules (shared)
- **Agent needs to know:** outline format (opening, 8 to 12 questions in three blocks, closing), question-writing rules (open-ended, no repeats of the guest's stock answers from past interviews), host name for the opening
- **Checkpoints:**
  - After drafting questions: agent presents all questions grouped in three blocks. Human reviews, rewrites and reorders. **Required, every episode.**
- **Audit:** question count is 8 to 12; exactly three blocks; opening and closing present; no question duplicates a topic the brief marks as over-covered
- **Output artifact:** `output/interview-outline.md`
- **Human edit surface:** the outline. This is where reordering is recorded.

### (Offline) Recording
Not a workspace stage. The host records the episode and exports the transcript from Descript as a text file. This is the handoff into stage 03.

### 03-cut-list: Transcript to Cut List
- **Single responsibility:** Mark sections to remove or flag in editing
- **Inputs:** Descript text transcript placed in the stage's `input/` folder (per-run, user-provided); `../02-outline/output/interview-outline.md` (to tell on-topic from tangent)
- **Agent needs to know:** Descript text export format (timestamps, speaker labels); cut categories (tangent, false start, ad break); timestamp format rule
- **Audit:** every cut has start and end timestamps, a category and a one-line reason; timestamps exist in the transcript; no overlapping cuts
- **Output artifact:** `output/cut-list.md` (table: start, end, category, reason)
- **Human edit surface:** the cut list. User accepts or rejects cuts in Descript.

### 04-show-notes: Transcript + Cut List to Show Notes
- **Single responsibility:** Write publishable show notes
- **Inputs:** Descript transcript (from stage 03 `input/`); `../03-cut-list/output/cut-list.md`; `../01-research/output/guest-brief.md` (guest bio, links); show identity and voice rules (shared); sponsor read (shared, conditional)
- **Agent needs to know:** show notes format (summary, chapter markers with timestamps, links mentioned, pull quote, optional sponsor block); timestamp adjustment rule (chapter times reflect the post-cut edit)
- **Checkpoints:**
  - After chapter markers and pull quote candidates: agent presents 2 to 3 pull quote options and the chapter list. Human picks a quote and confirms chapters.
- **Audit:** chapter timestamps are ascending and adjusted for cuts; pull quote is verbatim from the transcript; every link mentioned in the transcript is listed; summary follows voice rules; sponsor block present only if the episode has a sponsor
- **Output artifact:** `output/show-notes.md`
- **Human edit surface:** the show notes.

### 05-social: Show Notes to Social Posts
- **Single responsibility:** Write one post per platform in the show's voice
- **Inputs:** `../04-show-notes/output/show-notes.md`; voice rules (shared); platform specs (shared)
- **Agent needs to know:** per-platform length and format limits (LinkedIn, X, Instagram); voice rules
- **Checkpoints:** after drafts, human approves or redirects tone
- **Audit:** exactly three posts; each within its platform limit; each follows voice hard constraints; each names guest and episode
- **Output artifact:** `output/social-posts.md` (three labeled sections)
- **Optional extra (needs ffmpeg):** a list of clip timestamps for audio clips, plus the ffmpeg commands to cut them
- **Human edit surface:** the posts.

## Input/Output Chain

```
user (guest, topic, date) -> 01-research -> guest-brief
guest-brief -> 02-outline -> interview-outline  [human reorders]
(recording; Descript export -> 03 input/)
transcript + outline -> 03-cut-list -> cut-list
transcript + cut-list + brief -> 04-show-notes -> show-notes
show-notes -> 05-social -> social-posts (+ optional clips)
```
Every input is user-provided or produced by a prior stage.

## Shared Context (shared/ or workspace references)

| Resource | Used By | Contains |
|----------|---------|----------|
| `show-identity.md` | 02, 04, 05 | Show name, host name, tagline, publishing cadence |
| `voice-rules.md` | 02, 04, 05 | Hard constraints, sentence rules, wrong/right examples |
| `sponsor-read.md` (conditional) | 04 | Sponsor name, read copy, link |
| `platform-specs.md` | 05 | LinkedIn, X, Instagram length and format limits |
| `timestamp-format.md` | 03, 04 | One canonical timestamp format (HH:MM:SS) |

Stage-specific references (not shared): brief format (01), outline format and question rules (02), Descript export format and cut categories (03), show notes format (04).

## User-Specific Variables (set once at setup)

| Placeholder | Description |
|-------------|-------------|
| `{{SHOW_NAME}}` | Podcast name |
| `{{HOST_NAME}}` | Host's name as said in the opening |
| `{{SHOW_TAGLINE}}` | One-line description of the show |
| `{{VOICE_CONSTRAINT_1}}` to `{{VOICE_CONSTRAINT_3}}` | Hard voice rules |
| `{{VOICE_EXAMPLE_WRONG_1}}`, `{{VOICE_EXAMPLE_RIGHT_1}}` (and pair 2) | Voice examples |
| `{{VOICE_ANTI_PATTERN}}` | Phrasing the show never uses |
| `{{SPONSOR_NAME}}` | Sponsor (conditional) |
| `{{SPONSOR_READ}}` | Sponsor read copy (conditional) |
| `{{SPONSOR_LINK}}` | Sponsor URL (conditional) |
| `{{LINKEDIN_HANDLE}}`, `{{X_HANDLE}}`, `{{INSTAGRAM_HANDLE}}` | Show's social handles |

## Per-Run Variables (new every episode, not setup placeholders)

| Variable | Entered At |
|----------|-----------|
| `{{GUEST_NAME}}` | Stage 01 start |
| `{{EPISODE_TOPIC}}` | Stage 01 start |
| `{{RECORDING_DATE}}` | Stage 01 start |
| `{{EPISODE_HAS_SPONSOR}}` (yes/no) | Stage 04 start |
| Transcript file | Stage 03 `input/` |

These go in a per-episode `episode.md` input file, not in the questionnaire.

## Optional Stages and Conditional Sections

- `{{?SPONSOR}}...{{/SPONSOR}}`: wraps the sponsor block in the show notes format and `sponsor-read.md`. Workspace-level: removed if the show never has sponsors. Per-episode: the stage 04 agent omits the block when `EPISODE_HAS_SPONSOR` is no.
- `{{?AUDIO_CLIPS}}...{{/AUDIO_CLIPS}}`: wraps the clip-generation section of stage 05 and the ffmpeg setup guide. Removed if the user does not install ffmpeg.

No full stage is optional.

## Tool Prerequisites

| Tool | Stage | Required? | Purpose |
|------|-------|-----------|---------|
| Descript | 03 (input), 04 | Required (used outside the agent) | Record/edit and export the text transcript; apply cuts |
| ffmpeg | 05 | Optional | Cut short audio clips for social posts |

Setup guides: `stages/03-cut-list/references/descript-export.md`, `stages/05-social/references/ffmpeg-setup.md` (conditional).

## Selected Skills

None selected. No skill search was possible in this run (see Assumptions). Candidates to search for in a later pass: a podcast or show-notes skill, a social copywriting skill. Hand-written references cover all needs for now.

## Assumptions

1. **Step 1 (describe workflow):** The user's written description is the full answer. No follow-up questions were asked.
2. **Stage breakdown:** Five agent stages. Recording is an offline human step, not a stage. Cut list and show notes are kept as separate stages because the user listed them as separate deliverables and each is a useful edit point.
3. **Interview outline checkpoint:** Made a required checkpoint because the user said they "always" review and reorder questions.
4. **Show notes timestamps:** Chapter markers are assumed to use post-cut timestamps. This is the likely need for published notes, and it is why stage 04 reads the cut list.
5. **Per-run vs setup variables:** Guest, topic and recording date are per-episode inputs, not questionnaire placeholders, because the user said they are new every episode. The sponsor is both a setup conditional and a per-episode toggle, because "some episodes have no sponsor."
6. **Step 8 (skills):** Local folders and GitHub could not be scanned. No skills were bundled, and this is recorded instead of guessed.
7. **Step 9 (checkpoint):** No user was available, so the map was accepted as drafted. The user can merge 03 and 04 or split 05 per platform at the stage 02 handoff.
8. **ffmpeg clips:** Placed in stage 05 as an optional section, since clips mainly support social posts.
9. **Social handles:** Added as placeholders because posts usually tag the show. The user did not mention them, so they can be dropped.
</file>