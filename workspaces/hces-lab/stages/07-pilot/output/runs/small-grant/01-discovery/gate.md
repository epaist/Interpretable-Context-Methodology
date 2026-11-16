<file path="workflow-map.md">
# Workflow Map: Community Grant Application Workspace

## Purpose

This workspace turns a local foundation's call for proposals into a submission-ready grant application for a small community group. It covers grants of $5,000 to $50,000. Each run has a new funder, a new deadline and a new project. The group profile carries over from run to run.

**Starts with:** The funder's call for proposals, pasted in as text from a PDF or web page, and the group's own project notes.
**Ends with:** A compliance-checked application, exported to PDF and Word.

---

## Stages

### 01-requirements: Extract funder requirements
- **Responsibility:** Turn the call for proposals into a structured requirements checklist.
- **Inputs:** The call-for-proposals text (user, per run).
- **References:** A checklist format reference that lists the fields to extract.
- **Process:** Extract the following from the call:
  - eligibility rules
  - deadline
  - budget minimum and cap
  - required narrative sections
  - word or character limits for each section
  - scoring criteria and their weights
  - required attachments
  - whether a letter of support is required
  - submission format

  Mark anything ambiguous as "unclear, confirm with funder".
- **Output artifact:** `output/requirements-checklist.md`
- **Human edit surface:** The user can correct or add requirements before continuing.

### 02-eligibility: Eligibility gate
- **Responsibility:** Test the group against each eligibility rule and give a go or no-go result.
- **Inputs:**
  - `01-requirements/output/requirements-checklist.md`
  - Group profile (shared context)
  - The group's project notes (user, per run)
- **Process:**
  1. Compare each rule against the group's facts and record pass, fail or unknown.
  2. If any rule fails, record NO-GO with the reasons and stop the pipeline.
  3. If any rule is unknown, list questions for the user.
- **Checkpoint:** The user confirms GO before drafting begins.
- **Output artifact:** `output/eligibility-decision.md`, containing a GO or NO-GO verdict and a table of each rule against the evidence.

### 03-narrative: Draft the project narrative
- **Responsibility:** Write the narrative section by section, mapped to the scoring criteria, in plain language.
- **Inputs:**
  - Requirements checklist (stage 01)
  - Eligibility decision (stage 02, must be GO)
  - Project notes
  - Group profile
- **References:** Plain-language writing rules, and a narrative section guide covering common grant sections and how to tie each one to a criterion.
- **Process:**
  1. Map each required section to the scoring criteria it serves.
  2. Lock the outline.
  3. Draft each section, staying within its word limit.
- **Checkpoints:**
  - After the outline: the user approves the section-to-criterion mapping.
  - After the full draft: **the group must approve the narrative**. No later stage may run until this approval is recorded.
- **Audit:**
  - Every required section is present.
  - Every scoring criterion is addressed by at least one section.
  - Every section is within its word limit.
  - The text meets the plain-language rules.
- **Output artifact:** `output/narrative.md`, with an approval note at the top showing who approved it and when.

### 04-budget: Line-item budget and justification
- **Responsibility:** Build a line-item budget and a budget justification that stays under the funder's cap.
- **Inputs:**
  - Approved narrative (stage 03)
  - Requirements checklist, for the cap, allowed costs and match rules
  - Project notes
- **References:** A budget format guide covering line categories and the justification style.
- **Audit:**
  - The total is at or below the cap, and at or above the minimum if the funder sets one.
  - Every line has a justification.
  - Every line ties back to an activity in the narrative.
  - All arithmetic is correct.
- **Output artifacts:**
  - `output/budget.md`, containing a line-item table and totals
  - `output/budget-justification.md`

### 05-evaluation: Evaluation plan
- **Responsibility:** Write a short evaluation plan with two or three measurable outcomes.
- **Inputs:**
  - Approved narrative
  - Budget, to confirm that evaluation costs are covered
  - Requirements checklist, for any evaluation section limits
- **References:** An outcome-writing guide. Each outcome needs a measure, a target, a data source and a timeline.
- **Audit:**
  - There are two or three outcomes.
  - Every outcome is measurable, with a number and a date.
  - Every outcome links to a narrative goal.
  - The plan is within its word limit.
- **Output artifact:** `output/evaluation-plan.md`

### 06-support-letter (OPTIONAL): Letter of support
- **Responsibility:** Draft a letter of support for a partner to edit and sign.
- **Condition:** This stage runs only when the requirements checklist says the funder requires or invites a support letter.
- **Inputs:**
  - Requirements checklist
  - Approved narrative
  - Partner details (user, per run)
- **Output artifact:** `output/support-letter-draft.md`

### 07-compliance: Final compliance pass and export
- **Responsibility:** Assemble the application, check it against the checklist, and export it.
- **Inputs:**
  - Requirements checklist
  - Narrative
  - Budget and budget justification
  - Evaluation plan
  - Support letter, if stage 06 ran
  - Group profile, for the signatory block
