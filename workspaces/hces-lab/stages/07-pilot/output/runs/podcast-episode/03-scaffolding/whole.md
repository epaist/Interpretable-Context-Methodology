<file path="scaffold-notes.md">
# Scaffold Notes: Podcast Episode Pipeline

Stage 03 output for the workspace builder. The generated workspace is in `podcast-episode-pipeline/`. Stage 04 reads it to design `setup/questionnaire.md`.

## Generated Tree

```
podcast-episode-pipeline/
├── CLAUDE.md
├── CONTEXT.md
├── setup/
│   └── questionnaire.md            (stub; stage 04 fills it)
├── brand-vault/
│   ├── CONTEXT.md
│   ├── show-identity.md
│   ├── voice-rules.md
│   └── sponsor-read.md             (whole content wrapped in {{?SPONSOR}})
├── shared/
│   └── platform-specs.md
└── stages/
    ├── 01-research/    CONTEXT.md, references/brief-format.md, references/research-sources.md, output/.gitkeep
    ├── 02-outline/     CONTEXT.md, references/outline-format.md, references/question-rules.md, output/.gitkeep
    ├── 03-cut-list/    CONTEXT.md, input/.gitkeep, references/cut-categories.md, references/descript-export-format.md,
    │                   references/descript-setup.md, references/ffmpeg-setup.md, output/.gitkeep
    ├── 04-show-notes/  CONTEXT.md, references/show-notes-format.md, output/.gitkeep
    └── 05-social/      CONTEXT.md, references/.gitkeep, output/.gitkeep
```

## Placeholders Introduced

| Placeholder | File(s) |
|-------------|---------|
| `{{SHOW_NAME}}`, `{{SHOW_FORMAT}}`, `{{SHOW_TAGLINE}}`, `{{SHOW_URL}}` | `brand-vault/show-identity.md` |
| `{{HOST_NAME}}`, `{{HOST_BIO}}` | `brand-vault/show-identity.md` |
| `{{SHOW_AUDIENCE}}` | `brand-vault/show-identity.md` |
| `{{VOICE_HARD_CONSTRAINTS}}`, `{{VOICE_EXAMPLE_WRONG}}`, `{{VOICE_EXAMPLE_RIGHT}}`, `{{VOICE_PACING}}`, `{{VOICE_NOT}}` | `brand-vault/voice-rules.md` |
| `{{SPONSOR_NAME}}`, `{{SPONSOR_READ_TEXT}}`, `{{SPONSOR_LINK}}` | `brand-vault/sponsor-read.md` |
| `{{SHOW_HASHTAGS}}` | `shared/platform-specs.md` |
| Conditional `{{?SPONSOR}}` | `brand-vault/sponsor-read.md`, `stages/04-show-notes/references/show-notes-format.md` |
| Conditional `{{?AUDIO_CLIPS}}` | `stages/03-cut-list/references/ffmpeg-setup.md`, `stages/03-cut-list/references/cut-categories.md` |

## Audit Results

| Check | Result |
|-------|--------|
| Folder structure | Pass. Every stage has CONTEXT.md, output/ and references/. Stage 05 has no reference files of its own, so its references/ holds a .gitkeep. Stage 03 also has input/. |
| Contract fidelity | Pass. Inputs, process steps, checkpoints, audits and outputs follow `stage-contracts.md`. The only change is how optional items are marked (see Assumptions). |
| Placeholder syntax | Pass. All placeholders use `{{SCREAMING_SNAKE_CASE}}`. Conditionals wrap whole sections only. |
| .gitkeep coverage | Pass. Every output/ folder, stage 03 input/ and stage 05 references/ contain a .gitkeep. |
| CONTEXT.md size | Pass. The longest file (stage 04) is under 80 lines. |
| Naming conventions | Pass. All folders and files use lowercase-with-hyphens. |

## Assumptions

