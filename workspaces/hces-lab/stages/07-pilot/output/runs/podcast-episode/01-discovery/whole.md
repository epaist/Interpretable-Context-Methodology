<file path="workflow-map.md">
# Workflow Map: Podcast Episode Pipeline (Booking to Published Show Notes)

## Overview

**What it does:** Takes one episode of a weekly interview podcast from a guest name and topic to a guest brief, an interview outline, a cut list, show notes and three social posts.
**Starts with:** Guest name, topic, recording date (new each episode).
**Ends with:** Published-ready show notes plus LinkedIn, X and Instagram posts in the show's voice.
**Target user:** A podcast host or producer who runs a recurring interview show.
**Stages:** 5 (research, outline, cut list, show notes, social posts).

## Stage Breakdown

### 01-research: Guest and Topic to Guest Brief
- **Responsibility:** Research the guest and write a one-page brief.
- **Inputs:** User: guest name, topic, recording date (per episode). Shared: show identity (show name, host name, audience).
- **Agent needs to know:** Brief format (one page, fixed sections), source types to cover (past interviews, book or company, public statements on the topic), citation rules (every claim carries a source link).
- **Output artifact:** `output/guest-brief.md` (one page: bio, book or company, past interviews, public positions on the topic, possible angles, sources).
- **Handoff point:** The user may correct or add facts before the outline is written.

