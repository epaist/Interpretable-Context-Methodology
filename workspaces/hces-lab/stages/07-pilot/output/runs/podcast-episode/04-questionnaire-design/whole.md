<file path="questionnaire.md">
# Onboarding Questionnaire: Podcast Episode Pipeline

<!-- Agent instructions: Read this file when the user types "setup". Show ALL questions below
     in one message. The user answers in one reply and can skip any question. A skipped
     question takes its default. Replace each placeholder in the listed files by string
     substitution. Fill derived fields without asking. Apply the conditional logic. Then run
     the voice review pass in "After Onboarding". Last, scan the whole workspace for any
     remaining {{ patterns and ask about any that remain. -->

<!-- Per-episode values are NOT asked here: guest name, topic, recording date, whether this
     episode has a sponsor, and the Descript transcript. Stage 01 collects guest, topic,
     date and sponsor yes/no at the start of each run (see stages/01-research/CONTEXT.md,
     Process step 1, and the Episode header in references/brief-format.md). The transcript
     goes into stages/03-cut-list/input/ (see stages/02-outline/CONTEXT.md Handoff). -->

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

1. **Voice review (second pass).** Before saving the files, show the user the finished `brand-vault/voice-rules.md`. This includes the derived Pacing section, the derived "What the Voice Is NOT" list, the numbered hard constraints with any rules added from Q9, and the tagline if it was derived. Ask: "Does this match your show? Change anything that is off." Apply the edits, then save. This catches misreadings of the examples.
2. **Placeholder scan.** Scan the whole workspace for any remaining `{{` patterns, including conditional markers. If any remain, ask for the missing information. Onboarding is complete only when none remain.
3. **Tell the user what was set up:** the show identity, voice rules, hashtags, the sponsor section (on or off) and audio clips (on or off).
4. **Descript check.** Remind the user to export transcripts with timestamps and speaker labels on (see `stages/03-cut-list/references/descript-setup.md`). Also remind them to confirm the timestamp format against their first export in `references/descript-export-format.md`.
5. **Where to start.** "To start an episode, go to `stages/01-research/CONTEXT.md` and give the guest name, topic, recording date and whether this episode has a sponsor."

## Audit (stage 04)

| Check | Result |
|-------|--------|
| Placeholder coverage | Pass. All 16 placeholders found in the scaffold are covered. SHOW_NAME (Q1), HOST_NAME (Q2), HOST_BIO (Q3), SHOW_FORMAT (Q4), SHOW_AUDIENCE (Q5), SHOW_TAGLINE (Q6), SHOW_URL (Q7), VOICE_EXAMPLE_RIGHT (Q8), VOICE_EXAMPLE_WRONG (Q9) and VOICE_HARD_CONSTRAINTS (Q10) each have a question. VOICE_PACING is derived under Q8 and VOICE_NOT under Q9. SHOW_HASHTAGS is Q11 and SPONSOR_NAME, SPONSOR_READ_TEXT and SPONSOR_LINK are Q13 to Q15. The SPONSOR conditional is handled by Q12 and AUDIO_CLIPS by Q16. |
| Per-run separation | Pass. Guest, topic, recording date, per-episode sponsor yes/no and the transcript are not asked here. Stage 01 and the stage 03 input collect them. |
| Flat structure | Pass. There is one numbered list, Q1 to Q16, with no category groupings. |
| Defaults present | Pass. Every question has a default or example. Q1 and Q2 have no usable default and are marked required, with examples. |

## Assumptions

- **No live user:** The questions and defaults are based only on the workflow description and the upstream outputs.
- **Placeholder list:** It was built from the scaffold notes table and a check of the scaffold files. No placeholders appear in CLAUDE.md, CONTEXT.md or stage CONTEXT.md files.
- **Sponsor details are system-level:** The discovery stage treats the sponsor name, read text and link as onboarding values. The per-episode decision is only yes or no, collected at stage 01. If sponsors change often, the user edits `brand-vault/sponsor-read.md` directly. Running a new setup is not needed.
- **Voice fields are derived:** VOICE_PACING and VOICE_NOT are derived from the examples, following Rule 7, so the user does not describe the voice in abstract terms. Because these fields are derived, a second review pass (step 9) is included.
- **Derived defaults:** The tagline, host bio and hashtags fall back to values built from other answers.
- **Audio clips default to "no"**, because the user said ffmpeg is optional. The sponsor section defaults to "yes", because the user said only some episodes have no sponsor.
- **Descript** needs no placeholder. It is covered by a reminder after onboarding.
</file>