<file path="stage-contracts.md">
# Stage Contracts: Community Grant Application Workspace

Formal Inputs/Process/Outputs contracts for every stage of the community grant workspace. These are derived from `../01-discovery/output/workflow-map.md`. Paths are relative to each stage folder (`stages/0N-name/`), unless they begin with `shared/`, which means the workspace root.

## Dependency Diagram

```
 PER-RUN INPUTS (Layer 4)              SHARED CONTEXT (read-only, points nowhere)
 call text | group notes |             shared/organization-profile.md
 partner names                          shared/voice-rules.md
      |                                         |
      v                                         v
 [01-requirements] --checklist--+------------------------------------------+
      |                         |              |            |              |
      v                         v              v            v              v
 [02-eligibility] --verdict--> [03-narrative] --approved--> [04-budget] --> [05-evaluation]
   (STOP GATE)                 (APPROVAL GATE)   |              |               |
                                    |            |              |               |
                                    +-----> [06-support-letter] (optional)      |
                                    |            |              |               |
                                    v            v              v               v
                                 [07-compliance] <------------------------------+
                                    |
                                    v
                         application.md / .pdf / .docx  (FINAL DELIVERABLE)
```

### Edge List

The graph is acyclic. Every edge points from a lower-numbered stage to a higher-numbered stage, or from shared context or per-run input into a stage.

| Consumer | Reads from |
|----------|-----------|
| 02 | 01, organization profile, group notes |
| 03 | 01, 02, organization profile, voice rules, group notes |
| 04 | 01, 03, group notes |
| 05 | 01, 03, 04, voice rules |
| 06 | 01, 03, voice rules, partner names |
| 07 | 01, 03, 04, 05, 06 (if it ran), organization profile |

### Who Consumes Each Output

| Output | Consumed by |
|--------|------------|
| 01 `requirements-checklist.md` | 02, 03, 04, 05, 06, 07 |
| 02 `eligibility-report.md` | 03 (gate); also the terminal artifact when the verdict stops the run |
| 03 `project-narrative.md` | 04, 05, 06, 07 |
| 04 `budget.md` | 05, 07 |
| 05 `evaluation-plan.md` | 07 |
| 06 `support-letters.md` | 07 |
| 07 `application.*` and `compliance-report.md` | Final deliverable |

### Output File Naming

Output artifacts follow `[topic-slug]-[artifact].md`. The topic slug is `[funder-slug]-[project-slug]`, which stage 01 sets from the call. For example: `riverbend-foundation-garden-requirements-checklist.md`. In the contracts below, the short names stand for the full slugged names.

## Canonical Sources (one home per fact)

| Fact | Canonical home | Everyone else |
|------|---------------|---------------|
| Funder requirements (eligibility, deadline, cap, sections, limits, criteria, attachments, letter flag) | 01 requirements checklist | Points to the checklist section |
| Eligibility verdict | 02 eligibility report | 03 reads the verdict only |
| Narrative approval status | 03 narrative header line `Approval: APPROVED / PENDING` | 04 to 07 check this line; they do not record approval themselves |
| Project activities and goals | 03 narrative | 04 and 05 trace to it |
| Budget figures and total | 04 budget | 05 and 07 read them, never restate them as authoritative |
| Outcomes and targets | 05 evaluation plan | 07 reads it |
| Organization details and signatory | `shared/organization-profile.md` | Stages read it; they do not copy values into references |
| Plain-language and jargon rules | `shared/voice-rules.md` | 03's narrative guide points to it and does not repeat it |
| Checklist field definitions | `01-requirements/references/checklist-format.md` | 07 checks against the checklist itself, not the format doc |
| LibreOffice install and command | `07-compliance/references/libreoffice-setup.md` | Workspace CLAUDE.md points here |

---

## 01-requirements

### Inputs

| Source | File/Location | Section/Scope | Why |
|--------|--------------|---------------|-----|
| User (per run) | Call for proposals text, pasted into chat or saved as `input/call.md` | Full text | Source of every requirement |
| Stage reference | `references/checklist-format.md` | Full file | Field list and the "not stated in call" marking rule |

### Process

