<file path="validation-report.md">
# Validation Report: Podcast Episode Pipeline

Stage 05 output for the workspace builder. This report checks the workspace scaffolded in stage 03 (`podcast-episode-pipeline/`) and the stage 04 questionnaire against `_core/CONVENTIONS.md` and `_core/placeholder-syntax.md`.

Corrected copies of every changed file are saved next to this report, under `podcast-episode-pipeline/`. They replace the files with the same path in the scaffold.

## Summary

| # | Check | First Run | After Fixes |
|---|-------|-----------|-------------|
| 1 | Cross-reference integrity | Fail (1 issue) | Pass |
| 2 | No circular dependencies | Fail (2 issues) | Pass |
| 3 | Placeholder coverage | Pass with 2 issues | Pass |
| 4 | Conditional section validity | Pass | Pass |
| 5 | Stage handoff chain | Pass | Pass |
| 6 | CONTEXT.md purity | Fail (3 issues) | Pass |
| 7 | Checkpoints in creative stages | Pass | Pass |
| 8 | Audits in creative/build stages | Pass with 1 issue | Pass |
| 9 | Contract purity in spec stages | N/A (no spec stage) | N/A |
| 10 | Line count | Pass | Pass |
| 11 | Naming conventions | Pass | Pass |
| 12 | Tool prerequisites | Fail (2 issues) | Pass |
| 13 | Quality scan | Pass | Pass |

## Check Details

### 1. Cross-reference integrity: Fail, then Pass

Every path in the stage Inputs tables resolves:

- 01: `brand-vault/show-identity.md`, `references/brief-format.md`, `references/research-sources.md`. All exist.
- 02: 01 output brief (produced per episode), `show-identity.md`, `voice-rules.md`, `references/outline-format.md`, `references/question-rules.md`. All exist.
- 03: `input/[slug]-transcript.txt` (user-supplied per episode), 02 output outline, `cut-categories.md`, `descript-export-format.md` ("Timestamp Format" exists), `descript-setup.md` ("Exporting a Transcript" exists), `ffmpeg-setup.md` ("Clip Command" exists, conditional). All exist.
- 04: transcript, 03 output, 01 output, `show-identity.md`, `voice-rules.md`, `sponsor-read.md` ("Sponsor" exists, conditional), `show-notes-format.md`. All exist.
- 05: 04 output, `show-identity.md`, `voice-rules.md`, `shared/platform-specs.md`. All exist.

**Issue 1.1:** The `setup` trigger in `CLAUDE.md` points to `setup/questionnaire.md`, but the scaffold version is still the stub. The real questionnaire is in stage 04 output.
**Fix:** Copied the stage 04 questionnaire into `setup/questionnaire.md`, with the fixes from check 3.

### 2. No circular dependencies: Fail, then Pass

Dependency graph (arrows point from the reader to what it reads):

```
01-research   --> brand-vault
02-outline    --> 01, brand-vault
03-cut-list   --> 02, 03/input
04-show-notes --> 03, 03/input, 01, brand-vault
05-social     --> 04, brand-vault, shared
setup         --> brand-vault, shared, stages/*/references (fill targets only)
```

**Issue 2.1:** The Handoff line in `stages/02-outline/CONTEXT.md` names `../03-cut-list/input/[episode-slug]-transcript.txt`. Stage 03 reads stage 02's output, so this makes a 02 <-> 03 back-reference.
**Fix:** The line now says that recording happens outside the workspace before the next stage. It no longer names a stage 03 path. The transcript location is still documented in the root `CLAUDE.md` Stage Handoffs and in stage 03's own Inputs table.

**Issue 2.2:** `brand-vault/CONTEXT.md` (the "Used By" column and the line about guest briefs) and `brand-vault/sponsor-read.md` ("Used by stage 04 ... guest brief's Episode header") reference stages. Pattern 3 says the brand vault references no stage.
**Fix:** Removed the stage references from both files. Which stages use the brand vault is still listed in the root `CLAUDE.md` What to Load table.

