<file path="questionnaire.md">
# Onboarding Questionnaire: Community Grant Application

<!-- Agent instructions: Read this file when the user types "setup". Ask ALL questions below in one conversational pass, so the user can answer everything in a single message. Collect the answers and replace each placeholder in the listed files. Fill derived fields without asking. Then run the two-pass review described under "After Onboarding". After all replacements, scan the entire workspace for remaining {{ patterns. If any remain, ask only for the missing information. Onboarding is complete when zero placeholders remain. -->

<!-- Per-run details are NOT asked here. Stage 01 collects the call for proposals text and the project slug at the start of each run. The funder, the deadline and the project come from the call. Stages 02 and 03 collect the group notes. Stage 06 collects partner names only when a letter of support is requested. -->

### Q1: What is your group's full legal name, exactly as it should appear on applications?
- Placeholder: `{{ORG_NAME}}`
- Files: `shared/organization-profile.md`
- Type: free text
- Default: none. This is required, because it appears on every application.
- Example: "Eastside Neighbors Food Collective"

### Q2: What is your group's legal status?
- Placeholder: `{{ORG_LEGAL_STATUS}}`
- Files: `shared/organization-profile.md`
- Type: selection, with an optional free-text detail
- Options:
  - 501(c)(3) nonprofit
  - fiscally sponsored project (name the sponsor)
  - unincorporated community group
  - other (describe)
- Default: "Unincorporated community group"
- Example: "Fiscally sponsored project of Riverside Community Foundation"

### Q3: About how much does your group spend in a typical year, all costs included?
- Placeholder: `{{ANNUAL_OPERATING_BUDGET}}`
- Files: `shared/organization-profile.md`
- Type: free text (a dollar amount, plus the year it describes)
- Default: "Under $50,000 (to confirm)"
- Example: "$38,000 (2024)"

### Q4: Paste your mission statement as you normally write it.
- Placeholder: `{{MISSION_STATEMENT}}`
- Files: `shared/organization-profile.md`
- Type: free text, 1 to 3 sentences
- Default: none. If you do not have one, give a sentence on who you serve and how, and the agent will use that.
- Example: "We make sure every family in the Eastside has fresh food on the table, run by neighbors for neighbors."

### Q5: Which area do you serve? Name the neighborhoods, town, county or ZIP codes.
- Placeholder: `{{SERVICE_AREA}}`
- Files: `shared/organization-profile.md`
- Type: free text
- Default: none. Funders check this for eligibility.
- Example: "Eastside and Millbrook neighborhoods of Springfield, Hamlin County (ZIPs 01104, 01109)"

### Q6: List any grants you have received before, one per line, as: funder, year, amount, purpose.
- Placeholder: `{{PAST_GRANTS}}`
- Files: `shared/organization-profile.md`
- Type: free text (list)
- Default: "No prior grants."
- Example: "Hamlin Community Fund, 2023, $7,500, summer produce stand"

### Q7: Who is your board chair, the person who signs applications, and what title should print under their name?
- Placeholders: `{{BOARD_CHAIR_NAME}}`, `{{BOARD_CHAIR_TITLE}}`
- Files: `shared/organization-profile.md`
- Type: free text (name; title)
- Default for the title: "Board Chair"
- Example: "Maria Lopez; Chair, Board of Directors"
- Derived field: if only a name is given, `{{BOARD_CHAIR_TITLE}}` is set to "Board Chair".

### Q8: How plain should your writing be? Paste 2 or 3 sentences you have written that sound right for a funder.
- Placeholder: `{{READING_LEVEL}}`
- Files: `shared/voice-rules.md`
- Type: free text (example sentences); you may also name a grade level
- Default: "Grade 8 (general public)"
- Example: "We run a free produce stand every Saturday. Last summer, 140 families came at least once. Most walked from home."
- Derived field: the agent estimates a grade level from the sample sentences and writes it as the target, for example "Grade 7-8, matching sample sentences". If the user names a grade, that grade is used.

### Q9: Which words or phrases should never appear in your applications? List them, or paste a sentence that sounds wrong to you.
- Placeholder: `{{JARGON_LIST}}`
- Files: `shared/voice-rules.md`
- Type: free text (list or example sentences)
- Default list, used if skipped:
  - leverage
  - synergy
  - capacity-building
  - stakeholders
  - beneficiaries
  - underserved populations
  - holistic
  - impactful
  - utilize
  - robust
  - best practices
  - paradigm
- Example of a wrong sentence: "We will leverage synergies to deliver holistic, impactful programming to underserved stakeholders."
- Derived field: the agent pulls each jargon term out of any "sounds wrong" sentence and adds it to the list, then adds the default terms the user did not reject.

---

## After Onboarding

**Two-pass review.** Before the voice rules are saved as final:
1. Show the user the filled `shared/voice-rules.md`. This covers the reading level derived from Q8 and the jargon list derived from Q9.
2. Show the filled board chair title from Q7.
3. Ask the user to confirm or correct these.

The narrative audit rejects any jargon-list term, so a misread list would block real drafts.

**What was configured:**
- `shared/organization-profile.md` holds:
  - name, legal status and budget
  - mission and service area
  - past grants
  - signatory
- `shared/voice-rules.md` holds the reading level and the jargon list.

**Where to start.** For each new application, open `stages/01-requirements/CONTEXT.md`, paste the funder's call for proposals and give a project slug.

The following are asked at run time, not here:
- the funder, the deadline and the project, which come from the call;
- the group notes;
- partner names, only when the call requests letters of support.

**Optional stage.** No setup question is needed. Stage 06 (letters of support) runs or is skipped on each run, based on the checklist's "Letter of support requested" field.

**Final check.** After all replacements, scan the entire workspace for remaining `{{` patterns. If any remain, ask for the missing information.

---

## Assumptions

**Inputs and buckets**
- **Variable source:** All 10 placeholders were taken from the scaffold report's placeholder table. Every one appears only in `shared/organization-profile.md` or `shared/voice-rules.md`. The 6 discovery variables are a subset of these 10.
- **Bucket split:**
  - All 10 placeholders are system-level, because they describe the group and persist across runs.
  - Funder, deadline, project, call text, group notes and partner names are per-run. They are already collected by stage 01, stages 02 and 03, and stage 06 respectively, so they have no questions here.

**Fields added at scaffolding**
- **Extra fields kept:** `{{ORG_LEGAL_STATUS}}` and `{{ANNUAL_OPERATING_BUDGET}}` were added at scaffolding. They were kept because eligibility checks usually need them. Each has a skippable default ("to confirm") rather than being dropped.

**Question design**
- **Combined question:** The board chair name and title are asked in one question (Q7). The title is derived as "Board Chair" when it is not given.
- **Voice questions:** These follow Rule 7. Q8 asks for sample sentences, and Q9 accepts "sounds wrong" sentences.
- **Two-pass review:** Added because Q8 and Q9 produce derived fields.

**Optional stage**
- **No yes/no question for stage 06:** I followed the scaffold decision. Whether letters are needed varies by funder, not by group, and the `{{?SUPPORT_LETTER_STAGE}}` wrapper would sit in routing files where placeholders are not allowed.

**User interaction**
- **No user interaction:** All choices were made from the workflow description and the upstream outputs.

**Audit**

| Check | Result |
|-------|--------|
| Placeholder coverage | PASS. All 10 placeholders are mapped (Q1 to Q9). |
| Per-run separation | PASS |
| Flat structure | PASS. A single numbered list. |
| Defaults present | PASS. Every question has a default or an example. Q1, Q4 and Q5 have no skippable default because their values are required, but each shows an example. |
</file>