1. Read the call text in full.
2. Set the topic slug from the funder name and the project name.
3. Extract eligibility rules. Write each one as a separately checkable item.
4. Extract the deadline, including the date, time, time zone and submission method.
5. Extract the budget limits: the cap, any match requirement, disallowed costs and the indirect-cost limit.
6. Extract the required sections, with the word or character limit for each one.
7. Extract the scoring criteria, with their weights.
8. Extract the required attachments, and mark whether a letter of support is requested (yes/no).
9. Mark every field the call does not mention as "not stated in call". Do not guess.
10. Quote the source sentence from the call for each extracted item.
11. Run the audit, then write the checklist.

### Audit

| Check | Pass Condition |
|-------|---------------|
| Field coverage | Every field in `checklist-format.md` has a value or reads "not stated in call" |
| Traceability | Every extracted item carries a quote from the call |
| Letter flag | "Letter of support requested" is explicitly yes or no |

### Outputs

| Artifact | Location | Format |
|----------|----------|--------|
| Requirements checklist | `output/[slug]-requirements-checklist.md` | Markdown checklist grouped by field, each item with a source quote; the user may edit it |

---

## 02-eligibility (stop gate)

### Inputs

| Source | File/Location | Section/Scope | Why |
|--------|--------------|---------------|-----|
| Previous stage | `../01-requirements/output/[slug]-requirements-checklist.md` | Eligibility section only | Rules to test |
| Shared context | `shared/organization-profile.md` | Full file | Organization facts (type, service area, past grants) |
| User (per run) | Group notes (`input/group-notes.md`) | Full file | Project-specific facts |

### Process

1. List every eligibility rule from the checklist.
2. For each rule, find the evidence in the profile or the notes, and mark the rule met, not met, or unclear.
3. Set the verdict:
   - DOES NOT QUALIFY if any rule is not met.
   - Otherwise NEEDS CONFIRMATION if any rule is unclear.
   - Otherwise QUALIFIES.
4. **[Checkpoint]** Present the rule table and the verdict to the user.
5. Record the human's resolutions of unclear items, and the final verdict.
6. If the final verdict is DOES NOT QUALIFY, write the report and stop the pipeline. The report includes a stop notice.
7. Run the audit, then write the report.

### Checkpoints

| After Step | Agent Presents | Human Decides |
|------------|---------------|---------------|
| 3 | Rule-by-rule table with evidence, plus the draft verdict | Confirms the verdict and resolves each unclear item |

### Audit

| Check | Pass Condition |
|-------|---------------|
| Rule coverage | Every checklist eligibility rule appears exactly once in the table |
| Evidence | Every met or not-met mark cites a profile or notes line |
| Final verdict | The final verdict is QUALIFIES or DOES NOT QUALIFY; no unclear items remain unresolved |

### Outputs

| Artifact | Location | Format |
|----------|----------|--------|
| Eligibility report | `output/[slug]-eligibility-report.md` | Header line `Verdict: QUALIFIES` or `Verdict: DOES NOT QUALIFY`, followed by the rule table and the human resolutions |

---

## 03-narrative (approval gate)

### Inputs

| Source | File/Location | Section/Scope | Why |
|--------|--------------|---------------|-----|
| Previous stage | `../01-requirements/output/[slug]-requirements-checklist.md` | Required sections, word limits and scoring criteria | Structure and targets |
| Previous stage | `../02-eligibility/output/[slug]-eligibility-report.md` | Verdict line only | Gate: proceed only on QUALIFIES |
| Shared context | `shared/organization-profile.md` | Full file | Name, mission, service area and track record |
| Shared context | `shared/voice-rules.md` | Full file | Plain-language and jargon rules |
| Stage reference | `references/narrative-section-guide.md` | Full file | Maps typical sections to criteria |
| User (per run) | Group notes | Full file | Project facts |

### Process

1. Confirm the verdict is QUALIFIES. If it is not, stop.
2. Outline the narrative using the funder's required section names, mapping each scoring criterion to at least one section.
3. **[Checkpoint]** Present the outline and the criterion map.
4. Draft each section in plain language, within its word limit. Use the notes and the profile.
5. Run the audit and revise until it passes.
6. **[Checkpoint]** Present the full narrative for group approval.
7. Apply any revisions. When approved, set the header to `Approval: APPROVED` with the approver's name and date. Until then the header reads `Approval: PENDING`.

### Checkpoints

| After Step | Agent Presents | Human Decides |
|------------|---------------|---------------|
| 2 | Section outline with the criterion each section answers | Confirms or reshapes the outline |
| 5 | Full narrative with word counts | The group approves, or requests revisions; no later stage runs without approval |

