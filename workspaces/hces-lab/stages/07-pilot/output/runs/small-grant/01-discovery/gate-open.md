<file path="workflow-map.md">
# Workflow Map: Community Grant Application

Goal: turn a local foundation's call for proposals ($5,000 to $50,000 grants) into a submission-ready application for a small community group.

Start: the funder's call (PDF or web page, pasted as text) plus the group's own notes.
End: a compliance-checked application, exported to PDF and Word.

## Stages

### 01-requirements: Call to Requirements Checklist
- **Responsibility:** Pull every funder requirement out of the call.
- **Inputs:** Call for proposals text (user, per run). Group notes are not needed here.
- **References:** Checklist format (what to capture and how to label it).
- **Process:** Extract eligibility rules, deadline, budget limits (cap, match, disallowed costs), required sections, word or character limits per section, scoring criteria with weights, required attachments, and whether a letter of support is requested.
- **Output:** `output/requirements-checklist.md`, a structured checklist. Each item has an ID so later stages can cite it.
- **Human edit surface:** The checklist. User can fix misread limits or add requirements the call stated elsewhere.

### 02-eligibility: Eligibility Gate
- **Responsibility:** Decide whether the group qualifies. Stop the run if it does not.
- **Inputs:** `01-requirements/output/requirements-checklist.md` (eligibility section), group notes (user, per run), organization profile (shared).
- **References:** Eligibility decision rules (pass, fail, unclear and needs a question to the funder).
- **Process:** Compare each eligibility item to the group's facts. Mark pass, fail or unclear with evidence.
- **Checkpoint:** Present the verdict. Human confirms GO or STOP. On STOP, the run ends here.
- **Output:** `output/eligibility-decision.md` with a per-item table and a GO/STOP verdict.

### 03-narrative: Project Narrative
- **Responsibility:** Draft the project narrative section by section, matched to the scoring criteria, in plain language.
- **Inputs:** `01-requirements/output/requirements-checklist.md` (required sections, word limits, scoring criteria), `02-eligibility/output/eligibility-decision.md` (verdict must be GO), group notes, organization profile (shared).
- **References:** Plain-language writing rules (shared), narrative section guide (maps scoring criteria to section content).
- **Process:** Map each scoring criterion to a section, draft one section at a time, and keep each within its word limit.
- **Checkpoints:** (a) After the section outline and criteria map, human confirms structure. (b) After the full draft, **the group must approve the narrative**. No later stage starts without that approval.
- **Audit:** Every scoring criterion is addressed in a named section. Every section is within its word limit. Plain-language check passes. No claims appear that are not in the group notes or profile.
- **Output:** `output/project-narrative.md` with an approval line (approved by, date).

### 04-budget: Budget and Justification
- **Responsibility:** Build a line-item budget and justification under the funder's cap.
- **Inputs:** `01-requirements/output/requirements-checklist.md` (budget limits, disallowed costs), `03-narrative/output/project-narrative.md` (approved activities), group notes (cost figures).
- **References:** Budget format and justification guide.
- **Process:** List line items tied to narrative activities, total them, and write a one-line justification per item.
- **Checkpoint:** Human confirms figures, especially any estimated cost.
- **Audit:** The total is at or below the cap. No disallowed cost categories appear. Every line ties to an activity in the narrative. Any required match is shown.
- **Output:** `output/budget.md` with a line-item table and the justification.

### 05-evaluation: Evaluation Plan
- **Responsibility:** Write a short evaluation plan with two or three measurable outcomes.
- **Inputs:** `03-narrative/output/project-narrative.md`, `04-budget/output/budget.md` (evaluation costs, if any), requirements checklist (evaluation section rules).
- **References:** Outcome-writing guide (measurable, with a baseline, target, method and timing).
- **Audit:** There are 2 to 3 outcomes. Each outcome has a number, a method and a date. Each one ties to a narrative goal.
- **Output:** `output/evaluation-plan.md`.

