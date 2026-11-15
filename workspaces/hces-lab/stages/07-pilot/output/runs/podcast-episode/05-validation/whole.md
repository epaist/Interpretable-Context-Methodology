<file path="validation-report.md">
# Validation Report: Podcast Episode Pipeline

Stage 05 output for the workspace builder. I validated the workspace in `../03-scaffolding/output/podcast-episode-pipeline/` and the questionnaire in `../04-questionnaire-design/output/questionnaire.md` against `_core/CONVENTIONS.md` and `_core/placeholder-syntax.md`.

This stage can only write to its own output folder. Corrected copies of every changed file are therefore saved under `output/podcast-episode-pipeline/`, at the same relative paths as in the scaffold. To ship the workspace, copy these files over the scaffold. Files not listed here passed unchanged.

## Summary

| # | Check | First run | After fixes |
|---|-------|-----------|-------------|
| 1 | Cross-reference integrity | Fail (1 issue) | Pass |
| 2 | No circular dependencies | Fail (2 issues) | Pass |
| 3 | Placeholder coverage | Pass (1 related issue) | Pass |
| 4 | Conditional section validity | Pass | Pass |
| 5 | Stage handoff chain | Pass | Pass |
| 6 | CONTEXT.md purity | Fail (4 issues) | Pass |
| 7 | Checkpoints in creative stages | Pass | Pass |
| 8 | Audits in creative/build stages | Pass | Pass |
| 9 | Contract purity in spec stages | Not applicable | Not applicable |
| 10 | Line count | Pass | Pass |
| 11 | Naming conventions | Pass | Pass |
| 12 | Tool prerequisites | Fail (2 issues) | Pass |
| 13 | Quality scan | Pass | Pass |

## Check Details

### 1. Cross-reference integrity

I checked every path in every Inputs table:
- Stage 01: `brand-vault/show-identity.md`, `references/brief-format.md` and `references/research-sources.md` all exist.
- Stage 02: the 01 output pattern, `show-identity.md`, `voice-rules.md`, `outline-format.md` and `question-rules.md` all exist.
- Stage 03: the `input/` transcript pattern, the 02 output pattern, `cut-categories.md`, `descript-export-format.md`, `descript-setup.md` and `ffmpeg-setup.md` all exist. Every named section ("Timestamp Format", "Exporting a Transcript" and "Clip Command") is present.
- Stage 04: the transcript, the 03 output, the 01 output, the brand-vault files and `show-notes-format.md` all exist. The "Sponsor" section exists in `sponsor-read.md`.
- Stage 05: the 04 output, the brand-vault files and `shared/platform-specs.md` all exist.

**Issue 1.1:** CLAUDE.md routes `setup` to `setup/questionnaire.md`, but that file is still the stage 03 stub. The real questionnaire is only in stage 04's output.
**Fix:** I installed the questionnaire as `setup/questionnaire.md`. The stage 04 Audit and Assumptions sections were left out, because they are build notes and not onboarding content. As a result, the stale "step 9" reference in those Assumptions does not ship.

### 2. No circular dependencies

Dependency graph after the fixes (an arrow means "reads from"):

```
01-research   -> brand-vault, 01/references
02-outline    -> 01/output, brand-vault, 02/references
03-cut-list   -> 03/input, 02/output, 03/references
04-show-notes -> 03/input, 03/output, 01/output, brand-vault, 04/references
05-social     -> 04/output, brand-vault, shared
brand-vault   -> (nothing)
shared        -> (nothing)
```

The graph is acyclic.

**Issue 2.1:** The Handoff line in Stage 02's CONTEXT.md pointed forward to `../03-cut-list/input/`. Stage 03 already reads from Stage 02, so this created a two-way reference.
**Fix:** I removed the line. The transcript location stays canonical in Stage 03's Inputs table and in the Stage Handoffs section of CLAUDE.md.

**Issue 2.2:** `brand-vault/` pointed back to the stages that use it. `brand-vault/CONTEXT.md` had a "Used By" column (01, 02, 04, 05) and a pointer to "the Episode header of each guest brief". `sponsor-read.md` said "Used by stage 04". Pattern 3 says the brand vault must not reference any stage.
**Fix:** I dropped the Used By column and the stage pointers. Both files now describe only their own content.

### 3. Placeholder coverage

The scaffold contains 16 placeholders, and each one maps to a question or a derived field:
- SHOW_NAME is Q1, HOST_NAME is Q2, HOST_BIO is Q3, SHOW_FORMAT is Q4, SHOW_AUDIENCE is Q5, SHOW_TAGLINE is Q6 and SHOW_URL is Q7.
- VOICE_EXAMPLE_RIGHT is Q8, with VOICE_PACING derived from it.
- VOICE_EXAMPLE_WRONG is Q9, with VOICE_NOT derived from it.
- VOICE_HARD_CONSTRAINTS is Q10 and SHOW_HASHTAGS is Q11.
- SPONSOR_NAME, SPONSOR_READ_TEXT and SPONSOR_LINK are Q13 to Q15.

