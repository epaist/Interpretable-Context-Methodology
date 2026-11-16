<file path="stage-contracts.md">
# Stage Contracts: Community Grant Application

This document formalizes the seven stages from `01-discovery/output/workflow-map.md` as Inputs/Process/Outputs contracts (Pattern 1). It also verifies that every cross-reference points one way only (Pattern 3).

---

## Dependency Diagram

```
                 [per-run: call text]      [per-run: group notes]      [per-run: partner names]
                         |                    |   |   |                          |
                         v                    |   |   |                          |
                  01-requirements             |   |   |                          |
                   (checklist)                |   |   |                          |
                         |                    |   |   |                          |
     +--------+----------+-------+------+     |   |   |                          |
     |        |                  |      |     |   |   |                          |
     v        v                  |      |     |   |   |                          |
 02-eligibility <----------------|------|-----+   |   |                          |
 (STOP GATE)                     |      |         |   |                          |
     |  verdict                  |      |         |   |                          |
     v                           |      |         |   |                          |
 03-narrative <------------------+      |         |   |                          |
 (APPROVAL GATE) <----------------------|---------+   |                          |
     |  approved narrative              |             |                          |
     +-------------+------------+-------|-------------|---------+                |
     |             |            |       |             |         |                |
     v             |            |       |             |         v                |
 04-budget <-------|------------|-------+ (limits)    |    06-support-letter <---+
     |   <---------|------------|---------------------+    (OPTIONAL; also reads 01)
     | budget      v            |                                  |
     +------> 05-evaluation <---+ (01: eval reqs, limits)          |
                   |                                               |
                   v                                               |
              07-compliance <---- 01 (full), 03, 04, 06-if-ran ----+
              (final: report, application.md/.pdf/.docx)

 Shared (read-only, references no stage):
   shared/organization-profile.md --> 02, 03, 06, 07
   shared/voice-rules.md          --> 03, 05, 06
```

**Linear order:** 01 → 02 → 03 → 04 → 05 → [06] → 07

Every arrow points from a lower-numbered stage, or from shared/per-run material, into a higher-numbered stage. No stage reads from a later stage, and shared files reference no stage. The graph is acyclic.

---

## Canonical Sources (one home per fact)

| Fact | Canonical home | Readers |
|------|---------------|---------|
| Funder requirements: eligibility rules, deadline, budget cap/match/disallowed costs, required sections, word limits, scoring criteria, attachments, letter-of-support flag, evaluation requirements | `01-requirements/output/requirements-checklist.md` | 02, 03, 04, 05, 06, 07 |
| Org name, mission, service area, past grants, board chair name and title | `shared/organization-profile.md` | 02, 03, 06, 07 |
| Plain-language voice rules and jargon list | `shared/voice-rules.md` | 03, 05, 06 |
| Eligibility verdict | `02-eligibility/output/eligibility-report.md` | 03 |
| Project activities and goals; approval status | `03-narrative/output/project-narrative.md` (header) | 04, 05, 06, 07 |
| Line-item costs and total | `04-budget/output/budget.md` | 05, 07 |
| Outcomes, targets, data sources | `05-evaluation/output/evaluation-plan.md` | 07 |
| Support letter text | `06-support-letter/output/support-letters.md` | 07 |
| Compliance verdicts; assembled application | `07-compliance/output/` | final deliverable |

Rules that follow from this table:

- Later stages quote the checklist; they never restate requirements as their own.
- The budget total lives only in `budget.md`. The evaluation plan and the application reference it rather than redefine it.

---

## Stage 01-requirements: Call to Requirements Checklist

### Inputs

| Source | File/Location | Section/Scope | Why |
|--------|--------------|---------------|-----|
| User (per run) | Call for proposals text, pasted into `01-requirements/input/call.md` | Full text | Source of all funder requirements |
| Stage reference | `references/checklist-format.md` | Full file | Defines the checklist fields and the "not stated in call" marking |

### Process

1. Read the call text in full.
2. Extract the funder's name, the project title (if given) and the deadline, with date, time and timezone.
3. Extract the eligibility rules, one per line.
4. Extract the budget limits: cap, minimum, match requirement and disallowed costs.
5. Extract the required sections, each with its word or character limit.
6. Extract the scoring criteria with their weights.
7. Extract the evaluation requirements.
8. Extract the required attachments.
9. Record whether a letter of support is requested (yes/no).
10. Mark every field the call does not address as "not stated in call". Never guess a value.
11. Quote the source sentence from the call for each item.
12. Run the audit, then write the checklist.

