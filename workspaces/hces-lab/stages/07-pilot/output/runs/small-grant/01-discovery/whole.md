<file path="workflow-map.md">
# Workflow Map: Community Grant Application

## Purpose

This workspace takes a local foundation's call for proposals and produces a submission-ready grant application for a small community group. Grants in scope are 5,000 to 50,000 dollars.

- **Starts with:** the funder's call for proposals, pasted in as text from a PDF or web page, plus the group's own project notes.
- **Ends with:** a compliance-checked application exported to PDF and Word.

Each run has a new funder, a new deadline and a new project. Organization details persist across runs.

## Stage Overview

```
01-requirements --> 02-eligibility --> 03-narrative --> 04-budget --> 05-evaluation --> [06-support-letter] --> 07-compliance
                    (stop gate)        (approval gate)                                  (optional)
```

## Stages

### 01-requirements: Call to Requirements Checklist

- **Responsibility:** Pull the funder's requirements out of the call and turn them into one checklist.
- **Inputs:**
  - The call for proposals text (user, per run).
- **Process focus:** Extract the following items:
  - eligibility rules
  - deadline
  - budget limits (cap, match, disallowed costs)
  - required sections
  - word or character limits
  - scoring criteria and weights
  - required attachments
  - whether a letter of support is requested
- **Reference needs:** a checklist format doc that defines the fields and how to mark items "not stated in call".
- **Output:** `output/requirements-checklist.md`
- **Human edit surface:** The user can correct any requirement the agent misread.

### 02-eligibility: Eligibility Check (stop gate)

- **Responsibility:** Compare the group against each eligibility rule and give a verdict.
- **Inputs:**
  - Requirements checklist from 01, eligibility section only.
  - Organization profile (shared context).
  - Group notes (user, per run).
- **Process focus:**
  - Mark each rule as met, not met, or unclear.
  - The verdict is one of: QUALIFIES, DOES NOT QUALIFY, or NEEDS CONFIRMATION.
  - If the verdict is DOES NOT QUALIFY, the pipeline stops here.
- **Checkpoint:** The human confirms the verdict, and resolves any "unclear" items, before the run continues.
- **Output:** `output/eligibility-report.md`

### 03-narrative: Project Narrative (approval gate)

- **Responsibility:** Draft the project narrative section by section in plain language, with each section matched to the scoring criteria.
- **Inputs:**
  - Requirements checklist from 01, covering required sections, word limits and scoring criteria.
  - Eligibility report from 02, verdict only.
  - Organization profile.
  - Group notes.
- **Reference needs:**
  - plain-language writing rules
  - a narrative section guide that maps typical sections (need, project description, organizational capacity, sustainability) to criteria
- **Checkpoints:**
  - After outlining: the agent shows which criterion each section answers, and the human confirms.
  - After drafting: the group must approve the full narrative. No later stage runs until the narrative is approved.
- **Audit:**
  - Every required section is present.
  - Every section is within its word limit.
  - Every scoring criterion is addressed by at least one section.
  - No jargon list violations.
- **Output:** `output/project-narrative.md`, with an approval status line in its header.

### 04-budget: Line-Item Budget and Justification

- **Responsibility:** Build a line-item budget and a budget justification that stay under the funder's cap.
- **Inputs:**
  - Requirements checklist from 01, budget limits only.
  - The approved narrative from 03, so that the budget covers only the activities it describes.
  - Group notes, for costs.
- **Reference needs:** budget format and justification guide covering cost categories, in-kind contributions and rounding.
- **Audit:**
  - The total is at or under the cap.
  - Every line has a justification.
  - Every line ties to a narrative activity.
  - No disallowed costs.
  - The arithmetic sums correctly.
- **Output:** `output/budget.md`, containing the line-item table and the justification.

### 05-evaluation: Evaluation Plan

- **Responsibility:** Write a short evaluation plan with two or three measurable outcomes.
- **Inputs:**
  - The approved narrative from 03.
  - The budget from 04, for any evaluation costs.
  - Requirements checklist from 01, for evaluation requirements and word limits.
- **Reference needs:** an outcome-writing guide, giving the measurable outcome pattern of indicator, target, timeframe and data source.
- **Audit:**
  - The plan has 2 to 3 outcomes.
  - Each outcome has a numeric target, a timeframe and a data source.
  - Each outcome traces to a narrative goal.
