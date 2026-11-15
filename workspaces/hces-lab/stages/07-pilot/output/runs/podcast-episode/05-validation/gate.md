<file path="validation-report.md">
# Validation Report: Podcast Episode Pipeline

Stage 05 output for the workspace builder. This report validates the workspace generated in `../03-scaffolding/output/podcast-episode-pipeline/` and the questionnaire in `../04-questionnaire-design/output/questionnaire.md`. The rules come from `_core/CONVENTIONS.md` and `_core/placeholder-syntax.md`.

Corrected files are in `fixes/`, which mirrors the workspace tree. Copy them over the matching scaffold files. The questionnaire fix goes to `podcast-episode-pipeline/setup/questionnaire.md`.

## Summary

| # | Check | First run | After fixes |
|---|-------|-----------|-------------|
| 1 | Cross-reference integrity | Pass | Pass |
| 2 | No circular dependencies | **Fail** (2 issues) | Pass |
| 3 | Placeholder coverage | Pass, 1 issue | Pass |
| 4 | Conditional section validity | Pass | Pass |
| 5 | Stage handoff chain | Pass | Pass |
| 6 | CONTEXT.md purity | **Fail** (3 issues) | Pass |
| 7 | Checkpoints in creative stages | Pass | Pass |
| 8 | Audits in creative/build stages | Pass | Pass |
| 9 | Contract purity in spec stages | N/A | N/A |
| 10 | Line count | Pass | Pass |
| 11 | Naming conventions | Pass | Pass |
| 12 | Tool prerequisites | **Fail** (1 issue) | Pass |
| 13 | Quality scan | Pass, 1 issue | Pass |

## 1. Cross-Reference Integrity: Pass

I resolved every path in each stage's Inputs table against the generated tree.

- Fixed files: `brand-vault/show-identity.md`, `voice-rules.md`, `sponsor-read.md`, `shared/platform-specs.md`, and every `references/*.md` that is listed. All of them exist.
- Named sections: "Show", "Host" and "Audience" exist in show-identity. "Hard Constraints" through "What the Voice Is NOT" exist in voice-rules. "Timestamp Format", "Exporting a Transcript", "Clip Command" and "Sponsor" all exist.
- Per-episode paths: `[episode-slug]-guest-brief.md`, `-interview-outline.md`, `-transcript.txt` and `-cut-list.md` are created at run time. Each one matches the path that the producing stage declares in its Outputs table, or the user drop location for the transcript.
- Conditional targets: the "Clip Command" and "Sponsor" sections may be removed during onboarding. The Inputs rows that point to them already say "only if that section exists". This is acceptable.

Broken references: none.

## 2. No Circular Dependencies: Fail, then Pass

Dependency graph after the fixes (arrow means "reads from"):

```
01-research  --> brand-vault
02-outline   --> 01, brand-vault
03-cut-list  --> 02, 03/input
04-show-notes --> 03 (output + input), 01, brand-vault
05-social    --> 04, brand-vault, shared
brand-vault  --> (nothing)
shared       --> (nothing)
```

This is a directed acyclic graph.

Issues found:

1. **Stage 02 to stage 03 cycle.** Stage 02's CONTEXT.md ended with a Handoff line that pointed to `../03-cut-list/input/`, and stage 03 reads stage 02's output. Fix: I removed the line. The drop location is already documented in root `CLAUDE.md` (Stage Handoffs) and in stage 03's Inputs table.
2. **brand-vault points back to stages.** `brand-vault/CONTEXT.md` had a "Used By" column listing stages and said where per-episode facts live, which is the stage 01 brief. `sponsor-read.md` said "Used by stage 04 ... guest brief's Episode header". Pattern 3 says a shared folder must not reference its consumers. Fix: I removed the column and reworded both files so they describe only their own content.

## 3. Placeholder Coverage: Pass (1 issue fixed)

I found 16 placeholders, all in `brand-vault/` and `shared/`. None appear in any CONTEXT.md.

