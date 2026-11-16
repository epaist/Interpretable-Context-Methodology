<file path="validation-report.md">
# Validation Report: Community Grant Application Workspace

Stage 05 output. Validated `community-grants/` from stage 03 against `_core/CONVENTIONS.md` and `_core/placeholder-syntax.md`. The questionnaire from stage 04 was also checked.

**Result: all 13 checks pass after fixes.** Eight issues were found and fixed. The fixed files are in `fixes/community-grants/` in this output folder. Each one replaces the file at the same path in the scaffold. The questionnaire is installed at `fixes/community-grants/setup/questionnaire.md`.

## Summary

| # | Check | First Run | After Fixes |
|---|-------|-----------|-------------|
| 1 | Cross-reference integrity | FAIL (1 issue) | PASS |
| 2 | No circular dependencies | FAIL (2 back-references) | PASS |
| 3 | Placeholder coverage | FAIL (scan conflict, 1 stray pattern) | PASS |
| 4 | Conditional section validity | PASS | PASS |
| 5 | Stage handoff chain | PASS (with note) | PASS |
| 6 | CONTEXT.md purity | PASS | PASS |
| 7 | Checkpoints in creative stages | FAIL (04, 05, 06) | PASS |
| 8 | Audits in creative/build stages | PASS (2 gaps fixed) | PASS |
| 9 | Contract purity in spec stages | N/A | N/A |
| 10 | Line count | PASS | PASS |
| 11 | Naming conventions | PASS | PASS |
| 12 | Tool prerequisites | FAIL (2 issues) | PASS |
| 13 | Quality scan | FAIL (2 issues) | PASS |

## Check Details

### 1. Cross-reference integrity: PASS after fix

Every path in the stage Inputs tables resolves to a real file:

- `references/checklist-format.md`
- `references/narrative-section-guide.md`
- `references/budget-guide.md`
- `references/outcome-guide.md`
- `references/libreoffice-setup.md`
- `../../shared/organization-profile.md`
- `../../shared/voice-rules.md`
- every `../0N-*/output/[slug]-*.md`, which matches the producing stage's Outputs table

**Issue:** `CLAUDE.md` routes `setup` to `setup/questionnaire.md`, but the scaffold holds only `setup/.gitkeep`.

**Fix:** Installed the stage 04 questionnaire at `setup/questionnaire.md`. The `setup/.gitkeep` can be deleted because the folder is no longer empty.

### 2. No circular dependencies: PASS after fixes

Dependency graph, where each stage points to what it reads:

```
01 -> (call text only)
02 -> 01, shared
03 -> 01, 02, shared
04 -> 01, 03
05 -> 01, 03, 04, shared
06 -> 01, 03, shared
07 -> 01, 03, 04, 05, 06 (optional), shared
shared -> (nothing)
```

All edges point to earlier stages or to `shared/`, so the graph is acyclic. Two text back-references broke Pattern 3:

- **Issue:** `shared/CONTEXT.md` had a "Read By" column that named stages 02, 03, 05, 06 and 07. Under Pattern 3 a shared folder must not reference stages.
  - **Fix:** Removed the column.
- **Issue:** The `06-support-letter/CONTEXT.md` description said "stage 07 does not expect its output". This is a forward reference to a later stage.
  - **Fix:** Removed the clause. Stage 07 already handles this through its "Previous stage (optional)" Inputs row.

### 3. Placeholder coverage: PASS after fixes

| Placeholder | File | Question |
|-------------|------|----------|
| `{{ORG_NAME}}` | shared/organization-profile.md | Q1 |
| `{{ORG_LEGAL_STATUS}}` | shared/organization-profile.md | Q2 |
| `{{ANNUAL_OPERATING_BUDGET}}` | shared/organization-profile.md | Q3 |
| `{{MISSION_STATEMENT}}` | shared/organization-profile.md | Q4 |
| `{{SERVICE_AREA}}` | shared/organization-profile.md | Q5 |
| `{{PAST_GRANTS}}` | shared/organization-profile.md | Q6 |
| `{{BOARD_CHAIR_NAME}}` | shared/organization-profile.md | Q7 |
| `{{BOARD_CHAIR_TITLE}}` | shared/organization-profile.md | Q7 |
| `{{READING_LEVEL}}` | shared/voice-rules.md | Q8, Q9 |
| `{{JARGON_LIST}}` | shared/voice-rules.md | Q8, Q9 |