The conditionals are covered too: SPONSOR by Q12 and AUDIO_CLIPS by Q16. Every question maps to at least one file. There are no orphaned placeholders and no orphaned questions. No placeholders appear in CLAUDE.md, the top-level CONTEXT.md or the stage CONTEXT.md files.

**Related issue 3.1:** The questionnaire's final scan of the "whole workspace" for `{{` would match the questionnaire itself, which names every placeholder. Onboarding could then never reach zero remaining placeholders.
**Fix:** The agent comment and After Onboarding step 2 now exclude `setup/questionnaire.md` from the scan. This follows placeholder-syntax.md, which says the questionnaire is the source of placeholders, not a target. I also corrected the stale pointer in the per-episode comment, which said "stage 02 Handoff", to Stage 03's Inputs table.

### 4. Conditional section validity

- `sponsor-read.md`: `{{?SPONSOR}}` wraps the whole `## Sponsor` section to the end of the file. Valid.
- `show-notes-format.md`: `{{?SPONSOR}}` wraps the whole `## Sponsor` section, and the block ends before `## About the Guest`. Valid.
- `cut-categories.md`: `{{?AUDIO_CLIPS}}` wraps the whole `## Clip Candidates` section. Valid.
- `ffmpeg-setup.md`: `{{?AUDIO_CLIPS}}` wraps two complete sections, `## Install` and `## Clip Command`. Valid.

There are no inline conditionals.

### 5. Stage handoff chain

| Stage | Output location | Read by |
|-------|-----------------|---------|
| 01 | `01-research/output/[episode-slug]-guest-brief.md` | 02 and 04 (paths match) |
| 02 | `02-outline/output/[episode-slug]-interview-outline.md` | 03 (path matches) |
| 03 | `03-cut-list/output/[episode-slug]-cut-list.md` | 04 (path matches) |
| 04 | `04-show-notes/output/[episode-slug]-show-notes.md` | 05 (path matches) |
| 05 | `05-social/output/[episode-slug]-social-posts.md` | Final deliverable |

Recording is an outside step between stages 02 and 03, covered by Stage 03's `input/` folder. The chain is unbroken.

### 6. CONTEXT.md purity

- **Issue 6.1:** Stage 02 had a prose Handoff paragraph after Outputs. It was removed under fix 2.1.
- **Issue 6.2:** Stage 03 step 4 restated the definition of a tangent, which already lives in `cut-categories.md`. It also had a trailing prose paragraph after Outputs.
  **Fix:** Step 4 now points to `cut-categories.md`. The paragraph is now a one-line note.
- **Issue 6.3:** Stage 04 step 1 restated the timestamp formula, which already lives in "Timestamp Math" in `show-notes-format.md`. This broke Pattern 5.
  **Fix:** Step 1 now points to that section.
- **Issue 6.4:** `brand-vault/CONTEXT.md` described per-episode data rules. This was fixed under 2.2.

All the other CONTEXT.md files contain only a title, a description, Inputs, Process, Checkpoints, Audit and Outputs.

### 7. Checkpoints in creative stages

| Stage | Type | Checkpoint |
|-------|------|------------|
| 01 Research | Writing | After step 6 (step 7 marks the pause) |
| 02 Outline | Writing | After step 3 (step 4 marks the pause; required every episode, as the user asked) |
| 03 Cut list | Linear marking | None, which is allowed |
| 04 Show notes | Writing | After step 6 (step 7 marks the pause) |
| 05 Social | Writing | After step 4 (step 5 marks the pause) |

All the step numbers are valid. Every stage uses the same pattern: the table names the last work step, and the next step is the labeled pause.

### 8. Audits in creative/build stages

Stages 01, 02, 04 and 05 each have an Audit table, and Stage 03 also has one. In every stage the last process step is "Run the audit and save", so the audit runs after the work and before output is written. The pass conditions are concrete: counts, verbatim matching, timestamp ranges and the named limits in the reference files. Pass.

### 9. Contract purity in spec stages

There is no specification stage. Not applicable.

### 10. Line count

All the CONTEXT.md files are under 80 lines. The longest is Stage 04, at about 55 lines. All the reference files are under 200 lines. Pass.

### 11. Naming conventions

All folder and file names are lowercase-with-hyphens. The stage folders are `01-` to `05-`. Every empty output/ folder has a `.gitkeep`, and so do Stage 03's `input/` and Stage 05's `references/`. Pass.

### 12. Tool prerequisites

There is no `prerequisites/` folder. Following Pattern 7, the setup guides live in the references/ folder of the stage that uses each tool, `stages/03-cut-list/references/`. Q16 asks whether the optional tool (ffmpeg) is needed and removes its sections if it is not. Descript is the only required tool, and the After Onboarding step 4 reminder points to its guide.

- **Issue 12.1:** `descript-setup.md` had no one-sentence description, no install steps and no way to check the install.
  **Fix:** I added "What It Is" and "Install and Verify" sections.
- **Issue 12.2:** `ffmpeg-setup.md` had no one-sentence description of the tool or of how the workspace uses it.
  **Fix:** I added both, outside the conditional block, so they stay in the file when clips are off.

### 13. Quality scan