| Placeholder | Question |
|-------------|----------|
| SHOW_NAME, HOST_NAME, HOST_BIO, SHOW_FORMAT, SHOW_AUDIENCE, SHOW_TAGLINE, SHOW_URL | Q1 to Q7 |
| VOICE_EXAMPLE_RIGHT, VOICE_EXAMPLE_WRONG, VOICE_HARD_CONSTRAINTS | Q8, Q9, Q10 |
| VOICE_PACING, VOICE_NOT | Derived under Q8 and Q9, then confirmed in the voice review pass |
| SHOW_HASHTAGS | Q11 |
| SPONSOR_NAME, SPONSOR_READ_TEXT, SPONSOR_LINK | Q13 to Q15 |
| `{{?SPONSOR}}`, `{{?AUDIO_CLIPS}}` | Q12, Q16 |

- Orphaned placeholders: none.
- Orphaned questions: none.

Issue: the final step of the questionnaire said to scan "the whole workspace" for remaining `{{` patterns. `setup/questionnaire.md` itself contains those patterns, so onboarding could never finish. Fix: the scan now excludes `setup/questionnaire.md`. In the same file, I also corrected the Assumptions entry that cited the review pass as "step 9". It is now "After Onboarding, step 1".

## 4. Conditional Section Validity: Pass

| File | Block | Wraps |
|------|-------|-------|
| `brand-vault/sponsor-read.md` | SPONSOR | `## Sponsor` and all of its content |
| `stages/04-show-notes/references/show-notes-format.md` | SPONSOR | `## Sponsor` section |
| `stages/03-cut-list/references/cut-categories.md` | AUDIO_CLIPS | `## Clip Candidates` section |
| `stages/03-cut-list/references/ffmpeg-setup.md` | AUDIO_CLIPS | `## Install` and `## Clip Command` (two complete sections) |

No block wraps inline content. Removing any of these blocks leaves clean markdown.

## 5. Stage Handoff Chain: Pass

| From | Output | Read by |
|------|--------|---------|
| 01 | `01-research/output/[slug]-guest-brief.md` | 02 (full), 04 (Episode, Bio, Sources) |
| 02 | `02-outline/output/[slug]-interview-outline.md` | 03 |
| (recording) | `03-cut-list/input/[slug]-transcript.txt` | 03, 04 |
| 03 | `03-cut-list/output/[slug]-cut-list.md` | 04 |
| 04 | `04-show-notes/output/[slug]-show-notes.md` | 05 |

There are no gaps. File names follow `[topic-slug]-[artifact].md`.

## 6. CONTEXT.md Purity: Fail, then Pass

Issues found:

1. Stage 02 had a "Handoff" paragraph outside the allowed sections. It was removed (see check 2).
2. Stage 03 had a definition of a tangent in Process step 4, and a free paragraph after Outputs ("No checkpoint: this is a linear marking stage..."). Fix: step 4 now points to `cut-categories.md`, and the paragraph was removed. The rationale for having no checkpoint is recorded here instead.
3. Stage 04 Process step 1 restated the timestamp formula, which already lives in `show-notes-format.md`. Fix: the step now points to the "Timestamp Math" section.

Stage 01, stage 05, root `CONTEXT.md` and `brand-vault/CONTEXT.md` contain routing only.

## 7. Checkpoints in Creative Stages: Pass

| Stage | Type | Checkpoint |
|-------|------|------------|
| 01 research | Creative (angles) | After step 6 (step 7 is the checkpoint) |
| 02 outline | Creative | After step 3 (step 4). This is the user's required review and reorder. |
| 03 cut list | Linear | None (allowed) |
| 04 show notes | Creative | After step 6 (step 7) |
| 05 social | Creative | After step 4 (step 5) |

Every "After Step" number points to a real step that comes right before the step marked [Checkpoint].

## 8. Audits: Pass

All five stages have an Audit table. In each one, the audit runs as the last process step, after any checkpoint and before saving. The pass conditions are concrete: word and question counts, verbatim match, timestamp ordering, and platform limits.

## 9. Contract Purity in Spec Stages: N/A

The workspace has no specification stage. The outline is a script the host reads aloud, not a build spec.

## 10. Line Count: Pass

- Longest CONTEXT.md: stage 04, about 55 lines. All are under 80.
- All reference files are under 60 lines.

## 11. Naming Conventions: Pass

- All names are lowercase-with-hyphens.
- Stage folders are numbered 01 to 05.
- `.gitkeep` files exist in every output/, in `03-cut-list/input/` and in `05-social/references/`.

## 12. Tool Prerequisites: Fail, then Pass