No placeholders are orphaned, and every question maps to a placeholder. No placeholders appear in `CLAUDE.md`, the top-level `CONTEXT.md` or any stage `CONTEXT.md`.

- **Issue:** The questionnaire tells the agent to scan "the whole workspace" for `{{` after onboarding. Once the questionnaire sits in `setup/`, that scan would always find the questionnaire's own placeholder names, so onboarding could never complete.
  - **Fix:** The agent comment and closing line now exclude `setup/questionnaire.md` from the scan.
- **Issue:** The questionnaire's Assumptions section contained the pattern `{{?SUPPORT_LETTER_STAGE}}`. No such block exists in the workspace.
  - **Fix:** The stage 04 Assumptions and Audit sections are design notes, not onboarding content, so they were left out of the installed copy. They remain in the stage 04 output.

### 4. Conditional section validity: PASS

The workspace has no `{{?SECTION}}` blocks. Optional stage 06 is a run-time skip driven by the checklist flag, which is a valid design: the need varies by funder, not by group.

### 5. Stage handoff chain: PASS (with note)

```
01 checklist      -> 02, 03, 04, 05, 06, 07
02 eligibility    -> 03 (verdict line)
03 narrative      -> 04, 05, 06, 07 (approval line)
04 budget         -> 05, 07
05 evaluation     -> 07
06 letters (opt.) -> 07 (only if requested)
```

Every output path matches the Inputs path of the stage that reads it, including the `[slug]` prefix.

**Note:** Stage 06 does not read stage 05. This is correct: 06 is an optional side branch, and stage 07 reads both 05 and 06 directly. The chain has no gap.

The stop gates are consistent:

- 02 writes `Verdict: QUALIFIES`, and 03 stops otherwise.
- 03 writes `Approval: APPROVED`, and 04, 05 and 06 stop otherwise.

### 6. CONTEXT.md purity: PASS

Stage CONTEXT.md files hold only the allowed parts: title, description, Inputs, Process, Checkpoints, Audit and Outputs. All definitions, formats and rules live in reference files.

The top-level `CONTEXT.md` has a short "Per-Run Inputs" list. This is routing information (what to paste at run time), not reference content.

### 7. Checkpoints in creative stages: PASS after fixes

| Stage | Type | Checkpoint | Valid Step Ref |
|-------|------|-----------|----------------|
| 01 | Extract | After 4 | Yes |
| 02 | Decision gate | After 3 | Yes |
| 03 | Writing | After 2, after 5 | Yes |
| 04 | Build (budget) | **None, added: after 5** | Yes |
| 05 | Writing | **None, added: after 4** | Yes |
| 06 | Writing | **None, added: after 4** | Yes |
| 07 | Validate/render | After 3 | Yes |

- **Issue:** Stages 04, 05 and 06 produce content for the group (costs, targets and partner letters) but had no checkpoint.
- **Fix:** Added one checkpoint to each stage, so the group can confirm real costs, realistic targets and accurate partner roles.
  - The narrative remains the only formal approval gate, as the user required.
  - The new checkpoints are confirmations only.

### 8. Audits in creative/build stages: PASS after fixes

Every stage has an Audit table with unambiguous pass conditions, and each audit runs before the save.

Stage 07 is a special case. Its export audit rows (Export, No early export) must run after the export, because they check the exported files. The compliance report is written at step 3, before export, and the export only happens once all items pass. This is accepted.

- **Gap:** Stages 05 and 06 load `voice-rules.md` but did not audit against it.
  - **Fix:** Added a "Plain language" row to both audits, matching stage 03.

### 9. Contract purity in spec stages: N/A

The workspace has no specification stage. The requirements checklist only records funder rules.

### 10. Line count: PASS