### 02-outline: Guest Brief to Interview Outline
- **Responsibility:** Write the interview outline.
- **Inputs:** `01-research/output/guest-brief.md`. Shared: show identity, voice rules (for the opening and closing).
- **Agent needs to know:** Outline structure: opening, 8 to 12 questions in three blocks, closing. Question quality rules (open-ended, grounded in the brief, no repeats of the guest's most common past questions).
- **Checkpoint (required):** After drafting the questions, the agent presents the blocks and the user reviews, reorders, adds or cuts questions before the outline is finalized.
- **Output artifact:** `output/interview-outline.md`.
- **Handoff point:** Recording happens outside the workspace, between this stage and the next.

### 03-cut-list: Transcript to Cut List
- **Responsibility:** Mark sections to remove or handle in the edit.
- **Inputs:** User: Descript transcript text export with timestamps (per episode, placed in this stage's input). Per-run reference: `02-outline/output/interview-outline.md` (used to tell planned material from tangents).
- **Agent needs to know:** Cut categories (tangent, false start, ad break), timestamp format of the Descript text export, and the rule that each entry gets a start, end, category and one-line reason.
- **Output artifact:** `output/cut-list.md` (table: start, end, category, reason; optional clip candidates for ffmpeg).
- **Handoff point:** The user edits in Descript using the cut list and may adjust it.

### 04-show-notes: Transcript and Cut List to Show Notes
- **Responsibility:** Write the show notes for publishing.
- **Inputs:** Descript transcript (from stage 03 input), `03-cut-list/output/cut-list.md` (so that chapter timestamps skip cut material), `01-research/output/guest-brief.md` (guest bio and links). Shared: show identity, voice rules, sponsor read (optional).
- **Agent needs to know:** Show notes format: summary, chapter markers with timestamps, links mentioned, pull quote (verbatim from the transcript), sponsor read section when there is a sponsor.
- **Output artifact:** `output/show-notes.md`.
- **Handoff point:** The user reviews the show notes before publishing.

### 05-social: Show Notes to Social Posts
- **Responsibility:** Write three promotion posts.
- **Inputs:** `04-show-notes/output/show-notes.md`. Shared: show identity, voice rules, platform specs.
- **Agent needs to know:** Platform specs (LinkedIn, X, Instagram: length limits, hashtag and link conventions), voice rules.
- **Output artifact:** `output/social-posts.md` (one section each for LinkedIn, X, Instagram).

## Input/Output Chain

```
guest + topic + date (user) -> 01 guest-brief -> 02 interview-outline -> [recording, outside workspace]
Descript transcript (user) + 02 outline -> 03 cut-list -> 04 show-notes (+ transcript, + 01 brief) -> 05 social-posts
```

Every input is either user-provided (guest, topic, date, transcript) or produced by an earlier stage.

## Shared Context (Layer 3, persistent)

| Resource | Proposed Location | Used By |
|----------|-------------------|---------|
| Show identity (show name, host name, audience, show format) | `brand-vault/show-identity.md` | 01, 02, 04, 05 |
| Voice rules (hard constraints, sentence rules wrong/right, what the voice is NOT) | `brand-vault/voice-rules.md` | 02, 04, 05 |
| Sponsor read (optional) | `brand-vault/sponsor-read.md` | 04 |
| Platform specs (LinkedIn, X, Instagram) | `shared/platform-specs.md` | 05 |

Stage-specific references (Layer 3, one stage each): brief format (01), outline format and question rules (02), cut categories and Descript export format (03), show notes format (04).

## User-Specific Variables (set once at onboarding)

| Placeholder | Meaning |
|-------------|---------|
| `{{SHOW_NAME}}` | Podcast name |
| `{{HOST_NAME}}` | Host name |
| `{{SHOW_AUDIENCE}}` | Who listens |
| `{{VOICE_HARD_CONSTRAINTS}}` | Numbered voice rules |
| `{{VOICE_EXAMPLE_RIGHT}}` / `{{VOICE_EXAMPLE_WRONG}}` | Sentence pairs that do and do not sound like the show |
| `{{VOICE_NOT}}` | What the voice is not |
| `{{SPONSOR_NAME}}` | Sponsor name (conditional) |
| `{{SPONSOR_READ_TEXT}}` | Sponsor read copy (conditional) |
| `{{SPONSOR_LINK}}` | Sponsor URL or promo code (conditional) |

## Per-Episode Inputs (not placeholders; Layer 4 working input)

Guest name, topic, recording date, Descript transcript export. These change every run and come in at stages 01 and 03. They are not baked into the workspace at setup.

## Optional / Conditional Sections

- `{{?SPONSOR}}...{{/SPONSOR}}`: Wraps the sponsor read file reference and the sponsor section of the show notes format. It is removed at onboarding if the show never has sponsors. Per episode, the user says whether this episode has a sponsor, and stage 04 skips the section if not.
- `{{?AUDIO_CLIPS}}...{{/AUDIO_CLIPS}}`: Wraps the clip-candidate section of the cut list and the ffmpeg setup guide. It is included only if the user wants ffmpeg clips.

## Tool Prerequisites

| Tool | Stage | Required? | Purpose |
|------|-------|-----------|---------|
| Descript | 03 (source of the input) | Required | Produces the transcript text export. It is used outside the agent, so the setup guide covers the export steps and settings (timestamps on). |
| ffmpeg | 03 (or a later clip step) | Optional | Cuts short audio clips from the episode audio at the cut-list or pull-quote timestamps. The setup guide goes in `stages/03-cut-list/references/`. |

## Selected Skills

None bundled. See Assumptions.

## Audit Results

| Check | Result |
|-------|--------|
| Stage clarity | Pass: each of the 5 stages has one responsibility and one named artifact. |
| Input/output chain | Pass: the only external inputs are the per-episode user inputs. Every other input comes from an earlier stage. |
| Shared context identified | Pass: brand-vault and shared/ are listed apart from stage references. |
| Variable coverage | Pass: show name, host, voice and sponsor are placeholders. Per-episode values are documented as run inputs. |

## Assumptions

- **Step 1 and steps 3 to 7 (user questions):** The answers come from the workflow description alone. Details the description does not give (brief sections, cut-list columns, platform limits) are proposed defaults for stage 02 to refine.
- **Stage split:** Cut list and show notes are kept as separate stages because the user edits in Descript between them, which gives a natural review point. The outline checkpoint is required because the user always reorders questions.
- **Recording** happens outside the workspace. The transcript enters as user input at stage 03.
- **Audience** was added as a placeholder (`{{SHOW_AUDIENCE}}`) even though the user did not name it, because research and social posts need it. It can be dropped at stage 02.
- **Sponsor** is treated as optional both at onboarding and per episode.
- **ffmpeg clips** are attached to stage 03 as an optional section, not a separate stage.
- **Step 8 (skills):** No tools or search were available, so no local or GitHub skills were found or presented. The decision is to bundle none, and the workspace uses custom references. This can be revisited in stage 03 scaffolding.
- **Step 9 checkpoint:** No live review was possible. The draft is approved as written, based on how closely it follows the user's stated sequence.
</file>