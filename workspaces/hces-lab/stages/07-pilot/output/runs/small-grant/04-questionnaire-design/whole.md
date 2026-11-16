<file path="questionnaire.md">
# Onboarding Questionnaire: Community Grant Application

<!-- Agent instructions: Read this file when the user types "setup". Ask ALL questions
     below in one conversational pass, so the user can answer everything in one message.
     Collect the answers, then replace each placeholder in the files listed for it.
     After all replacements, scan the whole workspace for remaining {{ patterns.
     If any remain, ask for the missing information.
     These answers are permanent. Do not ask them again on later runs.
     Do not ask about the funder, deadline, project, call text, group notes or partner names.
     Stage 01 collects those at the start of each run. -->

Answer as many as you like in one reply. Skip any question to accept its default. You can also paste existing documents, such as a past application or an annual report, and I will pull the answers from them.

### Q1: What is your group's full name, exactly as it should appear on applications?
- Placeholder: `{{ORG_NAME}}`
- Files: `shared/organization-profile.md`
- Type: free text
- Default: none. This is required, because every application names the applicant. Example: "Eastside Neighbors Garden Collective"

### Q2: What is your group's legal status?
- Placeholder: `{{ORG_LEGAL_STATUS}}`
- Files: `shared/organization-profile.md`
- Type: selection
- Options: 501(c)(3) nonprofit; other tax-exempt nonprofit; unincorporated group with a fiscal sponsor (give the sponsor's name); other (describe)
- Default: "501(c)(3) nonprofit". Funders usually check this first, so confirm it if you can.

### Q3: About how much does your group spend in a typical year?
- Placeholder: `{{ANNUAL_OPERATING_BUDGET}}`
- Files: `shared/organization-profile.md`
- Type: free text (a dollar amount and the year it applies to)
- Default: "Under $100,000 (to confirm)". Example: "$42,000 (2024)"

### Q4: What is your mission statement? Paste it word for word.
- Placeholder: `{{MISSION_STATEMENT}}`
- Files: `shared/organization-profile.md`
- Type: free text
- Default: none. If you have no written mission, give one sentence on who you serve and what you do, and I will use that.

### Q5: What area do you serve? Name the neighborhoods, town, county or zip codes.
- Placeholder: `{{SERVICE_AREA}}`
- Files: `shared/organization-profile.md`
- Type: free text
- Default: none. Example: "The Eastside and Riverbend neighborhoods of Springfield (zip codes 01104 and 01105)"

### Q6: What grants has your group received before? For each one, give the funder, the year, the amount and what it paid for.
- Placeholder: `{{PAST_GRANTS}}`
- Files: `shared/organization-profile.md`
- Type: free text (one grant per line)
- Default: "No prior grants". Example: "Springfield Community Foundation, 2023, $8,000, summer youth garden program"

### Q7: Who signs applications for your group? Give the name and the title exactly as they should be printed.
- Placeholders: `{{BOARD_CHAIR_NAME}}`, `{{BOARD_CHAIR_TITLE}}`
- Files: `shared/organization-profile.md`
- Type: free text
- Default for the title: "Board Chair". There is no default for the name. Example: "Maria Lopez, Board Chair"
- Derived field: if you give only a name, the title is set to "Board Chair".

### Q8: Paste 2 or 3 sentences you have written about your work that sound right to you. Then add 1 sentence that sounds too formal or too much like "grant-speak". These can come from a flyer, a newsletter, an email or an old application.
- Placeholders: `{{READING_LEVEL}}`, `{{JARGON_LIST}}`
- Files: `shared/voice-rules.md`
- Type: free text (examples)
- Default: reading level "Grade 8 (plain language)". Default jargon list: "stakeholders, beneficiaries, leverage, synergy, capacity-building, holistic, empower, impactful, utilize, robust, best practices, underserved populations, deliverables, paradigm"
- Derived fields:
  - `{{READING_LEVEL}}`: estimated from the sentences that sound right, rounded to a grade level between 6 and 10. A request in Q9 overrides this estimate.
  - `{{JARGON_LIST}}`: the default list, plus the formal terms in the "sounds wrong" sentence, plus any terms you give in Q9.

### Q9: Are there any words you never want to see in your applications, or any reading level you must hit? (Optional)
- Placeholders: `{{JARGON_LIST}}` (adds to the list), `{{READING_LEVEL}}` (overrides the estimate)
- Files: `shared/voice-rules.md`
- Type: free text
- Default: none. The list and reading level derived from Q8 are used.

---

## Two-Pass Review (voice rules)

The reading level and jargon list are derived from your examples, so they need one check. After filling in `shared/voice-rules.md`, I will show you the reading level I chose and the full jargon list. You can then add terms, remove terms or change the level. I save the file only after you confirm it, or after you say "looks fine".

## After Onboarding

I will tell you what was configured:

- `shared/organization-profile.md` now holds your name, legal status, budget, mission, service area, past grants and signer.
- `shared/voice-rules.md` now holds your reading level and jargon list.

To start an application, go to `stages/01-requirements/CONTEXT.md`. Paste the funder's call for proposals and give a short project slug. Have your group's project notes ready for stage 02. The funder, deadline, project and partner names are collected on every run, never here.

There is no setup question for letters of support. Stage 06 runs only when a funder's call asks for a letter.

After all replacements, I will scan the entire workspace for remaining `{{` patterns. If any remain, I will ask you for the missing information.

---

## Assumptions

- **No user interaction was possible.** Defaults and examples were set from the workflow description. Name, mission, service area and signer name have no real default, because inventing them would violate the voice rule "do not invent facts". Each of those questions gives an example and is marked required.
- **Placeholder list.** The list comes from the scaffold report and a scan of the scaffold files. All 10 placeholders live in `shared/organization-profile.md` or `shared/voice-rules.md`. All are system-level.
- **Per-run variables excluded.** The following are not in the questionnaire:
  - funder, deadline and project;
  - call text, group notes and partner names;
  - project slug.

  Stages 01, 02 and 06 already collect these at run time.
- **Extra profile fields kept.** `{{ORG_LEGAL_STATUS}}` and `{{ANNUAL_OPERATING_BUDGET}}` were kept as Q2 and Q3 rather than dropped. The user gave no instruction to decline them, and eligibility checks need them.
- **Signer merged into one question.** The board chair name and title share Q7, and the title is derived when it is left out.
- **Voice questions use examples.** Reading level and jargon list come from example sentences (template Rule 7). They are derived fields, with Q9 as an optional override. Because they are derived, a two-pass review step was added.
- **No yes/no question for stage 06.** Whether a letter is needed varies by funder, not by group. Following the scaffold decision, no `{{?SUPPORT_LETTER_STAGE}}` wrapper exists, and stage 06 stays a run-time skip.
- **No LibreOffice question.** LibreOffice is a tool prerequisite, documented in `stages/07-compliance/references/libreoffice-setup.md`. It has no placeholder, so it is only mentioned as a setup note.

## Audit

| Check | Result |
|-------|--------|
| Placeholder coverage | PASS. All 10 placeholders map to Q1 to Q9. |
| Per-run separation | PASS. No funder, deadline, project or partner questions are included. |
| Flat structure | PASS. Q1 to Q9 form a single numbered list. |
| Defaults present | PASS. Every question has a default or an example. |
</file>