After the fixes, the graph is a directed acyclic graph. All references point toward earlier stages or toward the shared folders (`brand-vault/`, `shared/`).

### 3. Placeholder coverage: Pass with 2 issues, then Pass

Placeholders found in the scaffold (16), each with the question that fills it:

| Placeholder | File | Filled by |
|-------------|------|-----------|
| SHOW_NAME | show-identity.md | Q1 |
| HOST_NAME | show-identity.md | Q2 |
| HOST_BIO | show-identity.md | Q3 |
| SHOW_FORMAT | show-identity.md | Q4 |
| SHOW_AUDIENCE | show-identity.md | Q5 |
| SHOW_TAGLINE | show-identity.md | Q6 |
| SHOW_URL | show-identity.md | Q7 |
| VOICE_EXAMPLE_RIGHT | voice-rules.md | Q8 |
| VOICE_PACING | voice-rules.md | Derived from Q8 |
| VOICE_EXAMPLE_WRONG | voice-rules.md | Q9 |
| VOICE_NOT | voice-rules.md | Derived from Q9 |
| VOICE_HARD_CONSTRAINTS | voice-rules.md | Q10 |
| SHOW_HASHTAGS | platform-specs.md | Q11 |
| SPONSOR_NAME | sponsor-read.md | Q13 |
| SPONSOR_READ_TEXT | sponsor-read.md | Q14 |
| SPONSOR_LINK | sponsor-read.md | Q15 |
| `{{?SPONSOR}}` | sponsor-read.md, show-notes-format.md | Q12 |
| `{{?AUDIO_CLIPS}}` | cut-categories.md, ffmpeg-setup.md | Q16 |

There are no orphaned placeholders and no orphaned questions. No placeholders appear in a `CLAUDE.md` or `CONTEXT.md`.

**Issue 3.1:** The final scan in the questionnaire ("scan the whole workspace for any remaining `{{`") would match the placeholder names written inside `setup/questionnaire.md` itself, so onboarding could never finish.
**Fix:** The scan now excludes `setup/questionnaire.md`, both in the agent instructions and in After Onboarding step 2.

**Issue 3.2:** The questionnaire's Assumptions point to a "step 9" voice review, but the voice review is After Onboarding step 1. The stage 04 Audit and Assumptions sections are builder notes, so they should not ship inside the workspace.
**Fix:** These two sections were left out of the shipped `setup/questionnaire.md`. They stay on record in stage 04 output.

### 4. Conditional section validity: Pass

- `sponsor-read.md`: `{{?SPONSOR}}` wraps `## Sponsor` through the end of the file.
- `show-notes-format.md`: `{{?SPONSOR}}` wraps `## Sponsor` up to `## About the Guest`.
- `cut-categories.md`: `{{?AUDIO_CLIPS}}` wraps `## Clip Candidates` through the end of the file.
- `ffmpeg-setup.md`: `{{?AUDIO_CLIPS}}` wraps `## Install` and `## Clip Command`. These are two complete sections.

No conditional is used inline. Stage 03 moved the inline conditionals out of the contracts before this check ran.

### 5. Stage handoff chain: Pass

| From | Output | Read by |
|------|--------|---------|
| 01 | `01-research/output/[slug]-guest-brief.md` | 02 (and 04) |
| 02 | `02-outline/output/[slug]-interview-outline.md` | 03 |
| 03 | `03-cut-list/output/[slug]-cut-list.md` | 04 |
| 04 | `04-show-notes/output/[slug]-show-notes.md` | 05 |
| 05 | `05-social/output/[slug]-social-posts.md` | Final deliverable |

Between 02 and 03 there is an outside step: the recording, then the Descript export placed in `03-cut-list/input/`. This step is documented in the root `CLAUDE.md` and in stage 03's Inputs table.

### 6. CONTEXT.md purity: Fail, then Pass

