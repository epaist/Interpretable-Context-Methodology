<file path="stage-contracts.md">
# Stage Contracts: Community Grant Application

Formal Inputs / Process / Outputs contracts for every stage of the community grant workspace. Source: `../01-discovery/output/workflow-map.md`. Rules: `_core/CONVENTIONS.md`, Pattern 1 (Stage Contracts) and Pattern 3 (One-Way Cross-References).

Paths are written from inside each stage folder. `../../shared/` is the workspace-level shared folder.

---

## Dependency Diagram

```
 Per-run inputs (user):  call text | group notes | partner names
 Shared (Layer 3):       shared/organization-profile.md   shared/voice-rules.md

 call text
    |
    v
 [01-requirements] ---------------------------------------------------+
    | requirements-checklist.md                                        |
    |------------------+---------------+-------------+-----------+      |
    v                  |               |             |           |      |
 [02-eligibility]      |               |             |           |      |
    | eligibility-report.md (STOP if DOES NOT QUALIFY)               |      |
    v                  v               |             |           |      |
 [03-narrative] <------+               |             |           |      |
    | project-narrative.md (APPROVED required)                     |      |
    |------------------+---------------|-------------+           |      |
    v                  v               v             v           |      |
 [04-budget] <-----------------------(checklist)    |           |      |
    | budget.md                                      |           |      |
    v                                                |           |      |
 [05-evaluation] <---- narrative + checklist         |           |      |
    | evaluation-plan.md                             |           |      |
    v                                                v           |      |
 [06-support-letter] (optional: only if checklist says requested)  |      |
    | support-letters.md                                           |      |
    v                                                              v      v
 [07-compliance] <-- checklist (full), 03, 04, 05, [06], org profile
    | compliance-report.md, application.md, application.pdf, application.docx
    v
 FINAL DELIVERABLE
```

Edge list (reader <- source). Every edge points backward to a lower-numbered stage or to `shared/`:

| Reader | Reads from |
|--------|-----------|
| 01 | user call text |
| 02 | 01, shared/organization-profile, group notes |
| 03 | 01, 02, shared/organization-profile, shared/voice-rules, group notes |
| 04 | 01, 03, group notes |
| 05 | 01, 03, 04, shared/voice-rules |
| 06 | 01, 03, shared/organization-profile, shared/voice-rules, partner names |
| 07 | 01, 03, 04, 05, 06 (if present), shared/organization-profile |

No stage reads from a higher-numbered stage. `shared/` reads from no stage. The graph is acyclic.

---

## Stage 01-requirements: Call to Requirements Checklist

### Inputs

| Source | File/Location | Section/Scope | Why |
|--------|--------------|---------------|-----|
| User (per run) | Call for proposals text, pasted at run start | Full text | The funder's rules to extract |
| Stage reference | `references/checklist-format.md` | Full file | Field list and how to mark "not stated in call" |

### Process

1. Ask the user to paste the call for proposals text and give a short project slug.
2. Extract: funder name, deadline, eligibility rules, budget limits (cap, match, disallowed costs), required sections, word or character limits, scoring criteria and weights, required attachments, evaluation requirements, and whether a letter of support is requested.
3. Mark any field the call does not cover as "not stated in call".
4. Write the checklist using the format in `references/checklist-format.md`.
5. **[Checkpoint]** Show the checklist; the user corrects any misread item.
6. Run the audit, then save.

### Checkpoints

| After Step | Agent Presents | Human Decides |
|------------|---------------|---------------|
| 4 | Draft requirements checklist | Corrections to any misread requirement |

### Audit

| Check | Pass Condition |
|-------|---------------|
| Field coverage | Every field in the checklist format has a value or "not stated in call" |
| Source fidelity | Every limit, date and amount appears in the call text as written |
| Support letter flag | "Letter of support requested" is explicitly yes or no |

### Outputs

| Artifact | Location | Format |
|----------|----------|--------|
| Requirements checklist | `output/[slug]-requirements-checklist.md` | Markdown checklist with one section per field group (Eligibility, Deadline, Budget Limits, Sections and Limits, Scoring, Attachments, Evaluation, Support Letter) |

---

## Stage 02-eligibility: Eligibility Check (stop gate)

### Inputs

| Source | File/Location | Section/Scope | Why |
|--------|--------------|---------------|-----|
| Previous stage | `../01-requirements/output/[slug]-requirements-checklist.md` | "Eligibility" section only | Rules to check |
| Shared context | `../../shared/organization-profile.md` | Full file | Facts about the group |
| User (per run) | Group notes | Full text | Project-specific facts relevant to eligibility |

### Process