- **Workspace name:** `podcast-episode-pipeline`, taken from the contracts title.
- **Inline conditionals moved:** The contracts wrapped single table rows and process steps in `{{?SPONSOR}}` and `{{?AUDIO_CLIPS}}`. `_core/placeholder-syntax.md` allows conditional blocks only around entire sections, and placeholders in stage CONTEXT.md files only in Inputs table values. The conditionals were therefore moved into the reference files, where each one wraps a whole section:
  - `sponsor-read.md` content and the Sponsor section of `show-notes-format.md` use `{{?SPONSOR}}`.
  - The `ffmpeg-setup.md` content and the Clip Candidates section of `cut-categories.md` use `{{?AUDIO_CLIPS}}`.
  - The stage 03 and stage 04 CONTEXT.md files say "only if the section exists". The behavior matches the contracts.
- **Contract wording kept:** Stage 01 lists its checkpoint as "after step 6" and has a separate step 7. This was kept as written.
- **Value framework (Pattern 13) not created:** Process step 7 calls for one in content-producing workspaces. Stage 02 decided against it, and adding it would put an input that is not in the contracts. The outline checkpoint covers steering. It can be added later.
- **Shared constants (Pattern 15):** Not applicable, because this workspace does not produce code.
- **Skills:** None were selected in discovery, so there is no skills/ folder. The skills rows were removed from CLAUDE.md and CONTEXT.md.
- **Setup guides:** Descript and ffmpeg guides were written to `stages/03-cut-list/references/`. Descript runs outside the agent, so its guide covers export steps only.
- **Descript timestamp format:** The default is `[HH:MM:SS]` at the start of each speaker turn. The guide tells the user to confirm this against the first real export, because no sample was available.
- **Platform limits:** Defaults are LinkedIn 3,000 characters, X 280 characters and Instagram 2,200 characters. Hashtags are a placeholder.
- **Questionnaire:** `setup/questionnaire.md` is a stub. Stage 04 builds it.
- **No live review:** No live review was possible. The scaffold is saved as audited.
</file>

<file path="podcast-episode-pipeline/CLAUDE.md">
# Podcast Episode Pipeline

Takes one episode of a weekly interview podcast from a guest name and topic to a guest brief, interview outline, cut list, show notes and three social posts.

## Folder Map

```
podcast-episode-pipeline/
├── CLAUDE.md          (you are here)
├── CONTEXT.md         (start here for task routing)
├── setup/             (onboarding questionnaire)
├── brand-vault/       (show identity, voice rules, sponsor read)
├── stages/
│   ├── 01-research/   (guest + topic -> guest brief)
│   ├── 02-outline/    (brief -> interview outline, user reorders)
│   ├── 03-cut-list/   (Descript transcript -> cut list)
│   ├── 04-show-notes/ (transcript + cut list -> show notes)
│   └── 05-social/     (show notes -> LinkedIn, X, Instagram posts)
└── shared/            (platform specs)
```

## Triggers

| Keyword | Action |
|---------|--------|
| `setup` | Run onboarding questionnaire in `setup/questionnaire.md` |
| `status` | Show pipeline completion for all stages |

`status`: for each `stages/*/output/`, the stage is COMPLETE if it holds files other than .gitkeep, otherwise PENDING. Group by episode slug when several episodes are present.

## Routing

| Task | Go To |
|------|-------|
| Research a new guest (start an episode) | `stages/01-research/CONTEXT.md` |
| Write the interview outline | `stages/02-outline/CONTEXT.md` |
| Build the cut list from a transcript | `stages/03-cut-list/CONTEXT.md` |
| Write show notes | `stages/04-show-notes/CONTEXT.md` |
| Write social posts | `stages/05-social/CONTEXT.md` |

## What to Load

| Task | Load These | Do NOT Load |
|------|-----------|-------------|
| Research | `brand-vault/show-identity.md`, `stages/01-research/references/` | Other stages, voice rules, platform specs |
| Outline | 01 output brief, `show-identity.md`, `voice-rules.md`, `stages/02-outline/references/` | Transcript, stages 03 to 05 |
| Cut list | Transcript in `stages/03-cut-list/input/`, 02 output outline, `stages/03-cut-list/references/` | brand-vault, stages 04 and 05 |
| Show notes | Transcript, 03 output, 01 output brief, `show-identity.md`, `voice-rules.md`, `sponsor-read.md` (if sponsored), `stages/04-show-notes/references/` | 02 output, platform specs |
| Social | 04 output, `show-identity.md`, `voice-rules.md`, `shared/platform-specs.md` | Transcript, cut list, brief, outline |