**Issue 6.1:** Stage 04 Process step 1 restates the timestamp formula ("each timestamp minus the total length of cuts before it"). This repeats `show-notes-format.md` and does not match it: the reference counts only cuts that end at or before T, and it also covers timestamps that fall inside a cut.
**Fix:** Step 1 now only points to the "Timestamp Math" section.

**Issue 6.2:** Stage 03 Process step 4 restates the definition of a tangent, which `cut-categories.md` already holds.
**Fix:** Step 4 now points to `cut-categories.md`.

**Issue 6.3:** Stage 03 ends with a note after the Outputs table explaining why there is no checkpoint. This is content outside the allowed sections.
**Fix:** Removed the note. The root `CLAUDE.md` already says that users may edit output files between stages.

The other CONTEXT.md files contain only a title, a description, Inputs, Process, Checkpoints, Audit and Outputs.

### 7. Checkpoints in creative stages: Pass

| Stage | Type | Checkpoint | Step valid |
|-------|------|------------|-----------|
| 01 Research | Creative (brief, angles) | After 6 | Yes (8 steps) |
| 02 Outline | Creative | After 3 (required every episode) | Yes (6 steps) |
| 03 Cut list | Linear marking | None (allowed) | n/a |
| 04 Show notes | Creative | After 6 | Yes (8 steps) |
| 05 Social | Creative | After 4 | Yes (6 steps) |

The user's request to review and reorder the questions before every recording is met by the stage 02 checkpoint.

### 8. Audits in creative/build stages: Pass with 1 issue, then Pass

All five stages have an Audit section. In each stage, the audit step comes after the process work and before the save.

**Issue 8.1:** The stage 01 Citations check requires a source link for every claim. `brief-format.md` also allows a claim to be marked `(unverified)`. With both rules in place, pass or fail is ambiguous.
**Fix:** The pass condition now reads "has a source number or is marked `(unverified)`".

### 9. Contract purity in spec stages: N/A

The workspace has no specification stage. The interview outline is a recording script, not a build spec.

### 10. Line count: Pass

All CONTEXT.md files are under 80 lines; the longest is stage 04, at about 50 lines. All reference files are under 200 lines.

### 11. Naming conventions: Pass

- Every folder and file name is lowercase-with-hyphens.
- Stage folders are numbered 01- to 05-.
- `.gitkeep` files are present in all five `output/` folders, in `03-cut-list/input/` and in `05-social/references/`.
- Output artifacts follow `[episode-slug]-[artifact].md`.

### 12. Tool prerequisites: Fail, then Pass

There is no `prerequisites/` folder. Following Pattern 7, the setup guides live in `stages/03-cut-list/references/`. Descript is the only required tool. ffmpeg is optional, and Q16 asks whether it is needed, so clip content can be removed.

**Issue 12.1:** `descript-setup.md` has no one-sentence description of the tool and no way to verify the setup.
**Fix:** Added a one-line description and a "Check the Export" section, which confirms that the first line of the file matches the expected timestamp and speaker pattern.

**Issue 12.2:** `ffmpeg-setup.md` has no one-sentence description of the tool.
**Fix:** Added one sentence, outside the conditional so it remains after removal. The guide already had install steps, the `ffmpeg -version` check and how the workspace uses it.

### 13. Quality scan: Pass

- No em dashes were found.
- The term "slug" is defined at its first use, in stage 01 step 1.
- The ffmpeg flags appear only inside a copy-ready command.
- No markdown formatting issues were found.

## Fixes Applied (files replaced)

- `podcast-episode-pipeline/setup/questionnaire.md`
- `podcast-episode-pipeline/brand-vault/CONTEXT.md`
- `podcast-episode-pipeline/brand-vault/sponsor-read.md`
- `podcast-episode-pipeline/stages/01-research/CONTEXT.md`
- `podcast-episode-pipeline/stages/02-outline/CONTEXT.md`
- `podcast-episode-pipeline/stages/03-cut-list/CONTEXT.md`
- `podcast-episode-pipeline/stages/03-cut-list/references/descript-setup.md`
- `podcast-episode-pipeline/stages/03-cut-list/references/ffmpeg-setup.md`
- `podcast-episode-pipeline/stages/04-show-notes/CONTEXT.md`