### 06-support-letter (optional): Letter of Support
- **Responsibility:** Draft a letter of support for a partner to sign.
- **Condition:** Run only when the checklist shows the funder asks for one.
- **Inputs:** Requirements checklist (letter requirements), approved narrative, partner details (user, per run).
- **Output:** `output/support-letter.md`.

### 07-compliance: Compliance Pass and Export
- **Responsibility:** Check the assembled application against the checklist and export it.
- **Inputs:** Requirements checklist (all items), narrative, budget, evaluation plan, support letter (if the stage ran), organization profile (signatory).
- **References:** Compliance checklist procedure, LibreOffice export setup guide.
- **Process:** Assemble the documents in the funder's required order. Check every required section, word limit, attachment, deadline and signature line. Export to PDF and .docx with LibreOffice.
- **Checkpoint:** Present the compliance report. Human fixes or accepts any open items before export.
- **Audit:** Every checklist ID is marked met or flagged. No section exceeds its limit. The budget total matches the narrative. The signatory is {{BOARD_CHAIR_NAME}}.
- **Output:** `output/compliance-report.md`, `output/application.pdf`, `output/application.docx`.

## Input/Output Chain
call text -> 01 checklist -> 02 GO/STOP -> 03 approved narrative -> 04 budget -> 05 evaluation -> (06 letter) -> 07 report and exports. Every stage input is either provided by the user or produced by an earlier stage.

## Shared Context (Layer 3, used across stages)
- **organization-profile.md:** name, mission, service area, past grants, signatory. Used by stages 02, 03, 06 and 07.
- **plain-language-rules.md:** Used by stages 03, 05 and 06.
- **Requirements checklist:** Per-run, not shared. It is a stage 01 output that many later stages read.

## User-Specific Variables (set once per group)
- `{{ORG_NAME}}`
- `{{MISSION_STATEMENT}}`
- `{{SERVICE_AREA}}`
- `{{PAST_GRANTS}}` (list: funder, year, amount, purpose)
- `{{BOARD_CHAIR_NAME}}` (signatory)

## Per-Run Inputs (not placeholders)
These change on every run, so they are supplied as stage inputs rather than set at onboarding:
- Funder name
- Call text
- Deadline
- Project idea and group notes
- Partner details for the letter

## Optional Stages
- **06-support-letter:** Wrapped in `{{?SUPPORT_LETTER}}...{{/SUPPORT_LETTER}}` in the workspace routing. It is triggered per run by the checklist, so the folder is kept and the stage is skipped when the funder does not request a letter.

## Tool Prerequisites
| Tool | Stage | Required? | Purpose |
|------|-------|-----------|---------|
| LibreOffice (headless `soffice --convert-to`) | 07-compliance | Required for export | Convert the assembled document to PDF and .docx |

Setup guide goes in `stages/07-compliance/references/libreoffice-setup.md`.

## Selected Skills
None selected. Skill discovery could not be run, so no local scan or GitHub search was done. A docx or pdf skill could later replace the LibreOffice guide if one is found.

## Assumptions
- **Step 1 (describe the workflow):** I used the user's written description as the full answer. No follow-up questions were asked.
- **Stage breakdown:** I split the work at the user's natural handoffs. Budget and evaluation are separate stages because they produce different artifacts and need different audits.
- **Funder questions:** Extracting requirements and the eligibility check are separate stages, so the eligibility gate can stop the run cleanly. "Unclear" eligibility items are surfaced for the human to resolve, for example by asking the funder.
- **Narrative approval:** The group's approval of the narrative is a hard checkpoint. Its approval line gates stages 04 and later.
- **Export placement:** LibreOffice export is placed in the compliance stage, since export follows the final pass.
- **Step 8 (skills):** No skill search was possible. I recorded "none" and noted a possible future replacement.
- **Step 9 (checkpoint):** I treated the draft map as approved as written, since the description covered stages, inputs, outputs, variables, the optional step and the tool.
- **Per-run versus per-group details:** Funder, deadline and project are per-run inputs, not placeholders, because the user said they change every run.
</file>