## Stage Handoffs

Each stage writes its output to its own `output/` folder as `[episode-slug]-[artifact].md`. The next stage reads from there. If you edit an output file, the next stage picks up your edits. Recording happens between stages 02 and 03. Place the Descript export in `stages/03-cut-list/input/[episode-slug]-transcript.txt`.
</file>

<file path="podcast-episode-pipeline/CONTEXT.md">
# Podcast Episode Pipeline

Covers one podcast episode from booking (guest + topic) to publish-ready show notes and social posts.

## Task Routing

| Task Type | Go To | Description |
|-----------|-------|-------------|
| Research | `stages/01-research/CONTEXT.md` | One-page guest brief; sets the episode slug |
| Outline | `stages/02-outline/CONTEXT.md` | Opening, 8 to 12 questions in three blocks, closing |
| Cut list | `stages/03-cut-list/CONTEXT.md` | Tangents, false starts, ad breaks with timestamps |
| Show notes | `stages/04-show-notes/CONTEXT.md` | Summary, chapters, links, pull quote, sponsor |
| Social | `stages/05-social/CONTEXT.md` | One post each for LinkedIn, X, Instagram |

## Shared Resources

| Resource | Location | Contains |
|----------|----------|----------|
| Brand vault | `brand-vault/CONTEXT.md` | Show identity, voice rules, sponsor read |
| Shared files | `shared/platform-specs.md` | Length, link and hashtag rules per platform |
</file>

<file path="podcast-episode-pipeline/setup/questionnaire.md">
# Onboarding Questionnaire

Stub. This file is built in workspace-builder stage 04 (questionnaire design). It will map questions to the placeholders in `brand-vault/` and `shared/`, and to the `SPONSOR` and `AUDIO_CLIPS` conditionals.
</file>

<file path="podcast-episode-pipeline/brand-vault/CONTEXT.md">
# Brand Vault

Persistent show context. Set once at onboarding and changed only when the show changes.

| File | Contains | Used By |
|------|----------|---------|
| `show-identity.md` | Show, Host, Audience sections | 01, 02, 04, 05 |
| `voice-rules.md` | Hard Constraints, Sentence Rules, Pacing, What the Voice Is NOT | 02, 04, 05 |
| `sponsor-read.md` | Sponsor name, read text, link (optional) | 04 |

Per-episode facts (guest, topic, date, sponsor yes/no) do not live here. They live in the Episode header of each guest brief.
</file>

<file path="podcast-episode-pipeline/brand-vault/show-identity.md">
# Show Identity

## Show

- Name: {{SHOW_NAME}}
- Format: {{SHOW_FORMAT}}
- Tagline: {{SHOW_TAGLINE}}
- Website: {{SHOW_URL}}

## Host

- Name: {{HOST_NAME}}
- Short bio: {{HOST_BIO}}

## Audience

{{SHOW_AUDIENCE}}
</file>

<file path="podcast-episode-pipeline/brand-vault/voice-rules.md">
# Voice Rules

## Hard Constraints

Numbered rules that no output may break.

{{VOICE_HARD_CONSTRAINTS}}

## Sentence Rules

Wrong (does not sound like the show):

{{VOICE_EXAMPLE_WRONG}}

Right (sounds like the show):

{{VOICE_EXAMPLE_RIGHT}}

## Pacing

{{VOICE_PACING}}

## What the Voice Is NOT

{{VOICE_NOT}}
</file>

<file path="podcast-episode-pipeline/brand-vault/sponsor-read.md">
# Sponsor Read

Used by stage 04 only when the guest brief's Episode header says `Sponsor: yes`. If the section below has been removed, the show has no sponsors and no episode gets a sponsor section.

{{?SPONSOR}}

## Sponsor

- Name: {{SPONSOR_NAME}}
- Link or promo code: {{SPONSOR_LINK}}

Read text (use exactly, do not rewrite):

{{SPONSOR_READ_TEXT}}

{{/SPONSOR}}
</file>

<file path="podcast-episode-pipeline/shared/platform-specs.md">
# Platform Specs

## LinkedIn