All failed checks were re-run after the fixes, and all now pass.

## Assumptions

- **Where the fixes are written:** This stage can only write to its own output folder. The corrected files are saved here under `podcast-episode-pipeline/`, using the same relative paths as the scaffold. They replace the stage 03 versions when the workspace ships.
- **Questionnaire placement:** The stage 04 questionnaire is copied into `setup/questionnaire.md` without its builder-only Audit and Assumptions sections.
- **Back-references:** Back-references from the brand vault, and from stage 02 to stage 03, count as Pattern 3 violations even when they are only prose rather than Inputs table rows. Removing them keeps the reference graph one-way.
- **No live review:** No user was available. Each fix keeps the behavior the user described and changes only where the information lives.
</file>

<file path="podcast-episode-pipeline/setup/questionnaire.md">
# Onboarding Questionnaire: Podcast Episode Pipeline

<!-- Agent instructions: Read this file when the user types "setup". Show ALL questions below
     in one message. The user answers in one reply and can skip any question. A skipped
     question takes its default. Replace each placeholder in the listed files by string
     substitution. Fill derived fields without asking. Apply the conditional logic. Then run
     the voice review pass in "After Onboarding". Last, scan the workspace (excluding this
     file) for any remaining {{ patterns and ask about any that remain. -->

<!-- Per-episode values are NOT asked here: guest name, topic, recording date, whether this
     episode has a sponsor, and the Descript transcript. Stage 01 collects guest, topic,
     date and sponsor yes/no at the start of each run. The transcript goes into
     stages/03-cut-list/input/. -->

### Q1: What is the name of your podcast?
- Placeholder: `{{SHOW_NAME}}`
- Files: `brand-vault/show-identity.md`
- Type: free text
- Default: none. This is required. Example: "The Long Game"

### Q2: Who hosts the show? Give the name the guests and listeners hear.
- Placeholder: `{{HOST_NAME}}`
- Files: `brand-vault/show-identity.md`
- Type: free text
- Default: none. This is required. Example: "Maya Chen"

### Q3: In one or two sentences, who is the host, as you would say it in an intro?
- Placeholder: `{{HOST_BIO}}`
- Files: `brand-vault/show-identity.md`
- Type: free text
- Default: "[Host name] hosts [show name], a weekly interview show."
- Derived if skipped: the agent builds the default from the answers to Q1 and Q2.

### Q4: How does an episode usually run? Give the length, whether it is one guest or several, and anything else that is always the same.
- Placeholder: `{{SHOW_FORMAT}}`
- Files: `brand-vault/show-identity.md`
- Type: free text
- Default: "Weekly one-on-one interview, about 45 to 60 minutes, one guest per episode."

### Q5: Who listens to the show? Describe the typical listener in a sentence or two, including their job or situation and what they want from the show.
- Placeholder: `{{SHOW_AUDIENCE}}`
- Files: `brand-vault/show-identity.md`
- Type: free text
- Default: "Curious professionals who want practical, candid conversations with people doing interesting work."

### Q6: Does the show have a tagline or one-line description? Paste it exactly as written.
- Placeholder: `{{SHOW_TAGLINE}}`
- Files: `brand-vault/show-identity.md`
- Type: free text
- Default: none. If you skip this, it is derived (see below).
- Derived if skipped: the agent writes a single line from Q4 and Q5. That line is shown in the voice review pass.

### Q7: What is the show's main link, the one listeners should use to find episodes?
- Placeholder: `{{SHOW_URL}}`
- Files: `brand-vault/show-identity.md`
- Type: free text (URL)
- Default: "(link needed)". Social posts will flag the missing link until you add it.

### Q8: Paste 2 or 3 sentences that sound exactly like your show. These can come from an intro, an episode description or a post you liked.
- Placeholder: `{{VOICE_EXAMPLE_RIGHT}}`
- Files: `brand-vault/voice-rules.md`
- Type: free text (examples)
- Default: "Today's guest spent ten years building something most people said couldn't work. We talk about what they got wrong first."
- Derived field: `{{VOICE_PACING}}`. The agent reads sentence length and rhythm from these examples, for instance "Short sentences. One idea each. Questions land at the end of a line."

### Q9: Paste 2 or 3 sentences that do NOT sound like your show. These can be from other podcasts or marketing copy you dislike, or you can make them up.
- Placeholder: `{{VOICE_EXAMPLE_WRONG}}`
- Files: `brand-vault/voice-rules.md`
- Type: free text (examples)
- Default: "In this game-changing episode, we dive deep into the incredible journey of an absolute legend! Don't miss it!!"
- Derived field: `{{VOICE_NOT}}`. The agent turns the patterns in these examples into a short "the voice is not" list, for instance "Not hype. Not exclamation-heavy. No buzzwords like 'dive deep'."

### Q10: List any hard rules the show's writing must never break. These can be specific words, punctuation, emoji, or how you refer to guests.
- Placeholder: `{{VOICE_HARD_CONSTRAINTS}}`
- Files: `brand-vault/voice-rules.md`
- Type: free text (list)
- Default: "1. No exclamation marks. 2. No emoji except on Instagram. 3. Refer to the guest by first name after the first mention. 4. Never promise what the guest 'reveals'."
- Derived addition: the agent turns the patterns from Q9 into numbered rules and adds them after the user's own rules.

### Q11: Which hashtags should always be available for the show's posts? List 1 to 5.
- Placeholder: `{{SHOW_HASHTAGS}}`
- Files: `shared/platform-specs.md`
- Type: free text (list)
- Default: one hashtag made from the show name, for example `#TheLongGame`, plus `#podcast`.
- Derived if skipped: the agent builds the hashtags from Q1.

### Q12: Does the show ever have sponsors? (Each episode you still say yes or no when you start it.)
- Type: yes/no
- Default: yes
- If NO: Remove the `{{?SPONSOR}}...{{/SPONSOR}}` blocks and everything inside them from `brand-vault/sponsor-read.md` and `stages/04-show-notes/references/show-notes-format.md`. Skip Q13 to Q15.
- If YES: Keep both sections. Delete only the `{{?SPONSOR}}` and `{{/SPONSOR}}` marker lines, then answer Q13 to Q15.

### Q13: (Only if Q12 is yes) What is the usual sponsor's name?
- Placeholder: `{{SPONSOR_NAME}}`
- Files: `brand-vault/sponsor-read.md`
- Type: free text
- Default: "(sponsor name needed)". You can change it in `brand-vault/sponsor-read.md` whenever the sponsor changes.

### Q14: (Only if Q12 is yes) Paste the sponsor read exactly as it should appear in the show notes. It is used word for word.
- Placeholder: `{{SPONSOR_READ_TEXT}}`
- Files: `brand-vault/sponsor-read.md`
- Type: free text (verbatim)
- Default: "This episode is supported by [sponsor]. Learn more at the link below."

### Q15: (Only if Q12 is yes) What is the sponsor link or promo code?
- Placeholder: `{{SPONSOR_LINK}}`
- Files: `brand-vault/sponsor-read.md`
- Type: free text
- Default: "(link needed)"

### Q16: Do you want short audio clips made with ffmpeg? These are 3 to 5 clip suggestions per episode, each with a ready-to-run command. ffmpeg is optional and installed separately.
- Type: yes/no
- Default: no
- If NO: Remove the `{{?AUDIO_CLIPS}}...{{/AUDIO_CLIPS}}` blocks and everything inside them from `stages/03-cut-list/references/cut-categories.md` and `stages/03-cut-list/references/ffmpeg-setup.md`.
- If YES: Keep both sections and delete only the marker lines. Tell the user to follow the Install section of `stages/03-cut-list/references/ffmpeg-setup.md`.

---

## After Onboarding

1. **Voice review (second pass).** Before saving, show the user the finished `brand-vault/voice-rules.md`. This includes the derived Pacing section, the derived "What the Voice Is NOT" list, the numbered hard constraints with any rules added from Q9, and the tagline if it was derived. Ask: "Does this match your show? Change anything that is off." Apply the edits, then save.
2. **Placeholder scan.** Scan the whole workspace, except this file, for any remaining `{{` patterns, including conditional markers. If any remain, ask for the missing information. Onboarding is complete only when none remain.
3. **Tell the user what was set up:** the show identity, voice rules, hashtags, the sponsor section (on or off) and audio clips (on or off).
4. **Descript check.** Remind the user to export transcripts with timestamps and speaker labels on (see `stages/03-cut-list/references/descript-setup.md`). Also remind them to confirm the timestamp format against their first export in `stages/03-cut-list/references/descript-export-format.md`.
5. **Where to start.** "To start an episode, go to `stages/01-research/CONTEXT.md` and give the guest name, topic, recording date and whether this episode has a sponsor."
</file>

<file path="podcast-episode-pipeline/brand-vault/CONTEXT.md">
# Brand Vault

Persistent show context. Set once at onboarding and changed only when the show changes.

| File | Contains |
|------|----------|
| `show-identity.md` | Show, Host, Audience sections |
| `voice-rules.md` | Hard Constraints, Sentence Rules, Pacing, What the Voice Is NOT |
| `sponsor-read.md` | Sponsor name, read text, link (optional) |

Per-episode facts (guest, topic, date, sponsor yes/no) do not live here.
</file>

<file path="podcast-episode-pipeline/brand-vault/sponsor-read.md">
# Sponsor Read

Used only for episodes that have a sponsor. If the section below has been removed, the show has no sponsors.

{{?SPONSOR}}

## Sponsor

- Name: {{SPONSOR_NAME}}
- Link or promo code: {{SPONSOR_LINK}}

Read text (use exactly, do not rewrite):

{{SPONSOR_READ_TEXT}}

{{/SPONSOR}}
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
| Citations | Every factual claim has a source number or is marked `(unverified)` |
| Episode header | Guest, topic, date, slug and sponsor yes/no are filled in |

## Outputs

| Artifact | Location | Format |
|----------|----------|--------|
| Guest brief | `output/[episode-slug]-guest-brief.md` | Markdown: Episode header, Bio, Book or Company, Past Interviews (incl. common questions), Public Positions on the Topic, Possible Angles, Sources |
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

**Handoff:** The episode is recorded outside the workspace before the next stage runs.
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
4. Mark tangents as defined in `cut-categories.md`.
5. Give each entry a start, end, category and one-line reason.
6. If `cut-categories.md` has a "Clip Candidates" section, list clip candidates as it describes, using `ffmpeg-setup.md`.
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
</file>

<file path="podcast-episode-pipeline/stages/03-cut-list/references/descript-setup.md">
# Descript Setup

Descript is an audio and video editor that transcribes recordings. It runs outside the agent, and this workspace only needs its transcript export.

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

## Check the Export
Open the file. The first line should look like `[00:00:05] Host Name: ...`. If it does not, see Troubleshooting, or update `descript-export-format.md` to match the layout Descript produced.

## Troubleshooting
- No timestamps in the file: re-export with the timestamps option on.
- Wrong speaker names: fix the labels in Descript and re-export.
</file>

<file path="podcast-episode-pipeline/stages/03-cut-list/references/ffmpeg-setup.md">
# ffmpeg Setup (optional)

ffmpeg is a free command-line tool that cuts and converts audio and video files. It is used only when audio clips are enabled. If the sections below have been removed, stage 03 skips clip candidates.

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

1. Read the cut list and compute the edited timeline using the "Timestamp Math" section of `show-notes-format.md`.
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