- **Output:** `output/evaluation-plan.md`

### 06-support-letter (optional): Letter of Support Draft

- **Responsibility:** Draft letter(s) of support for partners to sign.
- **Runs only when:** the requirements checklist says the funder asks for a letter of support.
- **Inputs:**
  - Requirements checklist from 01.
  - Approved narrative from 03.
  - Partner names (user, per run).
- **Output:** `output/support-letters.md`

### 07-compliance: Final Compliance Pass and Export

- **Responsibility:** Assemble the application and check it against the checklist.
- **Process focus:**
  - Check every required section, word limit and attachment.
  - Confirm the deadline and the signature block (board chair).
  - Export to PDF and Word through LibreOffice.
- **Inputs:**
  - Full requirements checklist from 01.
  - Outputs of stages 03, 04 and 05, plus 06 if it ran.
  - Organization profile, for the signatory.
- **Audit:**
  - Every checklist item is marked pass.
  - Any failures are listed with a fix, and no export happens until they are resolved.
- **Outputs:**
  - `output/compliance-report.md`
  - `output/application.md`
  - `output/application.pdf`
  - `output/application.docx`

## Shared Context (persistent, cross-stage)

- **Organization profile:** `shared/organization-profile.md`
  - Contents: organization name, mission statement, service area, past grants, board chair.
  - Used by stages 02, 03 and 07.
- **Plain-language voice rules:** `shared/voice-rules.md`
  - Used by stages 03, 05 and 06.

Stage-specific references live in each stage's own `references/` folder:
- checklist format (01)
- narrative section guide (03)
- budget guide (04)
- outcome guide (05)
- LibreOffice export guide (07)

## Per-Run Inputs (Layer 4, not placeholders)

- Call for proposals text.
- Group notes for this project.
- Partner names, only when a letter of support is required.

The funder, the deadline and the project are extracted from these inputs on each run. They are not set at onboarding.

## User-Specific Variables

| Placeholder | Meaning |
|-------------|---------|
| `{{ORG_NAME}}` | Organization name |
| `{{MISSION_STATEMENT}}` | Mission statement |
| `{{SERVICE_AREA}}` | Geographic area served |
| `{{PAST_GRANTS}}` | Prior grants (funder, year, amount, purpose) |
| `{{BOARD_CHAIR_NAME}}` | Board chair who signs |
| `{{BOARD_CHAIR_TITLE}}` | Signatory title as printed |

## Optional Stages

- **06-support-letter:** This is a run-time condition, triggered when the checklist field "letter of support requested" is yes. Otherwise the stage is skipped and 07 does not expect its output.
- For workspaces that never need letters, the routing entry can be wrapped in `{{?SUPPORT_LETTER_STAGE}}...{{/SUPPORT_LETTER_STAGE}}`.

## Tool Prerequisites

| Tool | Stage | Required? | Purpose |
|------|-------|-----------|---------|
| LibreOffice (headless `soffice`) | 07-compliance | Required for export | Convert assembled application to PDF and .docx |

The setup guide goes in `stages/07-compliance/references/libreoffice-setup.md`.

## Selected Skills

None are bundled at this point. No skill scan or GitHub search could be run in this session. Candidate types to look for later:
- a docx/pdf document skill, which could replace the LibreOffice guide
- a grant-writing skill

## Assumptions

- **Steps 1 to 3 (questions to the user):** Answered from the workflow description. No follow-up was possible.
- **Stage split:** Budget and evaluation are two separate stages because they are distinct artifacts with different audits. The letter of support sits after evaluation and before compliance.
- **Eligibility stop:** Treated as a hard gate with a human confirm checkpoint. "Unclear" items need human resolution before the run continues.
- **Narrative approval:** Modeled as a mandatory checkpoint. The approval is recorded in the narrative file header, and stages 04 to 07 require it.
- **Step 8 (skills):** Skill discovery was skipped because there was no tool access. No skills were selected, and LibreOffice remains a prerequisite.
- **Step 9 (checkpoint):** The draft map was accepted as described.
- **Signatory title placeholder:** Added `{{BOARD_CHAIR_TITLE}}`, since signature blocks usually need it.
- **Funder, deadline and project:** Treated as per-run inputs, not placeholders, because the user said each run has a new one.
- **Audit results:**
  - Stage clarity: pass
  - Input/output chain: pass
  - Shared context: pass
  - Variable coverage: pass
</file>