- No em dashes were found. Arrows (`->`) in the folder maps are plain ASCII.
- "Episode slug" is defined in `brief-format.md`. Tool names are explained in the setup guides.
- The markdown tables and code fences are well formed.

Pass.

## Re-run After Fixes

I re-ran checks 1, 2, 3, 6 and 12 against the corrected files:
- **Check 1:** `setup/questionnaire.md` now exists with real content.
- **Check 2:** The graph above has no back edges, and brand-vault has no outgoing references.
- **Check 3:** The scan scope excludes the questionnaire, so a complete onboarding reaches zero `{{` matches.
- **Check 6:** No rule text is duplicated in a CONTEXT.md.
- **Check 12:** Both guides now have a description, install steps and a verification step.

All five checks pass.

## Files Changed

| File | Change |
|------|--------|
| `podcast-episode-pipeline/setup/questionnaire.md` | Installed from stage 04; fixed the scan scope and the stale pointer; dropped the build notes |
| `podcast-episode-pipeline/brand-vault/CONTEXT.md` | Removed the back-references to stages |
| `podcast-episode-pipeline/brand-vault/sponsor-read.md` | Removed the stage reference from the intro |
| `podcast-episode-pipeline/stages/02-outline/CONTEXT.md` | Removed the forward Handoff line |
| `podcast-episode-pipeline/stages/03-cut-list/CONTEXT.md` | Step 4 points to cut-categories; trimmed the trailing prose |
| `podcast-episode-pipeline/stages/04-show-notes/CONTEXT.md` | Step 1 points to Timestamp Math instead of restating it |
| `podcast-episode-pipeline/stages/03-cut-list/references/descript-setup.md` | Added a description and install/verify steps |
| `podcast-episode-pipeline/stages/03-cut-list/references/ffmpeg-setup.md` | Added a description and how the workspace uses it |

## Assumptions

- **No live user:** I applied the fixes directly instead of asking for approval. Each fix is the smallest change that makes its check pass.
- **Write location:** I could only write to this stage's output folder, so the corrected files are copies to place over the scaffold.
- **Stage 04 build notes:** The questionnaire's Audit and Assumptions sections are treated as builder notes and were not shipped in `setup/questionnaire.md`.
- **Checkpoint numbering:** "After step N, then step N+1 is the labeled pause" is treated as valid, because the step numbers exist and the pattern is used the same way in all four stages.
- **Pattern 13 (value framework):** Stages 02 and 03 left it out on purpose. It is not part of the 13 checks, so I note it here and do not count it as a failure.
- **Descript install details:** These are kept general (download from the official site, sign in, open a project), because no tool documentation was available.
</file>

<file path="podcast-episode-pipeline/setup/questionnaire.md">
# Onboarding Questionnaire: Podcast Episode Pipeline

<!-- Agent instructions: Read this file when the user types "setup". Show ALL questions below
     in one message. The user answers in one reply and can skip any question. A skipped
     question takes its default. Replace each placeholder in the listed files by string
     substitution. Fill derived fields without asking. Apply the conditional logic. Then run
     the voice review pass in "After Onboarding". Last, scan the workspace (every file except
     this questionnaire) for any remaining {{ patterns and ask about any that remain. -->

<!-- Per-episode values are NOT asked here: guest name, topic, recording date, whether this
     episode has a sponsor, and the Descript transcript. Stage 01 collects guest, topic,
     date and sponsor yes/no at the start of each run (see stages/01-research/CONTEXT.md).
     The transcript goes into stages/03-cut-list/input/ (see the Inputs table in
     stages/03-cut-list/CONTEXT.md). -->

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
2. **Placeholder scan.** Scan every file in the workspace except this questionnaire for any remaining `{{` patterns, including conditional markers. If any remain, ask for the missing information. Onboarding is complete only when none remain.
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

The show's standing sponsor read, used only for episodes marked as sponsored. If the section below has been removed, the show has no sponsors.

{{?SPONSOR}}

## Sponsor

- Name: {{SPONSOR_NAME}}
- Link or promo code: {{SPONSOR_LINK}}

Read text (use exactly, do not rewrite):

{{SPONSOR_READ_TEXT}}

{{/SPONSOR}}
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

Linear stage: no checkpoint. The user may edit the output file before stage 04.
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

1. Read the cut list and compute the edited timeline using "Timestamp Math" in `show-notes-format.md`.
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

<file path="podcast-episode-pipeline/stages/03-cut-list/references/descript-setup.md">
# Descript Setup

Descript runs outside the agent. This guide only covers installing it and getting a usable transcript out of it.

## What It Is
Descript is an audio and video editor that transcribes recordings and lets you edit them like a text document.

## Install and Verify
1. Download Descript from its official website (Windows or macOS) and install it.
2. Sign in with your Descript account.
3. Verify: open Descript, create a project, drop in a short audio file and confirm a transcript appears.

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

ffmpeg is a free command-line tool for cutting and converting audio and video files. This workspace uses it only to cut short audio clips from the raw recording at the timestamps in the cut list. If the sections below have been removed, audio clips are off and stage 03 skips clip candidates.

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