- **Process:**
  1. Assemble the documents in the funder's required order.
  2. Check every required section, word limit, attachment, the budget cap and the deadline against the checklist.
  3. List any missing attachments for the user to supply. These are things such as a 501(c)(3) letter or financials.
  4. Export the assembled document to PDF and Word with LibreOffice.
- **Audit:** Every checklist item is marked pass, or flagged with the action needed.
- **Output artifacts:**
  - `output/compliance-report.md`
  - `output/application.docx`
  - `output/application.pdf`

---

## Input/Output Chain

```
call text + notes → 01 checklist → 02 GO/NO-GO ─(stop if NO-GO)
   → 03 narrative [group approval] → 04 budget → 05 evaluation
   → (06 support letter, optional) → 07 compliance + export
```

Every stage's inputs come either from the user (the call text, project notes, partner details, the group profile set at setup) or from the output of an earlier stage.

---

## Shared Context (cross-stage, persistent, Layer 3)

- **Group profile** (`shared/group-profile.md`): organization name, mission, service area, past grants and board chair. Stages 02, 03, 06 and 07 use it.
- **Plain-language writing rules** (`shared/voice.md`): stages 03, 05 and 06 use these.

Stage-specific references are kept separate from shared context:

| Stage | Reference |
|-------|-----------|
| 01 | Checklist format |
| 03 | Narrative section guide |
| 04 | Budget format guide |
| 05 | Outcome-writing guide |
| 07 | LibreOffice setup |

## Per-Run Inputs (Layer 4, not placeholders)

These change with every run, so they are supplied as working inputs rather than set at setup:

- Funder name
- Call text
- Deadline
- Project notes
- Partner details

---

## User-Specific Placeholder Variables (set at setup)

| Variable | Meaning |
|----------|---------|
| `{{ORG_NAME}}` | Organization's legal name |
| `{{MISSION_STATEMENT}}` | The group's mission statement |
| `{{SERVICE_AREA}}` | Geographic area served |
| `{{PAST_GRANTS}}` | List of prior grants: funder, year, amount and purpose |
| `{{BOARD_CHAIR_NAME}}` | Board chair who signs the application |
| `{{BOARD_CHAIR_TITLE}}` | Signatory title (defaults to "Board Chair") |

---

## Optional Stages / Conditional Sections

- **`{{?SUPPORT_LETTER_STAGE}}...{{/SUPPORT_LETTER_STAGE}}`** wraps the stage 06 routing entry and the support-letter row in stage 07's inputs. The flag is decided per run from the checklist, not at setup, so the stage folder stays in the workspace.
- **`{{?PAST_GRANTS}}...{{/PAST_GRANTS}}`** wraps the past-grants section of the group profile. It is removed if the group has no prior grants.

---

## Tool Prerequisites

| Tool | Stage | Required? | Purpose |
|------|-------|-----------|---------|
| LibreOffice (headless `soffice --convert-to`) | 07-compliance | Required for export | Convert the assembled application to PDF and .docx |

A setup guide goes in `stages/07-compliance/references/libreoffice-setup.md`.

---

## Selected Skills

None were bundled; see the Assumptions section for why. Candidate for later review: a docx/pdf document skill, if one is installed locally. It could replace the LibreOffice setup guide.

---

## Audit Results

| Check | Result |
|-------|--------|
| Stage clarity | PASS: each of the 7 stages has one responsibility and a named artifact |
| Input/output chain | PASS: all inputs come from the user or an earlier stage |
| Shared context identified | PASS: the group profile and voice rules are listed apart from stage references |
| Variable coverage | PASS: organization name, mission, service area, past grants and board chair are all placeholders; per-run items are treated as inputs |

---

## Assumptions

1. **Step 1 and the checkpoint (steps 9 and 10):** I could not ask the user, so I took the user's description as the full workflow. I treated the draft map as approved, keeping the stage split the user described.
2. **Separate eligibility stage:** I made eligibility its own stage, apart from requirements extraction, because the user wants a hard stop at that point.
3. **Merged compliance and export:** I combined the compliance pass and the LibreOffice export into one final stage instead of splitting export out.
4. **Approval gate:** "The group must approve the narrative" is a blocking checkpoint. Stages 04 to 07 require an approval note in `narrative.md`.
5. **Support-letter stage position:** The optional support-letter stage sits after evaluation and before compliance. Whether it runs is decided per run from the checklist.
6. **Per-run items are not placeholders:** The funder, deadline and project are per-run Layer 4 inputs. I added `BOARD_CHAIR_TITLE` as a small extra placeholder.
7. **Skills (step 8):** I could not scan local skill folders or search GitHub, so no skills were selected. A document-export skill is noted as a candidate.
8. **Attachments:** Attachments the group must supply, such as tax status letters and financials, are only flagged in the compliance report, not generated.
</file>