**Audit:** every field in `checklist-format.md` is filled or marked "not stated in call". Every item quotes its source.

### Outputs

| Artifact | Location | Format |
|----------|----------|--------|
| Requirements checklist | `output/requirements-checklist.md` | Markdown with fixed sections: Funder, Deadline, Eligibility, Budget Limits, Required Sections & Limits, Scoring Criteria, Evaluation Requirements, Attachments, Letter of Support Requested (yes/no). The user may edit it to correct misreads. |

---

## Stage 02-eligibility: Eligibility Check (stop gate)

### Inputs

| Source | File/Location | Section/Scope | Why |
|--------|--------------|---------------|-----|
| Previous stage | `../01-requirements/output/requirements-checklist.md` | "Eligibility" section only | The rules to test |
| Shared context | `../../shared/organization-profile.md` | Full file | The facts about the group |
| User (per run) | Group notes in `02-eligibility/input/group-notes.md` | Full file | Project-specific facts |

### Process

1. List each eligibility rule from the checklist.
2. Mark each rule as met, not met, or unclear, citing the evidence from the profile or the notes.
3. Set the verdict:
   - QUALIFIES if all rules are met.
   - DOES NOT QUALIFY if any rule is not met.
   - NEEDS CONFIRMATION otherwise.
4. **[Checkpoint]** Present the rule table and the verdict to the human. The human resolves the unclear items and confirms the verdict.
5. If the confirmed verdict is DOES NOT QUALIFY, write the report and stop the pipeline.
6. Run the audit, then write the report.

**Audit:** every checklist eligibility rule appears in the table with a status and evidence. The final verdict is QUALIFIES or DOES NOT QUALIFY, and no unclear items remain after the checkpoint.

### Outputs

| Artifact | Location | Format |
|----------|----------|--------|
| Eligibility report | `output/eligibility-report.md` | Header line `Verdict: QUALIFIES` or `Verdict: DOES NOT QUALIFY`, followed by the rule table (rule, status, evidence) and notes on resolved items |

---

## Stage 03-narrative: Project Narrative (approval gate)

### Inputs

| Source | File/Location | Section/Scope | Why |
|--------|--------------|---------------|-----|
| Stage 01 | `../01-requirements/output/requirements-checklist.md` | "Required Sections & Limits" and "Scoring Criteria" | Structure, limits and what is scored |
| Stage 02 | `../02-eligibility/output/eligibility-report.md` | Verdict line only | Do not run unless the verdict is QUALIFIES |
| Shared context | `../../shared/organization-profile.md` | Full file | Org name, mission, service area, past grants (capacity) |
| Shared context | `../../shared/voice-rules.md` | Full file | Plain-language rules and jargon list |
| User (per run) | `../02-eligibility/input/group-notes.md` | Full file | Project content |
| Stage reference | `references/narrative-section-guide.md` | Full file | Maps typical sections to criteria |

### Process

1. Confirm that the eligibility verdict is QUALIFIES. Stop otherwise.
2. Outline one entry per required section, naming the scoring criteria each section answers.
3. **[Checkpoint]** The human confirms the section-to-criterion map.
4. Draft each section in plain language within its word limit, using facts from the notes and the profile only.
5. Run the audit and revise until it passes.
6. **[Checkpoint]** The group reviews the full narrative and either approves it or requests changes. Repeat until approved.
7. Write the narrative with the header line `Approval: APPROVED by <name>, <date>`.

**Audit:** every required section is present. Every section is within its word limit, with word counts shown. Every scoring criterion maps to at least one section. There are no jargon-list violations. The approval line is present.

### Outputs

| Artifact | Location | Format |
|----------|----------|--------|
| Project narrative | `output/project-narrative.md` | Header: approval status line plus the criterion map. Then one H2 per required section, each followed by a word count. Ends with a "Project Activities" list and a "Project Goals" list for downstream tracing. |

---

## Stage 04-budget: Line-Item Budget and Justification

### Inputs