There is no `prerequisites/` folder. Setup guides live in `stages/03-cut-list/references/`, as Pattern 7 allows. The questionnaire asks about the optional tool in Q16 and removes the conditional sections if the answer is no.

Issue: Pattern 7 requires each guide to cover what the tool is, how to install it, how to verify it works, and how the workspace uses it.

- `descript-setup.md` had no description, no install step and no verification.
- `ffmpeg-setup.md` had no one-sentence description.

Fix: I added "What It Is", "Install" and "Verify" to the Descript guide. I added a one-sentence description and a usage line to the ffmpeg guide.

## 13. Quality Scan: Pass (1 issue fixed)

- Em dashes: none found.
- Markdown: no formatting problems.
- Jargon: "episode slug" is used in root `CLAUDE.md` before it is defined in stage 01. Fix: none needed in that file. The term is defined where it is created, in stage 01 step 1 and `brief-format.md`. This is acceptable.
- The questionnaire issues are fixed under check 3.

## Fixes Applied

| File | Change |
|------|--------|
| `stages/02-outline/CONTEXT.md` | Removed the Handoff line that pointed to stage 03 |
| `stages/03-cut-list/CONTEXT.md` | Step 4 now points to the reference file; removed the trailing paragraph |
| `stages/04-show-notes/CONTEXT.md` | Step 1 now points to "Timestamp Math" |
| `brand-vault/CONTEXT.md` | Removed the "Used By" column and the reference to stage outputs |
| `brand-vault/sponsor-read.md` | Removed the references to stage 04 and the guest brief |
| `stages/03-cut-list/references/descript-setup.md` | Added What It Is, Install and Verify |
| `stages/03-cut-list/references/ffmpeg-setup.md` | Added a description and a usage line |
| `setup/questionnaire.md` | Placeholder scan now excludes this file; fixed the step reference |

I re-ran checks 2, 3, 6, 12 and 13 on the fixed files, and all of them pass.

## Assumptions

- **No live review:** No user review was possible. All fixes were chosen to match the workflow description and the upstream decisions.
- **Where the fixes are saved:** This stage can only write to its own output folder. The fixes are therefore delivered as full replacement files under `fixes/`, in place of editing the scaffold directly.
- **Descriptions are not references:** Root `CLAUDE.md` describes the transcript drop location and the order of the stages. Root routing files sit above the stages, so they do not create cycles.
- **Two sections in one block:** The AUDIO_CLIPS block in `ffmpeg-setup.md` wraps two complete sections. This counts as valid, because each section inside it is whole.
- **Derived voice fields:** VOICE_PACING and VOICE_NOT count as covered. Each is derived from a question and confirmed by the user in the voice review pass.
</file>

<file path="fixes/podcast-episode-pipeline/stages/02-outline/CONTEXT.md">
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
</file>

<file path="fixes/podcast-episode-pipeline/stages/03-cut-list/CONTEXT.md">
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
4. Mark tangents, as defined in `cut-categories.md`.
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
</file>

<file path="fixes/podcast-episode-pipeline/stages/04-show-notes/CONTEXT.md">
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

<file path="fixes/podcast-episode-pipeline/brand-vault/CONTEXT.md">
# Brand Vault

Persistent show context. Set once at onboarding and changed only when the show changes.

| File | Contains |
|------|----------|
| `show-identity.md` | Show, Host, Audience sections |
| `voice-rules.md` | Hard Constraints, Sentence Rules, Pacing, What the Voice Is NOT |
| `sponsor-read.md` | Sponsor name, read text, link (optional) |

Per-episode facts (guest, topic, date, sponsor yes/no) do not live here.
</file>

<file path="fixes/podcast-episode-pipeline/brand-vault/sponsor-read.md">
# Sponsor Read

The show's standing sponsor read. Use it only for episodes that have a sponsor. If the section below has been removed, the show has no sponsors.

{{?SPONSOR}}

## Sponsor

- Name: {{SPONSOR_NAME}}
- Link or promo code: {{SPONSOR_LINK}}

Read text (use exactly, do not rewrite):

{{SPONSOR_READ_TEXT}}

{{/SPONSOR}}
</file>

<file path="fixes/podcast-episode-pipeline/stages/03-cut-list/references/descript-setup.md">
# Descript Setup