1. Read each eligibility rule.
2. Mark each rule met, not met, or unclear, with the supporting fact from the profile or notes.
3. Give one verdict: QUALIFIES, DOES NOT QUALIFY, or NEEDS CONFIRMATION.
4. **[Checkpoint]** Present the rule table and verdict; the human resolves every unclear item and confirms the verdict.
5. Update the verdict after the human resolves the unclear items. If the verdict is DOES NOT QUALIFY, save the report and stop the run.
6. Run the audit, then save.

### Checkpoints

| After Step | Agent Presents | Human Decides |
|------------|---------------|---------------|
| 3 | Rule-by-rule table and draft verdict | Resolution of unclear items; confirm or change verdict |

### Audit

| Check | Pass Condition |
|-------|---------------|
| Rule coverage | Every eligibility rule in the checklist has a row |
| Evidence | Every met or not-met row cites a fact from the profile or notes |
| Final verdict | Verdict is QUALIFIES or DOES NOT QUALIFY; no unclear items remain |

### Outputs

| Artifact | Location | Format |
|----------|----------|--------|
| Eligibility report | `output/[slug]-eligibility-report.md` | Verdict line at top, then a table: Rule, Status, Evidence |

---

## Stage 03-narrative: Project Narrative (approval gate)

### Inputs

| Source | File/Location | Section/Scope | Why |
|--------|--------------|---------------|-----|
| Previous stage | `../01-requirements/output/[slug]-requirements-checklist.md` | "Sections and Limits" and "Scoring" sections | What to write and how it is scored |
| Previous stage | `../02-eligibility/output/[slug]-eligibility-report.md` | Verdict line only | Confirm the run may continue |
| Shared context | `../../shared/organization-profile.md` | Full file | Mission, service area, capacity, past grants |
| Shared context | `../../shared/voice-rules.md` | Full file | Plain-language rules and jargon list |
| Stage reference | `references/narrative-section-guide.md` | Full file | Typical sections and criterion mapping |
| User (per run) | Group notes | Full text | Project facts |

### Process

1. Stop if the eligibility verdict is not QUALIFIES.
2. Outline the narrative: one entry per required section, naming the scoring criteria each one answers and its word limit.
3. **[Checkpoint]** Present the outline and criterion map; the human confirms or changes it.
4. Draft each section in plain language, within its word limit.
5. Run the audit and revise until it passes.
6. **[Checkpoint]** Present the full narrative; the group approves or requests changes. Repeat steps 4 to 6 until approved.
7. Save with the header line `Approval: APPROVED by [name], [date]`.

### Checkpoints

| After Step | Agent Presents | Human Decides |
|------------|---------------|---------------|
| 2 | Section outline with criterion map | Confirm the sections and criterion coverage |
| 5 | Full draft narrative with word counts | Approve, or list changes |

### Audit

| Check | Pass Condition |
|-------|---------------|
| Required sections | Every required section in the checklist is present |
| Word limits | Every section is at or under its limit |
| Criterion coverage | Every scoring criterion is addressed by at least one section |
| Plain language | No term from the jargon list in voice-rules.md appears |

### Outputs

| Artifact | Location | Format |
|----------|----------|--------|
| Project narrative | `output/[slug]-project-narrative.md` | Header with approval status line, then one heading per required section with word count noted |

---

## Stage 04-budget: Line-Item Budget and Justification

### Inputs

| Source | File/Location | Section/Scope | Why |
|--------|--------------|---------------|-----|
| Previous stage | `../01-requirements/output/[slug]-requirements-checklist.md` | "Budget Limits" section only | Cap, match, disallowed costs |
| Previous stage | `../03-narrative/output/[slug]-project-narrative.md` | Approval line and project description / activities sections | Budget covers only described activities |
| Stage reference | `references/budget-guide.md` | Full file | Cost categories, in-kind, rounding, justification format |
| User (per run) | Group notes | Cost information only | Real costs |

### Process

1. Stop if the narrative header is not APPROVED.
2. List the narrative activities that need funding.
3. Build line items by category, with the requested amount and any in-kind or match.
4. Write a one-to-three sentence justification per line naming the activity it supports.
5. Total the table and compare it with the cap.
6. Run the audit and revise until it passes.

### Audit

| Check | Pass Condition |
|-------|---------------|
| Under cap | Requested total is at or under the funder's cap |
| Justified | Every line has a justification |
| Tied to narrative | Every line names a narrative activity |
| Allowed costs | No line matches a disallowed cost |
| Arithmetic | Line items sum to the stated totals |

### Outputs

| Artifact | Location | Format |
|----------|----------|--------|
| Budget | `output/[slug]-budget.md` | Line-item table (Category, Item, Request, In-kind, Activity), totals row, then a Justification section |

---

## Stage 05-evaluation: Evaluation Plan

### Inputs

