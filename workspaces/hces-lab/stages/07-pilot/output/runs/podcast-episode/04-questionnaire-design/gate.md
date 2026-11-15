<file path="questionnaire.md">
# Onboarding Questionnaire: Podcast Episode Pipeline

<!-- Agent instructions: Read this file when the user types "setup". Ask ALL questions
     below in one message. The user answers everything in one reply and may skip any
     question, in which case the default applies. Replace each placeholder in the listed
     files. Apply the conditional logic (Q12, Q15). Run the two-pass voice review before
     finalizing. Then scan the whole workspace for remaining {{ patterns. -->

Answer as many of these as you like in one message. Skip any question and the default is used.

### Q1: What is the name of your podcast?
- Placeholder: `{{SHOW_NAME}}`
- Files: `brand-vault/show-identity.md`
- Type: free text
- Default: none. This one is required. Example: "The Long Game"

### Q2: What is the host's name, as it should appear in the show notes and the intro?
- Placeholder: `{{HOST_NAME}}`
- Files: `brand-vault/show-identity.md`
- Type: free text
- Default: none. This one is required. Example: "Maya Chen"

### Q3: In one or two sentences, who is the host? This is used for the show's "about" lines.
- Placeholder: `{{HOST_BIO}}`
- Files: `brand-vault/show-identity.md`
- Type: free text
- Default: "[Host name] hosts [show name], a weekly interview podcast."

### Q4: How would you describe the show's format?
- Placeholder: `{{SHOW_FORMAT}}`
- Files: `brand-vault/show-identity.md`
- Type: selection, or free text
- Options: Weekly one-guest interview, about 45 to 60 minutes / Weekly one-guest interview, under 30 minutes / Other (describe it)
- Default: "Weekly one-guest interview, about 45 to 60 minutes"

### Q5: Does the show have a tagline or one-line pitch?
- Placeholder: `{{SHOW_TAGLINE}}`
- Files: `brand-vault/show-identity.md`
- Type: free text
- Default: Derived from Q4 and Q7. Example: "Weekly conversations with people building things that last."

### Q6: What is the show's website or main listening link?
- Placeholder: `{{SHOW_URL}}`
- Files: `brand-vault/show-identity.md`
- Type: free text (URL)
- Default: "No website yet". In this case, posts and notes use "link in bio" or the platform link.

### Q7: Who listens to the show? Describe the typical listener in one or two sentences.
- Placeholder: `{{SHOW_AUDIENCE}}`
- Files: `brand-vault/show-identity.md`
- Type: free text
- Default: "Curious professionals who want practical ideas from people doing the work."

### Q8: Which hashtags should always be available for the show's social posts?
- Placeholder: `{{SHOW_HASHTAGS}}`
- Files: `shared/platform-specs.md`
- Type: free text (a list)
- Default: Derived from Q1: a hashtag of the show name with no spaces, plus `#podcast` and `#interview`.

### Q9: Paste 2 or 3 sentences that sound exactly like your show. You can use a past episode description, social post or intro line.
- Placeholder: `{{VOICE_EXAMPLE_RIGHT}}`
- Files: `brand-vault/voice-rules.md`
- Type: free text (examples, not a description)
- Default: "Most founders say they hate meetings. Priya Rao cancelled all of hers for a year. Here's what broke, and what didn't."
- Derived field: `{{VOICE_PACING}}` (`brand-vault/voice-rules.md`). The agent infers sentence length, rhythm and use of questions from these examples.

### Q10: Paste 2 or 3 sentences that do NOT sound like your show, such as hype or generic podcast copy you dislike.
- Placeholder: `{{VOICE_EXAMPLE_WRONG}}`
- Files: `brand-vault/voice-rules.md`
- Type: free text (examples)
- Default: "🔥 You WON'T believe this INCREDIBLE conversation!!! Don't miss this game-changing episode, smash that follow button!"
- Derived field: `{{VOICE_NOT}}` (`brand-vault/voice-rules.md`). The agent names the patterns in these examples, for example "not hype, not salesy, no clickbait".

### Q11: Are there hard rules that the show's writing must never break? Examples: "no emoji", "never use 'game-changer'", "always use the guest's first name after the first mention".
- Placeholder: `{{VOICE_HARD_CONSTRAINTS}}`
- Files: `brand-vault/voice-rules.md`
- Type: free text (list)
- Default: Derived from Q9 and Q10, plus these: 1. No exclamation marks. 2. No hype words (incredible, game-changing, must-listen). 3. Quote guests only with their exact words. 4. No more than one emoji per post.

### Q12: Does the show ever have sponsors?
- Type: yes/no
- If NO: Remove the `{{?SPONSOR}}...{{/SPONSOR}}` blocks in `brand-vault/sponsor-read.md` and `stages/04-show-notes/references/show-notes-format.md`. Skip Q13 and Q14.
- If YES: Keep both blocks and answer Q13 and Q14. Whether a given episode has a sponsor is asked at the start of each episode in stage 01. It is not asked here.
- Default: No

### Q13: (Only if Q12 is yes) What is the sponsor's name, and what link or promo code should listeners use?
- Placeholders: `{{SPONSOR_NAME}}`, `{{SPONSOR_LINK}}`
- Files: `brand-vault/sponsor-read.md`
- Type: free text
- Default: none if Q12 is yes. Example: "Acme Notes, acmenotes.com/longgame, code LONGGAME for 20% off"

### Q14: (Only if Q12 is yes) Paste the sponsor read exactly as it should appear in the show notes.
- Placeholder: `{{SPONSOR_READ_TEXT}}`
- Files: `brand-vault/sponsor-read.md`
- Type: free text. The text is used word for word.
- Default: "This episode is supported by [Q13 sponsor name]. Visit [Q13 link] to learn more."

### Q15: Do you want the cut list to suggest short audio clips with ready-made ffmpeg commands? ffmpeg is optional and must be installed separately.
- Type: yes/no
- If NO: Remove the `{{?AUDIO_CLIPS}}...{{/AUDIO_CLIPS}}` blocks in `stages/03-cut-list/references/cut-categories.md` and `stages/03-cut-list/references/ffmpeg-setup.md`.
- If YES: Keep both blocks and point the user to the Install section of `ffmpeg-setup.md`.
- Default: No

---

## Voice Review (second pass)

After filling Q9 to Q11, show the user the completed `brand-vault/voice-rules.md`. This includes the derived Pacing and "What the Voice Is NOT" sections. Ask: "Is this how the show sounds? Correct anything I misread." Apply the corrections, then finalize. Do not skip this step, because the derived fields are interpretations.

## After Onboarding

Tell the user:
- The show identity, voice rules, hashtags, sponsor setup (or its removal) and clip setting are now saved in `brand-vault/`, `shared/` and the stage 03 and 04 references.
- To start an episode, go to `stages/01-research/CONTEXT.md`. That stage asks for the guest name, topic, recording date and whether this episode has a sponsor. These change every episode and are never asked here.
- Before stage 03, export the transcript from Descript using `stages/03-cut-list/references/descript-setup.md`.

After all replacements, scan the entire workspace for remaining `{{` patterns. If any remain, ask for the missing information. Onboarding is complete only when zero placeholders remain.

---

## Assumptions

- **Placeholder scan:** The list was built from the scaffold's markdown files: 16 value placeholders and 2 conditionals (`SPONSOR`, `AUDIO_CLIPS`). Every one maps to Q1 to Q15. The 9 variables in the discovery output are a subset of these.
- **System-level vs per-run:** Guest name, topic, recording date, the per-episode sponsor yes/no and the transcript are per-run inputs. Stage 01 (Process step 1) and stage 03 (input/) already collect them, so none of them appear here.
- **Sponsor details are treated as system-level** because the workflow description lists "sponsor read" among the things that change between users. If sponsors rotate per episode, the user edits `brand-vault/sponsor-read.md` between episodes. Making this a per-run input would need a stage 01 change, so it is flagged for stage 05 validation.
- **Derived fields:** `{{VOICE_PACING}}` is derived from Q9 and `{{VOICE_NOT}}` from Q10. `{{SHOW_TAGLINE}}` and `{{SHOW_HASHTAGS}}` have derived defaults. This follows Rule 4 and Rule 7. Because of the derived voice fields, a two-pass review was added (process step 9).
- **Required fields:** Show name and host name have examples but no usable default, because a wrong default would leak into published copy. All other questions can be skipped.
- **Defaults for optional features:** Sponsors default to No and audio clips default to No. ffmpeg is optional and some shows have no sponsors.
- **Format:** All questions are in one flat numbered list (Q1 to Q15). Q13 and Q14 depend on Q12 but stay in the same list, so the user can answer in one message.
- **No live review:** No user review was possible. The questionnaire is saved after passing the audit: coverage, per-run separation, flat structure and defaults or examples on every question.
</file>