| Source | File/Location | Section/Scope | Why |
|--------|--------------|---------------|-----|
| Stage 01 | `../01-requirements/output/requirements-checklist.md` | "Budget Limits" only | Cap, match and disallowed costs |
| Stage 03 | `../03-narrative/output/project-narrative.md` | Approval line and "Project Activities" | Budget only the approved activities |
| User (per run) | `../02-eligibility/input/group-notes.md` | Cost information | Real prices and in-kind contributions |
| Stage reference | `references/budget-guide.md` | Full file | Categories, in-kind contributions, rounding |

### Process

1. Confirm that the narrative approval line reads APPROVED. Stop otherwise.
2. Build the line items by category, tying each line to a named narrative activity.
3. Add any in-kind and match lines as the checklist requires.
4. Write a one-to-three sentence justification for each line.
5. Total the request and compare it to the cap.
6. Run the audit and revise until it passes.

**Audit:** the total is at or under the cap. Every line has a justification and an activity tie. There are no disallowed costs. The arithmetic sums correctly. Any match requirement is met.

### Outputs

| Artifact | Location | Format |
|----------|----------|--------|
| Budget | `output/budget.md` | Line-item table (category, item, qty, unit cost, total, activity, cash or in-kind), a request total versus the cap, and a justification list keyed by line |

---

## Stage 05-evaluation: Evaluation Plan

### Inputs

| Source | File/Location | Section/Scope | Why |
|--------|--------------|---------------|-----|
| Stage 01 | `../01-requirements/output/requirements-checklist.md` | "Evaluation Requirements" and "Required Sections & Limits" (evaluation section) | Funder expectations and word limit |
| Stage 03 | `../03-narrative/output/project-narrative.md` | Approval line and "Project Goals" | Outcomes must trace to goals |
| Stage 04 | `../04-budget/output/budget.md` | Evaluation-related lines | Align the data collection with funded costs |
| Shared context | `../../shared/voice-rules.md` | Full file | Plain language |
| Stage reference | `references/outcome-guide.md` | Full file | Pattern: indicator, target, timeframe, data source |

### Process

1. Confirm that the narrative approval line reads APPROVED. Stop otherwise.
2. Pick two to three narrative goals that can be measured.
3. Write one outcome per goal using the indicator, target, timeframe and data source pattern.
4. Note who collects the data and how, referencing the budget lines where costs apply.
5. Run the audit and revise until it passes.

**Audit:** the plan has 2 to 3 outcomes. Each outcome has a numeric target, a timeframe and a data source. Each outcome names its narrative goal. The plan is within the word limit, if one is stated.

### Outputs

| Artifact | Location | Format |
|----------|----------|--------|
| Evaluation plan | `output/evaluation-plan.md` | Outcomes table (goal, indicator, target, timeframe, data source), a short data-collection paragraph and a word count |

---

## Stage 06-support-letter (optional): Letter of Support Draft

**Runs only if** the checklist field "Letter of Support Requested" is yes. Otherwise, the stage is skipped and writes nothing.

### Inputs

| Source | File/Location | Section/Scope | Why |
|--------|--------------|---------------|-----|
| Stage 01 | `../01-requirements/output/requirements-checklist.md` | "Letter of Support Requested" and any letter specifications | Run condition and requirements |
| Stage 03 | `../03-narrative/output/project-narrative.md` | Approval line and project summary | What the partner is supporting |
| Shared context | `../../shared/organization-profile.md` | Org name and service area | Letter content |
| Shared context | `../../shared/voice-rules.md` | Full file | Plain language |
| User (per run) | `06-support-letter/input/partners.md` | Full file | Partner names, roles and relationships |

### Process

1. Check the run condition. If it is no, skip the stage.
2. Confirm that the narrative is approved.
3. Draft one letter per partner, describing the partner's relationship and specific commitment, with a blank signature line.
4. Run the audit.

**Audit:** there is one letter per listed partner. Each letter meets the checklist specifications and contains no claims absent from the narrative or the partner notes.

### Outputs

| Artifact | Location | Format |
|----------|----------|--------|
| Support letters | `output/support-letters.md` | One H2 per partner, each holding the full letter text and a signature block |

---

## Stage 07-compliance: Final Compliance Pass and Export