| Source | File/Location | Section/Scope | Why |
|--------|--------------|---------------|-----|
| Previous stage | `../03-narrative/output/[slug]-project-narrative.md` | Approval line and goals / project description sections | Outcomes trace to goals |
| Previous stage | `../04-budget/output/[slug]-budget.md` | Evaluation-related lines only | Match any evaluation costs |
| Previous stage | `../01-requirements/output/[slug]-requirements-checklist.md` | "Evaluation" and "Sections and Limits" sections | Funder evaluation rules and word limit |
| Shared context | `../../shared/voice-rules.md` | Full file | Plain language |
| Stage reference | `references/outcome-guide.md` | Full file | Indicator, target, timeframe, data source pattern |

### Process

1. Stop if the narrative header is not APPROVED.
2. Pick 2 or 3 narrative goals that can be measured.
3. Write one outcome per goal using the outcome pattern.
4. Note how data is collected and any cost, matching budget lines.
5. Run the audit and revise until it passes.

### Audit

| Check | Pass Condition |
|-------|---------------|
| Outcome count | 2 or 3 outcomes |
| Measurable | Each outcome has a numeric target, a timeframe and a data source |
| Traceable | Each outcome names the narrative goal it measures |
| Word limit | Plan is within the checklist limit, if one is stated |

### Outputs

| Artifact | Location | Format |
|----------|----------|--------|
| Evaluation plan | `output/[slug]-evaluation-plan.md` | Short intro, then an outcome table (Goal, Indicator, Target, Timeframe, Data Source) |

---

## Stage 06-support-letter (optional): Letter of Support Draft

Runs only when the checklist field "Letter of support requested" is yes. Otherwise skipped, and 07 does not expect its output.

### Inputs

| Source | File/Location | Section/Scope | Why |
|--------|--------------|---------------|-----|
| Previous stage | `../01-requirements/output/[slug]-requirements-checklist.md` | "Support Letter" and "Attachments" sections | Whether, how many, and any content rules |
| Previous stage | `../03-narrative/output/[slug]-project-narrative.md` | Approval line and project description section | What partners are supporting |
| Shared context | `../../shared/organization-profile.md` | Organization name only | Name the applicant |
| Shared context | `../../shared/voice-rules.md` | Full file | Plain language |
| User (per run) | Partner names and roles | Full list | Who signs each letter |

### Process

1. Stop if the checklist says no letter is requested, or the narrative is not APPROVED.
2. Collect partner names and their role in the project.
3. Draft one letter per partner, describing their specific role and support.
4. Leave a signature block for each partner.
5. Run the audit, then save.

### Audit

| Check | Pass Condition |
|-------|---------------|
| Count | One letter per partner, and at least the number the funder requests |
| Specific | Each letter names the project and the partner's concrete role |
| Signature block | Each letter has a partner name and title line |

### Outputs

| Artifact | Location | Format |
|----------|----------|--------|
| Support letters | `output/[slug]-support-letters.md` | One heading per partner, letter text, signature block |

---

## Stage 07-compliance: Final Compliance Pass and Export

### Inputs

| Source | File/Location | Section/Scope | Why |
|--------|--------------|---------------|-----|
| Previous stage | `../01-requirements/output/[slug]-requirements-checklist.md` | Full file | Every item to check |
| Previous stage | `../03-narrative/output/[slug]-project-narrative.md` | Full file | Assemble and check |
| Previous stage | `../04-budget/output/[slug]-budget.md` | Full file | Assemble and check |
| Previous stage | `../05-evaluation/output/[slug]-evaluation-plan.md` | Full file | Assemble and check |
| Previous stage (optional) | `../06-support-letter/output/[slug]-support-letters.md` | Full file, only if the checklist says a letter is requested | Assemble and check |
| Shared context | `../../shared/organization-profile.md` | Organization name and board chair fields | Cover and signature block |
| Stage reference | `references/libreoffice-setup.md` | Full file | Export commands and verification |

### Process

1. Assemble the application in the funder's required section order, with a signature block for `{{BOARD_CHAIR_NAME}}`, `{{BOARD_CHAIR_TITLE}}`.
2. Check every checklist item: sections present, word limits, budget cap, attachments, support letters (if required), deadline not passed.
3. Write the compliance report with pass or fail per item and a fix for each failure.
4. **[Checkpoint]** If any item fails, present the failures; the human fixes upstream files or approves fixes, then repeat from step 1.
5. Once all items pass, export `application.md` to PDF and .docx with LibreOffice.
6. Run the audit.

### Checkpoints

| After Step | Agent Presents | Human Decides |
|------------|---------------|---------------|
| 3 | Compliance report | Fix failures, or confirm all pass and approve export |

### Audit