### Audit

| Check | Pass Condition |
|-------|---------------|
| Required sections | Every required section is present, using the funder's names |
| Word limits | Every section is at or under its limit, with counts shown |
| Criteria coverage | Every scoring criterion maps to at least one section |
| Voice | No terms from the `voice-rules.md` jargon list |

### Outputs

| Artifact | Location | Format |
|----------|----------|--------|
| Project narrative | `output/[slug]-project-narrative.md` | Header with the approval line and a criterion map, then the sections with word counts |

---

## 04-budget

### Inputs

| Source | File/Location | Section/Scope | Why |
|--------|--------------|---------------|-----|
| Previous stage | `../01-requirements/output/[slug]-requirements-checklist.md` | Budget limits only | Cap, match and disallowed costs |
| Previous stage | `../03-narrative/output/[slug]-project-narrative.md` | Approval line and activities | Gate, and the activities the budget may fund |
| Stage reference | `references/budget-guide.md` | Full file | Categories, in-kind contributions and rounding |
| User (per run) | Group notes | Cost information | Unit costs and quantities |

### Process

1. Confirm the narrative header reads `Approval: APPROVED`. If it does not, stop.
2. List the narrative activities.
3. Build the line items by category (quantity × unit cost), each tied to an activity.
4. Add in-kind and match lines if the call requires them.
5. Total the budget and compare it with the cap. Trim if it is over.
6. Write a justification for each line.
7. Run the audit, then write the budget.

### Audit

| Check | Pass Condition |
|-------|---------------|
| Cap | The requested total is at or under the cap |
| Justification | Every line has a justification |
| Traceability | Every line names a narrative activity |
| Disallowed costs | No line falls under a disallowed category |
| Arithmetic | Line totals and the grand total recompute exactly |

### Outputs

| Artifact | Location | Format |
|----------|----------|--------|
| Budget | `output/[slug]-budget.md` | Line-item table (category, item, quantity, unit cost, total, activity), followed by the justification |

---

## 05-evaluation

### Inputs

| Source | File/Location | Section/Scope | Why |
|--------|--------------|---------------|-----|
| Previous stage | `../01-requirements/output/[slug]-requirements-checklist.md` | Evaluation requirements and word limits | Constraints |
| Previous stage | `../03-narrative/output/[slug]-project-narrative.md` | Approval line and goals | Gate; outcomes must trace to the goals |
| Previous stage | `../04-budget/output/[slug]-budget.md` | Evaluation-related lines | Cost alignment |
| Shared context | `shared/voice-rules.md` | Full file | Plain language |
| Stage reference | `references/outcome-guide.md` | Full file | Indicator / target / timeframe / data source pattern |

### Process

1. Confirm the narrative is approved. If it is not, stop.
2. List the narrative goals.
3. Write 2 to 3 outcomes, each with an indicator, a numeric target, a timeframe and a data source.
4. Name the data collection method and who is responsible, consistent with the budget lines.
5. Fit the plan within any word limit.
6. Run the audit, then write the plan.

### Audit

| Check | Pass Condition |
|-------|---------------|
| Count | The plan has 2 to 3 outcomes |
| Measurability | Each outcome has a numeric target, a timeframe and a data source |
| Traceability | Each outcome names a narrative goal |
| Limit | The plan is within its word limit, if the call sets one |

### Outputs

| Artifact | Location | Format |
|----------|----------|--------|
| Evaluation plan | `output/[slug]-evaluation-plan.md` | Outcome table plus a short methods paragraph |

---

## 06-support-letter (optional)

Runs only when the checklist field "Letter of support requested" reads yes.

### Inputs

| Source | File/Location | Section/Scope | Why |
|--------|--------------|---------------|-----|
| Previous stage | `../01-requirements/output/[slug]-requirements-checklist.md` | Letter flag and letter requirements | Trigger and specifications |
| Previous stage | `../03-narrative/output/[slug]-project-narrative.md` | Approval line and project summary | Content for the letters |
| Shared context | `shared/voice-rules.md` | Full file | Plain language |
| User (per run) | Partner names and roles | Full list | Who signs, and their role in the project |

### Process

1. Check the letter flag. If it reads no, record "skipped" and stop.
2. Confirm the narrative is approved.
3. Draft one letter per partner, stating their relationship to the group and their specific commitment.
4. Leave a signature block for each partner.
5. Run the audit, then write the letters.