## What It Is
Descript is an audio and video editor that turns recordings into an editable text transcript. This workspace uses its plain-text transcript export as the input to the cut list.

## Install
1. Create an account at descript.com.
2. Download the desktop app for Windows or macOS and sign in.

## Verify
Open the app, import a short test recording, and confirm that a transcript appears with speaker labels.

## Requirements
- The episode project is transcribed.
- Speaker labels are set for the host and the guest.

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

<file path="fixes/podcast-episode-pipeline/stages/03-cut-list/references/ffmpeg-setup.md">
# ffmpeg Setup (optional)

ffmpeg is a free command-line tool that cuts and converts audio and video files. This workspace uses it to cut short audio clips from the raw recording. It is used only when audio clips are enabled. If the sections below have been removed, stage 03 skips clip candidates.

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

<file path="fixes/podcast-episode-pipeline/setup/questionnaire.md">
# Onboarding Questionnaire: Podcast Episode Pipeline

<!-- Agent instructions: Read this file when the user types "setup". Show ALL questions below
     in one message. The user answers in one reply and can skip any question. A skipped
     question takes its default. Replace each placeholder in the listed files by string
     substitution. Fill derived fields without asking. Apply the conditional logic. Then run
     the voice review pass in "After Onboarding". Last, scan the workspace (excluding this
     file) for any remaining {{ patterns and ask about any that remain. -->

<!-- Per-episode values are NOT asked here: guest name, topic, recording date, whether this
     episode has a sponsor, and the Descript transcript. Stage 01 collects guest, topic,
     date and sponsor yes/no at the start of each run (see stages/01-research/CONTEXT.md,
     Process step 1, and the Episode header in references/brief-format.md). The transcript
     goes into stages/03-cut-list/input/ (see the Stage Handoffs section of CLAUDE.md). -->

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
- Derived field: `{{VOICE_PACING}}`. The agent reads sentence length and rhythm from these examples, for instance "Short sentences. One idea each. Questions land at the end of a line." The user does not have to describe pacing.

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
- If NO: Remove the `{{?AUDIO_CLIPS}}...{{/AUDIO_CLIPS}}` blocks and everything inside them from `stages/03-cut-list/references/cut-categories.md` and `stages/03-cut-list/references/ffmpeg-setup.md`. Stage 03 then skips clip candidates.
- If YES: Keep both sections and delete only the marker lines. Tell the user to follow the Install section of `stages/03-cut-list/references/ffmpeg-setup.md`.

---

## After Onboarding

1. **Voice review (second pass).** Before saving the files, show the user the finished `brand-vault/voice-rules.md`. This includes the derived Pacing section, the derived "What the Voice Is NOT" list, the numbered hard constraints with any rules added from Q9, and the tagline if it was derived. Ask: "Does this match your show? Change anything that is off." Apply the edits, then save.
2. **Placeholder scan.** Scan every workspace file except this questionnaire for any remaining `{{` patterns, including conditional markers. If any remain, ask for the missing information. Onboarding is complete only when none remain.
3. **Tell the user what was set up:** the show identity, voice rules, hashtags, the sponsor section (on or off) and audio clips (on or off).
4. **Descript check.** Remind the user to export transcripts with timestamps and speaker labels on (see `stages/03-cut-list/references/descript-setup.md`). Also remind them to confirm the timestamp format against their first export in `stages/03-cut-list/references/descript-export-format.md`.
5. **Where to start.** "To start an episode, go to `stages/01-research/CONTEXT.md` and give the guest name, topic, recording date and whether this episode has a sponsor."

## Assumptions

- **No live user:** The questions and defaults are based only on the workflow description and the upstream outputs.
- **Sponsor details are system-level:** The per-episode decision is only yes or no, collected at stage 01. If sponsors change, edit `brand-vault/sponsor-read.md` directly.
- **Voice fields are derived:** VOICE_PACING and VOICE_NOT are derived from the examples. The voice review pass (After Onboarding, step 1) confirms them.
- **Derived defaults:** The tagline, host bio and hashtags fall back to values built from other answers.
- **Audio clips default to "no"**, because ffmpeg is optional. The sponsor section defaults to "yes", because only some episodes have no sponsor.
- **Descript** needs no placeholder. It is covered by a reminder after onboarding.
</file>