- Length: up to 3,000 characters; aim for 600 to 1,200.
- First two lines carry the hook (shown before "see more").
- Link: one episode link, allowed in the post body.
- Hashtags: 3 to 5 at the end.

## X

- Length: 280 characters including the link (links count as 23).
- Link: one episode link.
- Hashtags: 0 to 2.

## Instagram

- Caption length: up to 2,200 characters; the hook is in the first 125.
- Link: links in captions are not clickable, so write "link in bio" and include no URL.
- Hashtags: 5 to 15, placed at the end.

## Show Hashtags

Always available for any platform: {{SHOW_HASHTAGS}}
</file>

<file path="podcast-episode-pipeline/stages/01-research/CONTEXT.md">
# Stage 01: Research

Turn a guest name and topic into a one-page guest brief, and set the episode slug.

## Inputs

| Source | File/Location | Section/Scope | Why |
|--------|--------------|---------------|-----|
| User (per episode) | Conversation at stage start | Guest name, topic, recording date, sponsor yes/no | Run inputs for this episode |
| Show identity | `../../brand-vault/show-identity.md` | "Show" and "Audience" sections | Frame research for the show's listeners |
| Brief format | `references/brief-format.md` | Full file | Fixed sections, one-page length, citation rule |
| Research sources guide | `references/research-sources.md` | Full file | Source types to cover |

## Process

1. Collect guest name, topic, recording date and whether this episode has a sponsor. Build the episode slug `[guest-name]-[YYYY-MM-DD]` (lowercase, hyphens).
2. Fill in the brief's Episode header with these values, so later stages read them from one place.
3. Research the guest's bio, book or company, past interviews and public statements on the topic, using `research-sources.md`.
4. List the guest's most common past questions and answers.
5. Draft the brief in the fixed sections from `brief-format.md`, with a source link for every claim.
6. Propose three to five possible interview angles.
7. **[Checkpoint]** Present the draft brief. The user corrects or adds facts.
8. Run the audit and save.

## Checkpoints

| After Step | Agent Presents | Human Decides |
|------------|---------------|---------------|
| 6 | Draft guest brief with sources and angles | Which facts to correct, add or drop; which angles to keep |

## Audit

| Check | Pass Condition |
|-------|---------------|
| One page | Brief fits the length limit in `brief-format.md` |
| Sections | Every section from `brief-format.md` is present |
| Citations | Every factual claim has a source link |
| Episode header | Guest, topic, date, slug and sponsor yes/no are filled in |

## Outputs

| Artifact | Location | Format |
|----------|----------|--------|
| Guest brief | `output/[episode-slug]-guest-brief.md` | Markdown: Episode header, Bio, Book or Company, Past Interviews (incl. common questions), Public Positions on the Topic, Possible Angles, Sources |
</file>

<file path="podcast-episode-pipeline/stages/01-research/references/brief-format.md">
# Guest Brief Format

## Length

One page: at most 600 words, not counting the Sources list.

## Sections (in this order)

### Episode

```
Guest: [name]
Topic: [topic]
Recording date: [YYYY-MM-DD]
Episode slug: [guest-name]-[YYYY-MM-DD]
Sponsor: yes | no
```

### Bio
Three to five sentences on who the guest is and why they matter to the audience.

### Book or Company
What they built or wrote, with dates, in two to four bullets.

### Past Interviews
Three to six notable appearances, one line each. End with a **Common Questions** sub-list: the questions the guest gets asked most, with the usual gist of the answer.

### Public Positions on the Topic
Bullets of what the guest has said publicly about this episode's topic, quoted or paraphrased.

### Possible Angles
Three to five angles, one sentence each, that the guest has not covered often.

### Sources
A numbered list of links. Cite them in the body as `[1]`, `[2]`.

## Citation Rule

Every factual claim carries a source number. Claims without a source are removed or marked `(unverified)` for the user to check.
</file>

<file path="podcast-episode-pipeline/stages/01-research/references/research-sources.md">
# Research Sources

Cover each source type. Note in the brief if one type has nothing.

## Past Interviews
Podcasts, video interviews, print and web Q&As. Prefer the last 2 to 3 years. Record repeated questions for the Common Questions list.