| Check | Pass Condition |
|-------|---------------|
| All items pass | Every checklist item is marked pass |
| No early export | No PDF or .docx exists while any item fails |
| Signature | Board chair name and title appear in the signature block |
| Deadline | Deadline is stated in the report and is not past |
| Export | PDF and .docx exist and open |

### Outputs

| Artifact | Location | Format |
|----------|----------|--------|
| Compliance report | `output/[slug]-compliance-report.md` | Table: Checklist Item, Status, Fix |
| Application | `output/[slug]-application.md` | Assembled application in required section order |
| Application PDF | `output/[slug]-application.pdf` | LibreOffice export |
| Application Word | `output/[slug]-application.docx` | LibreOffice export |

---

## Canonical Sources

| Information | One Home | Readers |
|-------------|----------|---------|
| Funder requirements (eligibility, deadline, cap, sections, limits, criteria, attachments, letter flag) | `01-requirements/output/[slug]-requirements-checklist.md` | 02, 03, 04, 05, 06, 07 |
| Eligibility verdict | `02-eligibility/output/[slug]-eligibility-report.md` | 03 |
| Approval status and narrative goals and activities | `03-narrative/output/[slug]-project-narrative.md` (header line) | 04, 05, 06, 07 |
| Budget figures | `04-budget/output/[slug]-budget.md` | 05, 07 |
| Outcomes | `05-evaluation/output/[slug]-evaluation-plan.md` | 07 |
| Org name, mission, service area, past grants, board chair | `shared/organization-profile.md` | 02, 03, 06, 07 |
| Plain-language rules and jargon list | `shared/voice-rules.md` | 03, 05, 06 |
| Checklist field definitions | `01-requirements/references/checklist-format.md` | 01 |
| Narrative section-to-criterion guide | `03-narrative/references/narrative-section-guide.md` | 03 |
| Budget categories, in-kind, rounding | `04-budget/references/budget-guide.md` | 04 |
| Outcome pattern | `05-evaluation/references/outcome-guide.md` | 05 |
| LibreOffice install and export | `07-compliance/references/libreoffice-setup.md` | 07 |

The "letter of support requested" flag lives only in the checklist. Stage 07 reads it there; it does not decide again on its own.

---

## Output Consumption

| Stage | Output | Consumed By |
|-------|--------|-------------|
| 01 | requirements-checklist | 02, 03, 04, 05, 06, 07 |
| 02 | eligibility-report | 03 (verdict gate) |
| 03 | project-narrative | 04, 05, 06, 07 |
| 04 | budget | 05, 07 |
| 05 | evaluation-plan | 07 |
| 06 | support-letters | 07 (when present) |
| 07 | compliance report, application md/pdf/docx | Final deliverable |

---

## Audit Results

| Check | Result | Notes |
|-------|--------|-------|
| No circular references | PASS | All edges point to lower-numbered stages or `shared/`; shared files reference no stage |
| Output consumption | PASS | Every output is read downstream; 07 is the final deliverable |
| Contract completeness | PASS | All seven stages have filled Inputs, Process and Outputs tables |
| Canonical sources | PASS | Each fact has one home (table above); approval status lives only in the narrative header |

---

## Assumptions

- **Step 7 checkpoint (flow review):** No user was available. Following the workflow description, the dependency flow and contracts were accepted as drafted.
- **Artifact names:** Discovery used plain names (e.g. `requirements-checklist.md`). To follow the naming convention `[topic-slug]-[artifact-type].md`, a per-run project slug is asked for in stage 01 and used as a prefix. Example: `food-pantry-2025-budget.md`.
- **Eligibility in stage 03:** Discovery said 03 reads the verdict only. That is kept. Stages 04 to 07 do not reread eligibility, because the narrative only exists if the verdict passed.
- **Approval gate enforcement:** Stages 04, 05, 06 and 07 each check the narrative's approval line instead of copying it, so the approval stays in one place.
- **Evaluation reads the budget:** This follows discovery. The edge 05 to 04 still points backward, so it creates no cycle.
- **Stage 06 reads organization profile (name only):** Discovery did not list this. It was added because a support letter must name the applicant. It is a backward pointer to `shared/`, so it creates no cycle.
- **Stage 06 reads voice rules:** Discovery listed voice rules as used by 06, so it was added to 06's Inputs.
- **Stage 07 checkpoint added:** Discovery said failures block export. This is modeled as a human checkpoint, because fixes may need edits to upstream outputs that the user owns.
- **Deadline check:** Stage 07 checks that the deadline has not passed, using the date of the run.
- **Checkpoint numbering:** Checkpoint rows name the step after which the human decides. This matches the convention table shape.
- **Optional stage:** 06 is a run-time skip driven by the checklist flag. The `{{?SUPPORT_LETTER_STAGE}}` wrapper from discovery is left for scaffolding to decide.
</file>