### Audit

| Check | Pass Condition |
|-------|---------------|
| Coverage | There is one letter per named partner |
| Specificity | Each letter states a concrete commitment tied to a narrative activity |
| Requirements | Each letter meets any length or addressee rule in the checklist |

### Outputs

| Artifact | Location | Format |
|----------|----------|--------|
| Support letters | `output/[slug]-support-letters.md` | One section per partner, each with a signature block |

---

## 07-compliance (final)

### Inputs

| Source | File/Location | Section/Scope | Why |
|--------|--------------|---------------|-----|
| Previous stage | `../01-requirements/output/[slug]-requirements-checklist.md` | Full file | What to check against |
| Previous stage | `../03-narrative/output/[slug]-project-narrative.md` | Full file | Application body and approval |
| Previous stage | `../04-budget/output/[slug]-budget.md` | Full file | Budget section |
| Previous stage | `../05-evaluation/output/[slug]-evaluation-plan.md` | Full file | Evaluation section |
| Previous stage | `../06-support-letter/output/[slug]-support-letters.md` | Full file, only if the letter flag reads yes | Attachments |
| Shared context | `shared/organization-profile.md` | Board chair name and title | Signature block |
| Stage reference | `references/libreoffice-setup.md` | Full file | Export command |

### Process

1. Confirm the narrative is approved, and that the letters file exists if the flag reads yes.
2. Assemble `application.md` in the funder's section order, adding a signature block for `{{BOARD_CHAIR_NAME}}`, `{{BOARD_CHAIR_TITLE}}`.
3. Check each checklist item: section present, word limits, budget cap, attachments, deadline not passed, signature block. Mark each item pass or fail.
4. For each fail, record the fix and the stage that owns it.
5. If any item fails, write only the compliance report and stop. Do not export.
6. When all items pass, export to PDF and .docx with headless LibreOffice.
7. Run the audit, then write the outputs.

### Audit

| Check | Pass Condition |
|-------|---------------|
| Checklist pass | Every checklist item is marked pass |
| Failure handling | Any failure has a listed fix, and no export files exist |
| Export | The .pdf and .docx exist and open, and their section count matches `application.md` |

### Outputs

| Artifact | Location | Format |
|----------|----------|--------|
| Compliance report | `output/[slug]-compliance-report.md` | Table of checklist items with pass/fail and fixes |
| Application | `output/[slug]-application.md` | Assembled markdown |
| Application PDF | `output/[slug]-application.pdf` | LibreOffice export |
| Application Word | `output/[slug]-application.docx` | LibreOffice export |

---

## Audit Results (stage 02-mapping)

| Check | Result |
|-------|--------|
| No circular references | PASS. Every edge points forward. Shared files reference no stage. |
| Output consumption | PASS. 01 through 06 are each read downstream; 07 is the final deliverable. 02 is read by 03, and its report is also the terminal artifact on a stop. |
| Contract completeness | PASS. All 7 stages have filled Inputs, Process and Outputs. |
| Canonical sources | PASS. See the canonical table. The approval status lives only in the 03 header. Voice rules live only in shared context. |

## Assumptions

- **Step 7 checkpoint:** No user interaction was possible. I accepted the dependency flow and contracts as consistent with the workflow description, with no missing connections identified.
- **Voice rules for stage 06:** The discovery map lists voice rules for stages 03, 05 and 06. I kept stage 06 as a reader.
- **Output naming:** I added a `[funder-slug]-[project-slug]` topic slug, set in stage 01, to follow the `[topic-slug]-[artifact]` naming convention. Discovery's short names are used as the artifact part.
- **Per-run input location:** Per-run inputs are pasted in chat or saved in an `input/` folder at the workspace level. Scaffolding may finalize the location.
- **Verdict rule:** Any rule marked not met makes the verdict DOES NOT QUALIFY. NEEDS CONFIRMATION is only a draft state; it must resolve at the checkpoint before stage 03 runs.
- **Compliance on failure:** Stage 07 routes fixes back by naming the owning stage in its report. It does not reference that stage's folder for writing, so the flow stays one-way. The user re-runs the owning stage manually.
- **Deadline check:** The deadline check compares the run date to the checklist deadline.
- **Stage 05 reading 04:** Stage 05 reads only the evaluation-related budget lines, as discovery specified. The budget remains canonical for costs.
</file>