### Inputs

| Source | File/Location | Section/Scope | Why |
|--------|--------------|---------------|-----|
| Stage 01 | `../01-requirements/output/requirements-checklist.md` | Full file | The standard to check against |
| Stage 03 | `../03-narrative/output/project-narrative.md` | Full file | Narrative content and approval |
| Stage 04 | `../04-budget/output/budget.md` | Full file | Budget content |
| Stage 05 | `../05-evaluation/output/evaluation-plan.md` | Full file | Evaluation content |
| Stage 06 (if ran) | `../06-support-letter/output/support-letters.md` | Full file | Attachments; required only if the checklist says yes |
| Shared context | `../../shared/organization-profile.md` | Org name, board chair name and title | Cover and signature block |
| Stage reference | `references/libreoffice-setup.md` | Full file | Export commands |

### Process

1. Assemble `application.md` in the funder's required section order, with the signature block for `{{BOARD_CHAIR_NAME}}`, `{{BOARD_CHAIR_TITLE}}`.
2. Check every checklist item and mark it PASS or FAIL with evidence:
   - required sections
   - word limits
   - budget cap
   - attachments, including letters if requested
   - deadline not passed
   - signature block present
3. If any item fails, list a fix for each and stop. Do not export.
4. **[Checkpoint]** The human reviews the compliance report and the assembled application and approves the export.
5. Export to PDF and .docx via headless LibreOffice.
6. Run the audit.

**Audit:** every checklist item is marked PASS. No export exists while any item is FAIL. Both exported files exist.

### Outputs

| Artifact | Location | Format |
|----------|----------|--------|
| Compliance report | `output/compliance-report.md` | Table of checklist item, status, evidence and fix |
| Application | `output/application.md` | Assembled submission text |
| Application PDF | `output/application.pdf` | LibreOffice export |
| Application Word | `output/application.docx` | LibreOffice export |

---

## Cross-Reference Verification

| Stage | Reads from | Read by |
|-------|-----------|---------|
| 01 | per-run call text | 02, 03, 04, 05, 06, 07 |
| 02 | 01, shared profile, notes | 03 |
| 03 | 01, 02, shared profile and voice, notes | 04, 05, 06, 07 |
| 04 | 01, 03, notes | 05, 07 |
| 05 | 01, 03, 04, shared voice | 07 |
| 06 | 01, 03, shared profile and voice, partners | 07 |
| 07 | 01, 03, 04, 05, 06, shared profile | final deliverable |

---

## Audit Results

| Check | Result | Notes |
|-------|--------|-------|
| No circular references | PASS | All edges go from lower to higher stage numbers. Shared files reference no stage. |
| Output consumption | PASS | 01 through 06 are each read downstream. 07 is the final deliverable. 06 is conditional, and 07 reads it only when the checklist flag is yes. |
| Contract completeness | PASS | All seven stages have filled Inputs, Process and Outputs. |
| Canonical sources | PASS | Each fact has one home (see the Canonical Sources table). |

---

## Assumptions

- **Step 7 checkpoint:** No user was available. The dependency flow and contracts are accepted as drawn, in line with the workflow description and the discovery map.
- **Group notes location:** The notes are stored once at `02-eligibility/input/group-notes.md`, the first stage that needs them. Later stages read that file so the notes have a single home. Scaffolding could move them to a run-level `inputs/` folder instead.
- **Call text location:** `01-requirements/input/call.md`.
- **Stage 06 reads the organization profile:** Discovery listed the profile for stages 02, 03 and 07 only. 06 also reads it for the letter text (org name and service area). This is a one-way read, so it adds no cycle.
- **Stage 05 reads voice-rules:** Kept from discovery.
- **Run identifiers in the checklist:** The "Project Activities" and "Project Goals" lists are added to the narrative output to give 04 and 05 a stable trace target. Funder name and deadline are recorded in the checklist so they have a single home.
- **Eligibility gate:** NEEDS CONFIRMATION must be resolved at the stage 02 checkpoint. The saved report carries only a final verdict.
- **Compliance checkpoint:** A human export approval is added before the LibreOffice export, consistent with the "no export until resolved" rule.
- **Deadline check:** Stage 07 flags FAIL if the stated deadline has passed at the time of the run.
</file>