All CONTEXT.md files are under 80 lines; the largest is stage 07 at about 60. All reference files are under 200 lines; the largest is `libreoffice-setup.md` at about 45.

### 11. Naming conventions: PASS

- All names use lowercase-with-hyphens.
- Stage folders use the prefixes 01- through 07-.
- Every empty `output/` folder and every empty `references/` folder has a `.gitkeep`.
- Artifacts follow the pattern `[slug]-[artifact].md`.

### 12. Tool prerequisites: PASS after fixes

There is no `prerequisites/` folder. LibreOffice, the only system tool, has its guide in the references folder of the stage that uses it (`07-compliance/references/`), as Pattern 7 requires. The guide has install steps for 3 systems and a verification command (`soffice --version`).

- **Issue:** The guide did not say what LibreOffice is, and did not explain "headless".
  - **Fix:** Added a one-sentence description and a plain explanation of headless mode.
- **Issue:** The questionnaire's Assumptions section said LibreOffice is "mentioned as a setup note", but the After Onboarding text never mentioned it.
  - **Fix:** Added a LibreOffice note that points to the setup guide.

LibreOffice is required, not optional, so no yes/no tool question is needed.

### 13. Quality scan: PASS after fixes

No em dashes were found. Arrows are written as `->`.

- **Issue:** In the questionnaire, the questions used `###` headings directly under `#`, which skips a heading level.
  - **Fix:** Changed them to `##`.
- **Issue:** The term "headless" was used without explanation.
  - **Fix:** Explained it in the guide (see check 12).

## Fixes Applied

| File | Change |
|------|--------|
| `setup/questionnaire.md` | Installed from stage 04. Headings set to `##`. Questionnaire excluded from the `{{` scan. LibreOffice note added. Design-note sections left out. |
| `shared/CONTEXT.md` | Removed the "Read By" column (back-reference to stages) |
| `stages/04-budget/CONTEXT.md` | Added a checkpoint after step 5 |
| `stages/05-evaluation/CONTEXT.md` | Added a checkpoint after step 4 and a Plain language audit row |
| `stages/06-support-letter/CONTEXT.md` | Removed the forward reference to 07. Added a checkpoint after step 4 and a Plain language audit row |
| `stages/07-compliance/references/libreoffice-setup.md` | Added a one-sentence description of the tool and an explanation of "headless" |

Re-run results: checks 1, 2, 3, 7, 8, 12 and 13 were run again on the fixed files, and all pass.

## Assumptions

- **Where fixes are written.** This stage can only write to its own output folder. The fixed files are therefore written to `output/fixes/community-grants/`, using the same paths as the scaffold. To ship, copy them over the scaffold.
- **Checkpoints added without asking.** The user named only the narrative approval as a hard gate. The added checkpoints in 04, 05 and 06 are short confirmations that do not block on formal approval. I decided they are worth the small cost, because budgets and partner letters contain facts only the group can confirm.
- **Stage 07 audit order accepted.** Export checks cannot run before export, so stage 07 is not marked as a violation.
- **Unchanged files.** The questionnaire's Assumptions and Audit sections stay in the stage 04 output as the design record. They are not part of the shipped `setup/` file.
</file>

<file path="fixes/community-grants/setup/questionnaire.md">
# Onboarding Questionnaire: Community Grant Application