## Book or Company
The official site, the publisher page, the company About page, and reputable coverage (major press, trade press).

## Public Statements on the Topic
The guest's own posts, articles, talks and newsletters, plus quotes in news stories.

## Source Quality

- Prefer primary sources (the guest's own words) over summaries.
- Do not use anonymous or unsourced claims.
- If sources conflict, give both and flag the conflict for the user at the checkpoint.
</file>

<file path="podcast-episode-pipeline/stages/01-research/output/.gitkeep">
</file>

<file path="podcast-episode-pipeline/stages/02-outline/CONTEXT.md">
# Stage 02: Outline

Turn the guest brief into an interview outline the host records from.

## Inputs

| Source | File/Location | Section/Scope | Why |
|--------|--------------|---------------|-----|
| Previous stage | `../01-research/output/[episode-slug]-guest-brief.md` | Full file | Guest facts, angles, common past questions |
| Show identity | `../../brand-vault/show-identity.md` | "Show" and "Host" sections | Host name and show name for the opening and closing |
| Voice rules | `../../brand-vault/voice-rules.md` | "Hard Constraints" through "What the Voice Is NOT" | Tone of the opening and closing |
| Outline format | `references/outline-format.md` | Full file | Opening, 8 to 12 questions in three blocks, closing |
| Question rules | `references/question-rules.md` | Full file | Open-ended, grounded, no repeats |

## Process

1. Read the brief and pick the angles to carry into the three blocks.
2. Draft 8 to 12 questions across three blocks, each tagged with the brief section it comes from.
3. Check each question against the brief's Common Questions and replace any repeats.
4. **[Checkpoint]** Present the three blocks. The user reviews, reorders, adds or cuts questions.
5. Write the opening and closing in the show's voice around the approved questions.
6. Run the audit and save.

## Checkpoints

| After Step | Agent Presents | Human Decides |
|------------|---------------|---------------|
| 3 | Three question blocks with the brief source of each question | Order, additions, cuts and block assignment (required every episode) |

## Audit

| Check | Pass Condition |
|-------|---------------|
| Question count | 8 to 12 questions in exactly three blocks |
| Open-ended | No question can be answered yes or no |
| Grounded | Each question points to a fact or angle in the brief |
| No repeats | No question matches a common past question listed in the brief |
| User order kept | Final order matches what the user approved at the checkpoint |
| Voice | Opening and closing break none of the hard constraints |

## Outputs

| Artifact | Location | Format |
|----------|----------|--------|
| Interview outline | `output/[episode-slug]-interview-outline.md` | Markdown: Opening, Block 1, Block 2, Block 3 (numbered questions), Closing |

**Handoff:** Recording happens outside the workspace. The user then places the Descript transcript at `../03-cut-list/input/[episode-slug]-transcript.txt`.
</file>

<file path="podcast-episode-pipeline/stages/02-outline/references/outline-format.md">
# Interview Outline Format

## Opening
Two to four sentences for the host to say: the show name, the host name, the guest and why this guest on this topic now.

## Blocks
Three blocks with 8 to 12 questions in total. Each block has a short title and 2 to 5 questions. Number the questions continuously (1 to N) across all blocks.

- **Block 1: Background.** Who the guest is and how they got to the topic.
- **Block 2: Core.** The topic itself, built from the strongest angles.
- **Block 3: Forward.** Implications, advice and what comes next.

After each question, add a source tag in the outline: `(brief: [section])`.

## Closing
Two to four sentences: thank the guest, say where to find them, and give the show's sign-off.
</file>

<file path="podcast-episode-pipeline/stages/02-outline/references/question-rules.md">
# Question Rules

## Open-Ended
Start with how, why, what, or "tell me about". No question can be answered yes or no.

## Grounded
Each question cites a fact, position or angle from the brief.

## No Repeats
Do not ask a question that matches one in the brief's Common Questions list. If a common topic is needed, come at it from a new angle.

## One Thing at a Time
Each question asks one thing. Do not use double-barreled questions.

## Short
Keep each question under 35 words so the host can read it aloud.
</file>

<file path="podcast-episode-pipeline/stages/02-outline/output/.gitkeep">
</file>

<file path="podcast-episode-pipeline/stages/03-cut-list/CONTEXT.md">
# Stage 03: Cut List

Mark tangents, false starts and ad breaks in the transcript for the Descript edit.

## Inputs

| Source | File/Location | Section/Scope | Why |
|--------|--------------|---------------|-----|
| User (per episode) | `input/[episode-slug]-transcript.txt` | Full file | Descript text export with timestamps |
| Previous stage | `../02-outline/output/[episode-slug]-interview-outline.md` | Block 1 to Block 3 | Tell planned material from tangents |
| Cut categories | `references/cut-categories.md` | Full file | Definitions of tangent, false start, ad break |
| Descript export format | `references/descript-export-format.md` | "Timestamp Format" section | How to read timestamps in the export |
| Descript setup guide | `references/descript-setup.md` | "Exporting a Transcript" section | Only if the transcript is missing or has no timestamps |
| ffmpeg setup guide (optional) | `references/ffmpeg-setup.md` | "Clip Command" section | Only if that section exists (audio clips enabled) |

## Process

1. Confirm the transcript is in `input/` and has timestamps. If it is missing or has none, point the user to `descript-setup.md` and stop.
2. Map transcript sections to the outline questions.
3. Mark false starts and ad breaks.
4. Mark tangents: material that matches no outline question and adds nothing to the topic.
5. Give each entry a start, end, category and one-line reason.
6. If `cut-categories.md` has a "Clip Candidates" section, list 3 to 5 clip candidates with timestamps and an ffmpeg command for each, using `ffmpeg-setup.md`.
7. Run the audit and save.

## Audit

| Check | Pass Condition |
|-------|---------------|
| Complete entries | Every row has start, end, category and reason |
| Valid categories | Every category is one of those in `cut-categories.md` |
| Valid timestamps | Start is before end, both exist in the transcript, no overlapping rows |
| Planned material kept | No row cuts the main answer to an outline question |

## Outputs

| Artifact | Location | Format |
|----------|----------|--------|
| Cut list | `output/[episode-slug]-cut-list.md` | Markdown table: Start, End, Category, Reason. Plus a Clip Candidates table (Start, End, Why, ffmpeg command) when clips are enabled. |

No checkpoint: this is a linear marking stage. The user reviews the cut list while editing in Descript and may edit the output file before stage 04.
</file>

<file path="podcast-episode-pipeline/stages/03-cut-list/input/.gitkeep">
</file>

<file path="podcast-episode-pipeline/stages/03-cut-list/references/cut-categories.md">
# Cut Categories

## Categories

Use only these three values in the Category column.

### tangent
Off-topic material that matches no outline question and adds nothing to the topic. Do not mark material that is off-plan but strong; leave it in.

### false-start
A question or answer that is restarted, flubbed, or repeated right away. Cut the failed attempt and keep the clean take.

### ad-break
A pause, marker or spoken note left for an ad insertion, plus any live-read placeholder.

## Row Rules

- Format: `| Start | End | Category | Reason |`.
- Timestamps use the transcript format (see `descript-export-format.md`).
- The reason is one line on why the section goes.

{{?AUDIO_CLIPS}}

## Clip Candidates

List 3 to 5 moments of 20 to 60 seconds that work as standalone audio clips. Take them from uncut material only. Format: `| Start | End | Why | ffmpeg command |`, using the command in `ffmpeg-setup.md`.

{{/AUDIO_CLIPS}}
</file>

<file path="podcast-episode-pipeline/stages/03-cut-list/references/descript-export-format.md">
# Descript Export Format

## Timestamp Format

Default expectation: each speaker turn starts with a timestamp and a speaker label.

```
[00:12:34] Host Name: Question text...
[00:12:51] Guest Name: Answer text...
```

- Timestamps are `[HH:MM:SS]` measured from the start of the raw recording.
- A turn runs until the next timestamp.
- Confirm this pattern against the first real export. If Descript uses `MM:SS` or another layout, update this section once.

## File Naming

Save the export as `stages/03-cut-list/input/[episode-slug]-transcript.txt`.
</file>

<file path="podcast-episode-pipeline/stages/03-cut-list/references/descript-setup.md">
# Descript Setup

Descript runs outside the agent. This guide only covers getting a usable transcript out of it.

## Requirements
- A Descript account with the episode project transcribed.
- Speaker labels set for the host and the guest.

## Exporting a Transcript
1. Open the project in Descript.
2. Choose Publish (or File) > Export > Transcript.
3. Format: plain text (.txt).
4. Turn on timestamps (per paragraph or per speaker change) and speaker labels.
5. Export from the raw, unedited composition, so the timestamps match the recording.
6. Save as `[episode-slug]-transcript.txt` in `stages/03-cut-list/input/`.

## Troubleshooting
- No timestamps in the file: re-export with the timestamps option on.
- Wrong speaker names: fix the labels in Descript and re-export.
</file>

<file path="podcast-episode-pipeline/stages/03-cut-list/references/ffmpeg-setup.md">
# ffmpeg Setup (optional)

Used only when audio clips are enabled. If the section below has been removed, stage 03 skips clip candidates.

{{?AUDIO_CLIPS}}

## Install

- Windows: `winget install ffmpeg`
- macOS: `brew install ffmpeg`
- Linux: `sudo apt install ffmpeg`
- Check the install with `ffmpeg -version`.

## Clip Command

```
ffmpeg -i "[episode-audio-file]" -ss [START] -to [END] -c:a libmp3lame -q:a 2 "[episode-slug]-clip-[n].mp3"
```

- `[START]` and `[END]` use `HH:MM:SS` from the cut list.
- Run this against the raw recording audio, so the timestamps match the transcript.

{{/AUDIO_CLIPS}}
</file>

<file path="podcast-episode-pipeline/stages/03-cut-list/output/.gitkeep">
</file>

<file path="podcast-episode-pipeline/stages/04-show-notes/CONTEXT.md">
# Stage 04: Show Notes

Write publish-ready show notes from the edited episode.

## Inputs

| Source | File/Location | Section/Scope | Why |
|--------|--------------|---------------|-----|
| User (per episode, read-only) | `../03-cut-list/input/[episode-slug]-transcript.txt` | Full file | Summary, chapters, links mentioned, verbatim pull quote |
| Previous stage | `../03-cut-list/output/[episode-slug]-cut-list.md` | Cut table | Shift timestamps to the edited timeline; skip cut material |
| Earlier stage | `../01-research/output/[episode-slug]-guest-brief.md` | "Episode" header, "Bio", "Sources" | Guest bio, guest links, sponsor yes/no |
| Show identity | `../../brand-vault/show-identity.md` | "Show" and "Host" sections | Names in the notes |
| Voice rules | `../../brand-vault/voice-rules.md` | "Hard Constraints" through "What the Voice Is NOT" | Tone of the summary |
| Sponsor read (optional) | `../../brand-vault/sponsor-read.md` | "Sponsor" section | Only if the brief says `Sponsor: yes` and the section exists |
| Show notes format | `references/show-notes-format.md` | Full file | Section order, chapter rules, timestamp math |

## Process

1. Read the cut list and compute the edited timeline (each timestamp minus the total length of cuts before it), following `show-notes-format.md`.
2. Write the summary in the show's voice.
3. Build chapter markers from uncut sections, with edited-timeline timestamps.
4. List every link or resource mentioned in the transcript, plus the guest links from the brief's Sources.
5. Pick one pull quote verbatim from uncut material.
6. If the brief says `Sponsor: yes` and `sponsor-read.md` has a Sponsor section, add the sponsor section with the exact read text. Otherwise skip it.
7. **[Checkpoint]** Present the draft notes. The user approves or edits the summary, chapters and pull quote.
8. Run the audit and save.

## Checkpoints

| After Step | Agent Presents | Human Decides |
|------------|---------------|---------------|
| 6 | Draft show notes with chapters and pull quote | Summary edits, chapter titles, which pull quote to use |

## Audit

| Check | Pass Condition |
|-------|---------------|
| Sections | Summary, chapters, links and pull quote are present, in the order set by `show-notes-format.md` |
| Chapter timestamps | Every chapter falls on the edited timeline, outside cut ranges, in ascending order |
| Verbatim quote | The pull quote matches the transcript word for word and is not in a cut range |
| Links | Every link was mentioned in the transcript or is in the brief's Sources |
| Sponsor | Sponsor section appears only when the episode has a sponsor, with the exact read text |
| Voice | Summary breaks none of the hard constraints |

## Outputs

| Artifact | Location | Format |
|----------|----------|--------|
| Show notes | `output/[episode-slug]-show-notes.md` | Markdown: Title, Summary, Chapters (timestamp + title), Links Mentioned, Pull Quote, Sponsor (if any), About the Guest |
</file>

<file path="podcast-episode-pipeline/stages/04-show-notes/references/show-notes-format.md">
# Show Notes Format

## Section Order

1. Title: `[Guest Name]: [topic hook]`
2. Summary
3. Chapters
4. Links Mentioned
5. Pull Quote
6. Sponsor (only when the episode has a sponsor)
7. About the Guest

## Summary
120 to 200 words in the show's voice. Name the guest and the host. Mention no cut material.

## Chapters
- 5 to 10 chapters. The first one is `00:00`.
- Format: `MM:SS Title` (use `HH:MM:SS` past one hour).
- Titles are 3 to 8 words each.
- Chapters are in ascending order and never start inside a cut range.

## Timestamp Math
1. Sort the cut rows by start time.
2. For a raw timestamp T: edited T = T minus the sum of (end minus start) for every cut that ends at or before T.
3. If T falls inside a cut, move the chapter to the cut's end, then convert it.

## Links Mentioned
A bulleted list of `[Name](URL)` entries. Include resources named in the transcript and the guest links from the brief's Sources. If a mentioned resource has no URL, mark it `(link needed)`.

## Pull Quote
One quote of 1 to 3 sentences, verbatim, attributed to the guest, taken from uncut material.

{{?SPONSOR}}

## Sponsor
Heading `This episode is supported by [sponsor name]`. Below it, paste the read text from `brand-vault/sponsor-read.md` exactly, then the sponsor link or promo code. Include this only when the brief says `Sponsor: yes`.

{{/SPONSOR}}

## About the Guest
Two to three sentences from the brief's Bio, plus the guest's main link.
</file>

<file path="podcast-episode-pipeline/stages/04-show-notes/output/.gitkeep">
</file>

<file path="podcast-episode-pipeline/stages/05-social/CONTEXT.md">
# Stage 05: Social

Write one promotion post each for LinkedIn, X and Instagram.

## Inputs

| Source | File/Location | Section/Scope | Why |
|--------|--------------|---------------|-----|
| Previous stage | `../04-show-notes/output/[episode-slug]-show-notes.md` | Title, Summary, Pull Quote, About the Guest | Post content |
| Show identity | `../../brand-vault/show-identity.md` | "Show" and "Audience" sections | Who the posts speak to |
| Voice rules | `../../brand-vault/voice-rules.md` | Full file | Show voice for all three posts |
| Platform specs | `../../shared/platform-specs.md` | LinkedIn, X and Instagram sections | Length limits, hashtag and link rules |

## Process

1. Pick one hook per platform from the summary or the pull quote.
2. Draft the LinkedIn post.
3. Draft the X post.
4. Draft the Instagram caption.
5. **[Checkpoint]** Present all three posts. The user approves or edits.
6. Run the audit and save.

## Checkpoints

| After Step | Agent Presents | Human Decides |
|------------|---------------|---------------|
| 4 | Three draft posts | Edits per post, hook choice |

## Audit

| Check | Pass Condition |
|-------|---------------|
| Three platforms | Exactly one post each for LinkedIn, X and Instagram |
| Length limits | Each post is within its limit in `platform-specs.md` |
| Link and hashtag rules | Each post follows its platform's rules in `platform-specs.md` |
| Voice | No post breaks a hard constraint or matches a "wrong" example pattern |
| Facts | Every claim and quote appears in the show notes |

## Outputs

| Artifact | Location | Format |
|----------|----------|--------|
| Social posts | `output/[episode-slug]-social-posts.md` | Markdown: LinkedIn, X, Instagram sections (final deliverable) |
</file>

<file path="podcast-episode-pipeline/stages/05-social/references/.gitkeep">
</file>

<file path="podcast-episode-pipeline/stages/05-social/output/.gitkeep">
</file>