<!-- Agent instructions: Read this file when the user types "setup". Ask ALL questions
     below in one conversational pass, so the user can answer everything in one message.
     Collect the answers, then replace each placeholder in the files listed for it.
     After all replacements, scan the workspace for remaining {{ patterns, skipping this
     file (setup/questionnaire.md). If any remain, ask for the missing information.
     These answers are permanent. Do not ask them again on later runs.
     Do not ask about the funder, deadline, project, call text, group notes or partner names.
     Stage 01 collects those at the start of each run. -->

Answer as many as you like in one reply. Skip any question to accept its default. You can also paste existing documents, such as a past application or an annual report, and I will pull the answers from them.

## Q1: What is your group's full name, exactly as it should appear on applications?
- Placeholder: `{{ORG_NAME}}`
- Files: `shared/organization-profile.md`
- Type: free text
- Default: none. This is required, because every application names the applicant. Example: "Eastside Neighbors Garden Collective"

## Q2: What is your group's legal status?
- Placeholder: `{{ORG_LEGAL_STATUS}}`
- Files: `shared/organization-profile.md`
- Type: selection
- Options: 501(c)(3) nonprofit; other tax-exempt nonprofit; unincorporated group with a fiscal sponsor (give the sponsor's name); other (describe)
- Default: "501(c)(3) nonprofit". Funders usually check this first, so confirm it if you can.

## Q3: About how much does your group spend in a typical year?
- Placeholder: `{{ANNUAL_OPERATING_BUDGET}}`
- Files: `shared/organization-profile.md`
- Type: free text (a dollar amount and the year it applies to)
- Default: "Under $100,000 (to confirm)". Example: "$42,000 (2024)"

## Q4: What is your mission statement? Paste it word for word.
- Placeholder: `{{MISSION_STATEMENT}}`
- Files: `shared/organization-profile.md`
- Type: free text
- Default: none. If you have no written mission, give one sentence on who you serve and what you do, and I will use that.

## Q5: What area do you serve? Name the neighborhoods, town, county or zip codes.
- Placeholder: `{{SERVICE_AREA}}`
- Files: `shared/organization-profile.md`
- Type: free text
- Default: none. Example: "The Eastside and Riverbend neighborhoods of Springfield (zip codes 01104 and 01105)"

## Q6: What grants has your group received before? For each one, give the funder, the year, the amount and what it paid for.
- Placeholder: `{{PAST_GRANTS}}`
- Files: `shared/organization-profile.md`
- Type: free text (one grant per line)
- Default: "No prior grants". Example: "Springfield Community Foundation, 2023, $8,000, summer youth garden program"

## Q7: Who signs applications for your group? Give the name and the title exactly as they should be printed.
- Placeholders: `{{BOARD_CHAIR_NAME}}`, `{{BOARD_CHAIR_TITLE}}`
- Files: `shared/organization-profile.md`
- Type: free text
- Default for the title: "Board Chair". There is no default for the name. Example: "Maria Lopez, Board Chair"
- Derived field: if you give only a name, the title is set to "Board Chair".

## Q8: Paste 2 or 3 sentences you have written about your work that sound right to you. Then add 1 sentence that sounds too formal or too much like "grant-speak". These can come from a flyer, a newsletter, an email or an old application.
- Placeholders: `{{READING_LEVEL}}`, `{{JARGON_LIST}}`
- Files: `shared/voice-rules.md`
- Type: free text (examples)
- Default: reading level "Grade 8 (plain language)". Default jargon list: "stakeholders, beneficiaries, leverage, synergy, capacity-building, holistic, empower, impactful, utilize, robust, best practices, underserved populations, deliverables, paradigm"
- Derived fields:
  - `{{READING_LEVEL}}`: estimated from the sentences that sound right, rounded to a grade level between 6 and 10. A request in Q9 overrides this estimate.
  - `{{JARGON_LIST}}`: the default list, plus the formal terms in the "sounds wrong" sentence, plus any terms you give in Q9.

## Q9: Are there any words you never want to see in your applications, or any reading level you must hit? (Optional)
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

LibreOffice is needed in the last stage to export your application to PDF and Word. If it is not installed yet, follow `stages/07-compliance/references/libreoffice-setup.md`.

To start an application, go to `stages/01-requirements/CONTEXT.md`. Paste the funder's call for proposals and give a short project slug. Have your group's project notes ready for stage 02. The funder, deadline, project and partner names are collected on every run, never here.

There is no setup question for letters of support. Stage 06 runs only when a funder's call asks for a letter.

After all replacements, I will scan the workspace (except this file) for remaining `{{` patterns. If any remain, I will ask you for the missing information.
</file>

<file path="fixes/community-grants/shared/CONTEXT.md">
# Shared Context

Persistent facts about the group and how it writes. Onboarding (`setup`) fills these files once, and they carry across every run. Shared files read from no stage.

| File | Contains |
|------|----------|
| `organization-profile.md` | Org name, legal status, budget size, mission, service area, past grants, board chair |
| `voice-rules.md` | Plain-language hard constraints, sentence rules, pacing, jargon list |

Update a fact here, not in stage outputs. Each fact has one home.
</file>

<file path="fixes/community-grants/stages/04-budget/CONTEXT.md">
# Stage 04: Budget

Build a line-item budget and justification that cover only the narrative's activities and stay under the funder's cap.

## Inputs

| Source | File/Location | Section/Scope | Why |
|--------|--------------|---------------|-----|
| Previous stage | `../01-requirements/output/[slug]-requirements-checklist.md` | "Budget Limits" section only | Cap, match, disallowed costs |
| Previous stage | `../03-narrative/output/[slug]-project-narrative.md` | Approval line and project description / activities sections | Budget covers only described activities |
| Stage reference | `references/budget-guide.md` | Full file | Cost categories, in-kind, rounding, justification format |
| User (per run) | Group notes | Cost information only | Real costs |

## Process

1. Stop if the narrative header is not APPROVED.
2. List the narrative activities that need funding.
3. Build line items by category, with the requested amount and any in-kind or match.
4. Write a one-to-three sentence justification per line, naming the activity it supports.
5. Total the table and compare it with the cap.
6. **[Checkpoint]** Present the budget table and justifications. The group confirms the costs and in-kind values, and settles any "rate to confirm" item.
7. Run the audit and revise until it passes, then save.

## Checkpoints

| After Step | Agent Presents | Human Decides |
|------------|---------------|---------------|
| 5 | Budget table, totals and cap comparison | Confirm or correct costs, in-kind values and open rates |

## Audit

| Check | Pass Condition |
|-------|---------------|
| Under cap | Requested total is at or under the funder's cap |
| Justified | Every line has a justification |
| Tied to narrative | Every line names a narrative activity |
| Allowed costs | No line matches a disallowed cost |
| Arithmetic | Line items sum to the stated totals |

## Outputs

| Artifact | Location | Format |
|----------|----------|--------|
| Budget | `output/[slug]-budget.md` | Line-item table (Category, Item, Request, In-kind, Activity), totals row, then a Justification section |
</file>

<file path="fixes/community-grants/stages/05-evaluation/CONTEXT.md">
# Stage 05: Evaluation

Write a short evaluation plan with two or three measurable outcomes traced to the narrative goals.

## Inputs

| Source | File/Location | Section/Scope | Why |
|--------|--------------|---------------|-----|
| Previous stage | `../03-narrative/output/[slug]-project-narrative.md` | Approval line and goals / project description sections | Outcomes trace to goals |
| Previous stage | `../04-budget/output/[slug]-budget.md` | Evaluation-related lines only | Match any evaluation costs |
| Previous stage | `../01-requirements/output/[slug]-requirements-checklist.md` | "Evaluation" and "Sections and Limits" sections | Funder evaluation rules and word limit |
| Shared context | `../../shared/voice-rules.md` | Full file | Plain language |
| Stage reference | `references/outcome-guide.md` | Full file | Indicator, target, timeframe, data source pattern |

## Process

1. Stop if the narrative header is not APPROVED.
2. Pick 2 or 3 narrative goals that can be measured.
3. Write one outcome per goal using the outcome pattern.
4. Note how data is collected and any cost, matching budget lines.
5. **[Checkpoint]** Present the outcome table. The group confirms that each target is realistic and each data source is something volunteers can collect.
6. Run the audit and revise until it passes, then save.

## Checkpoints

| After Step | Agent Presents | Human Decides |
|------------|---------------|---------------|
| 4 | Outcome table with data collection notes | Confirm or adjust targets and data sources |

## Audit

| Check | Pass Condition |
|-------|---------------|
| Outcome count | 2 or 3 outcomes |
| Measurable | Each outcome has a numeric target, a timeframe and a data source |
| Traceable | Each outcome names the narrative goal it measures |
| Word limit | Plan is within the checklist limit, if one is stated |
| Plain language | No term from the jargon list in voice-rules.md appears |

## Outputs

| Artifact | Location | Format |
|----------|----------|--------|
| Evaluation plan | `output/[slug]-evaluation-plan.md` | Short intro, then an outcome table (Goal, Indicator, Target, Timeframe, Data Source) |
</file>

<file path="fixes/community-grants/stages/06-support-letter/CONTEXT.md">
# Stage 06: Support Letter (optional)

Draft letters of support for partners to sign. This stage runs only when the checklist says "Letter of support requested: yes". Otherwise it is skipped.

## Inputs

| Source | File/Location | Section/Scope | Why |
|--------|--------------|---------------|-----|
| Previous stage | `../01-requirements/output/[slug]-requirements-checklist.md` | "Support Letter" and "Attachments" sections | Whether, how many, and any content rules |
| Previous stage | `../03-narrative/output/[slug]-project-narrative.md` | Approval line and project description section | What partners are supporting |
| Shared context | `../../shared/organization-profile.md` | Organization name only | Name the applicant |
| Shared context | `../../shared/voice-rules.md` | Full file | Plain language |
| User (per run) | Partner names and roles | Full list | Who signs each letter |

## Process

1. Stop if the checklist says no letter is requested, or the narrative is not APPROVED.
2. Collect partner names and their role in the project.
3. Draft one letter per partner, describing their specific role and support.
4. Leave a signature block for each partner.
5. **[Checkpoint]** Present the letters. The user confirms each partner's role and title before the letters go to partners for signing.
6. Run the audit, then save.

## Checkpoints

| After Step | Agent Presents | Human Decides |
|------------|---------------|---------------|
| 4 | All draft letters | Confirm or correct each partner's role, name and title |

## Audit

| Check | Pass Condition |
|-------|---------------|
| Count | One letter per partner, and at least the number the funder requests |
| Specific | Each letter names the project and the partner's concrete role |
| Signature block | Each letter has a partner name and title line |
| Plain language | No term from the jargon list in voice-rules.md appears |

## Outputs

| Artifact | Location | Format |
|----------|----------|--------|
| Support letters | `output/[slug]-support-letters.md` | One heading per partner, letter text, signature block |
</file>

<file path="fixes/community-grants/stages/07-compliance/references/libreoffice-setup.md">
# LibreOffice Setup and Export

LibreOffice is a free office suite, similar to Microsoft Office. Stage 07 uses it to turn the finished application into PDF and Word files. It runs "headless", which means from the command line with no window opening, through the `soffice` command.

## Install

| System | Command |
|--------|---------|
| Windows | `winget install TheDocumentFoundation.LibreOffice`. Then add `C:\Program Files\LibreOffice\program` to PATH. |
| macOS | `brew install --cask libreoffice`. Then use `/Applications/LibreOffice.app/Contents/MacOS/soffice`. |
| Linux (Debian/Ubuntu) | `sudo apt install libreoffice` |

To check the install, run `soffice --version`. It should print a version number.

## Export Steps

LibreOffice does not read Markdown well, so export goes through HTML.

1. Write `[slug]-application.html` from `[slug]-application.md`.
   - Use headings as `<h1>`/`<h2>`, tables as `<table>` and paragraphs as `<p>`.
   - Add a simple style block: 11pt serif font, 1-inch margins.
2. Convert to Word:
   `soffice --headless --convert-to docx:"MS Word 2007 XML" --outdir output output/[slug]-application.html`
3. Convert to PDF:
   `soffice --headless --convert-to pdf:writer_web_pdf_Export --outdir output output/[slug]-application.html`
4. Delete the temporary .html file once both exports exist.

## Verify

- Both files exist in `output/` and are larger than 0 bytes.
- Reopen the .docx headless as a check, by converting it back to PDF in a temp folder. It must convert without errors.
- Spot-check that the section order, the budget table and the signature block (board chair name and title) survived the export.

## Troubleshooting

- **The command returns at once and creates no file:** close any open LibreOffice window, or add `-env:UserInstallation=file:///tmp/lo-profile`.
- **Tables lose their borders:** add `border="1"` to `<table>` in the HTML.
</file>