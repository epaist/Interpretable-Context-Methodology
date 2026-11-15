<file path="scaffold-report.md">
# Scaffold Report: Community Grant Application Workspace

Stage 03 output. The generated workspace is in `community-grants/`. It is ready for stage 04 (questionnaire design).

## Generated Tree

```
community-grants/
├── CLAUDE.md
├── CONTEXT.md
├── setup/
│   └── .gitkeep                      (stage 04 writes questionnaire.md here)
├── shared/                           (context folder: organization facts and voice)
│   ├── CONTEXT.md
│   ├── organization-profile.md
│   └── voice-rules.md
└── stages/
    ├── 01-requirements/      CONTEXT.md, output/.gitkeep, references/checklist-format.md
    ├── 02-eligibility/       CONTEXT.md, output/.gitkeep, references/.gitkeep
    ├── 03-narrative/         CONTEXT.md, output/.gitkeep, references/narrative-section-guide.md
    ├── 04-budget/            CONTEXT.md, output/.gitkeep, references/budget-guide.md
    ├── 05-evaluation/        CONTEXT.md, output/.gitkeep, references/outcome-guide.md
    ├── 06-support-letter/    CONTEXT.md, output/.gitkeep, references/.gitkeep
    └── 07-compliance/        CONTEXT.md, output/.gitkeep, references/libreoffice-setup.md
```

## Placeholders Created (for stage 04)

| Placeholder | File(s) |
|-------------|---------|
| `{{ORG_NAME}}` | `shared/organization-profile.md` |
| `{{MISSION_STATEMENT}}` | `shared/organization-profile.md` |
| `{{SERVICE_AREA}}` | `shared/organization-profile.md` |
| `{{PAST_GRANTS}}` | `shared/organization-profile.md` |
| `{{BOARD_CHAIR_NAME}}` | `shared/organization-profile.md` |
| `{{BOARD_CHAIR_TITLE}}` | `shared/organization-profile.md` |
| `{{ORG_LEGAL_STATUS}}` | `shared/organization-profile.md` |
| `{{ANNUAL_OPERATING_BUDGET}}` | `shared/organization-profile.md` |
| `{{READING_LEVEL}}` | `shared/voice-rules.md` |
| `{{JARGON_LIST}}` | `shared/voice-rules.md` |

## Audit Results

| Check | Result | Notes |
|-------|--------|-------|
| Folder structure | PASS | All 7 stages have CONTEXT.md, output/ and references/. Empty references/ folders hold a .gitkeep. |
| Contract fidelity | PASS | Inputs, Process, Checkpoints, Audit and Outputs follow `stage-contracts.md`. The two wording changes are listed under Assumptions. |
| Placeholder syntax | PASS | All placeholders use `{{SCREAMING_SNAKE_CASE}}`. None appear in CLAUDE.md, routing tables or stage CONTEXT.md process steps. |
| .gitkeep coverage | PASS | All 7 `output/` folders have a .gitkeep. |
| CONTEXT.md size | PASS | The largest file is 07-compliance, at about 60 lines. |
| Naming conventions | PASS | All folders and files use lowercase-with-hyphens. |

## Assumptions

- **Workspace folder name:** `community-grants`.
- **Context folder:** The contracts fix the paths `../../shared/organization-profile.md` and `../../shared/voice-rules.md`.
  - `shared/` therefore serves as both the context folder and the cross-stage folder, with its own CONTEXT.md.
  - No separate brand-vault folder was created, so paths do not need to change.
- **Board chair in stage 07:** The contract wrote `{{BOARD_CHAIR_NAME}}` and `{{BOARD_CHAIR_TITLE}}` inside a process step. Placeholder rules allow placeholders in stage CONTEXT.md only in Inputs table values.
  - Step 1 now says to take the "Board Chair Name" and "Board Chair Title" fields from `organization-profile.md`.
  - The placeholders live only in the profile, which is their one canonical home.
- **Optional stage 06:** The stage is kept as a run-time skip driven by the checklist flag.
  - The `{{?SUPPORT_LETTER_STAGE}}` wrapper was not used. Placeholders must not appear in CLAUDE.md or routing tables, and the need varies by funder, not by group.
- **Value framework (Pattern 13):** The workspace produces written content, but the "value" is set by each funder's scoring criteria.
  - The framework is placed in `03-narrative/references/narrative-section-guide.md`, as a "What Reviewers Value" section.
  - It is not a new shared file, which would have added an input the contracts do not list.
- **Pattern 15:** Not applied. The workspace does not produce code.
- **Voice rules:** Structured as Hard Constraints, Sentence Rules and Pacing. Two placeholders were added: `{{READING_LEVEL}}` and `{{JARGON_LIST}}`.
  - The narrative audit checks the jargon list, so the list must be filled per group.
- **Extra profile fields:** `{{ORG_LEGAL_STATUS}}` and `{{ANNUAL_OPERATING_BUDGET}}` were added. Eligibility rules almost always ask for these.
  - Stage 04 may drop them if the user declines.
- **Skills:** No skills folder. Discovery selected none.
- **LibreOffice route:** LibreOffice cannot reliably convert Markdown directly.
  - The setup guide has the agent write an HTML copy of the assembled application, then convert that HTML to PDF and .docx with headless `soffice`.
- **Setup folder:** Holds only a .gitkeep. The questionnaire is stage 04's output.
- **Per-run inputs:** The call text, group notes and partner names are pasted at run time. They have no files and no placeholders, following the discovery output.
</file>

<file path="community-grants/CLAUDE.md">
# Community Grant Application

Turns a local foundation's call for proposals and a community group's notes into a compliance-checked, submission-ready grant application (PDF and Word).

## Folder Map

```
community-grants/
├── CLAUDE.md          (you are here)
├── CONTEXT.md         (start here for task routing)
├── setup/             (onboarding questionnaire)
├── shared/            (organization profile and plain-language voice rules)
└── stages/
    ├── 01-requirements/     (call text -> requirements checklist)
    ├── 02-eligibility/      (eligibility check; stop gate)
    ├── 03-narrative/        (project narrative; group approval gate)
    ├── 04-budget/           (line-item budget and justification)
    ├── 05-evaluation/       (evaluation plan, 2-3 outcomes)
    ├── 06-support-letter/   (optional: only if the funder asks)
    └── 07-compliance/       (compliance pass, assembly, PDF/Word export)
```

## Triggers

| Keyword | Action |
|---------|--------|
| `setup` | Run the onboarding questionnaire in `setup/questionnaire.md` |
| `status` | Show pipeline completion for all stages |

### How `status` works

Scan `stages/*/output/` for each stage.

- If the folder holds files other than .gitkeep, the stage is COMPLETE. Otherwise it is PENDING.
- Mark 06 as SKIPPED when the checklist says "Letter of support requested: no".

Render the result like this:

```
Pipeline Status: community-grants
  [01] -> [02] -> [03] -> [04] -> [05] -> [06 opt] -> [07]
```

## Routing

| Task | Go To |
|------|-------|
| Start a new application from a call | `stages/01-requirements/CONTEXT.md` |
| Check eligibility | `stages/02-eligibility/CONTEXT.md` |
| Draft the project narrative | `stages/03-narrative/CONTEXT.md` |
| Build the budget | `stages/04-budget/CONTEXT.md` |
| Write the evaluation plan | `stages/05-evaluation/CONTEXT.md` |
| Draft letters of support | `stages/06-support-letter/CONTEXT.md` |
| Final compliance check and export | `stages/07-compliance/CONTEXT.md` |

## What to Load

| Task | Load These | Do NOT Load |
|------|-----------|-------------|
| Requirements | Call text, `stages/01-requirements/references/checklist-format.md` | `shared/`, all other stages |
| Eligibility | 01 checklist (Eligibility section), `shared/organization-profile.md`, group notes | `shared/voice-rules.md`, stages 03-07 |
| Narrative | 01 checklist (Sections and Limits, Scoring), 02 verdict line, `shared/`, `stages/03-narrative/references/`, group notes | Stages 04-07 |
| Budget | 01 checklist (Budget Limits), 03 narrative (approval line and activities), `stages/04-budget/references/`, group notes (costs) | `shared/`, stages 02, 05-07 |
| Evaluation | 03 narrative (approval line and goals), 04 budget (evaluation lines), 01 checklist (Evaluation, Sections and Limits), `shared/voice-rules.md`, `stages/05-evaluation/references/` | Stages 02, 06, 07 |
| Support letters | 01 checklist (Support Letter, Attachments), 03 narrative (approval line and description), org name, `shared/voice-rules.md`, partner list | Stages 02, 04, 05, 07 |
| Compliance | Full outputs of 01, 03, 04, 05, and 06 if present; org name and board chair fields; `stages/07-compliance/references/` | Stage 02, `shared/voice-rules.md` |

## Stage Handoffs

Each stage writes its output to its own `output/` folder, and the next stage reads from there. If you edit an output file, the next stage picks up your edits.

All artifacts are prefixed with the run's project slug.
</file>

<file path="community-grants/CONTEXT.md">
# Community Grant Application

Seven-stage pipeline from a funder's call for proposals to a submission-ready application. It covers local foundation grants of $5,000 to $50,000.

## Task Routing

| Task Type | Go To | Description |
|-----------|-------|-------------|
| Requirements | `stages/01-requirements/CONTEXT.md` | Extract the funder's rules into a checklist |
| Eligibility | `stages/02-eligibility/CONTEXT.md` | Check the group against each rule; stop if it does not qualify |
| Narrative | `stages/03-narrative/CONTEXT.md` | Draft the narrative against the scoring criteria; the group must approve it |
| Budget | `stages/04-budget/CONTEXT.md` | Line-item budget and justification under the cap |
| Evaluation | `stages/05-evaluation/CONTEXT.md` | Plan with 2-3 measurable outcomes |
| Support letters (optional) | `stages/06-support-letter/CONTEXT.md` | Partner letters, only if the funder requests them |
| Compliance | `stages/07-compliance/CONTEXT.md` | Check every requirement, assemble, export to PDF and Word |

## Shared Resources

| Resource | Location | Contains |
|----------|----------|----------|
| Context folder | `shared/CONTEXT.md` | Routes to the organization profile and voice rules |
| Organization profile | `shared/organization-profile.md` | Name, mission, service area, past grants, board chair |
| Voice rules | `shared/voice-rules.md` | Plain-language hard constraints, sentence rules, pacing, jargon list |

## Per-Run Inputs

Paste these in at run time. Each run has a new funder, deadline and project.

- The call for proposals text.
- The group's notes for this project.
- Partner names and roles, only if letters are requested.
</file>

<file path="community-grants/setup/.gitkeep">
</file>

<file path="community-grants/shared/CONTEXT.md">
# Shared Context

Persistent facts about the group and how it writes. Onboarding (`setup`) fills these files once, and they carry across every run. Shared files read from no stage.

| File | Contains | Read By |
|------|----------|---------|
| `organization-profile.md` | Org name, legal status, budget size, mission, service area, past grants, board chair | 02, 03, 06 (name only), 07 (name and board chair) |
| `voice-rules.md` | Plain-language hard constraints, sentence rules, pacing, jargon list | 03, 05, 06 |

Update a fact here, not in stage outputs. Each fact has one home.
</file>

<file path="community-grants/shared/organization-profile.md">
# Organization Profile

Canonical facts about the applicant group. These stay the same across runs.

## Organization Name

{{ORG_NAME}}

## Legal Status

{{ORG_LEGAL_STATUS}}

## Annual Operating Budget

{{ANNUAL_OPERATING_BUDGET}}

## Mission Statement

{{MISSION_STATEMENT}}

## Service Area

{{SERVICE_AREA}}

## Past Grants

List each prior grant as: funder, year, amount, purpose.

{{PAST_GRANTS}}

## Board Chair

- Board Chair Name: {{BOARD_CHAIR_NAME}}
- Board Chair Title: {{BOARD_CHAIR_TITLE}}
</file>

<file path="community-grants/shared/voice-rules.md">
# Voice Rules: Plain Language

Every applicant-facing text follows these rules: narrative, evaluation plan and support letters.

## Hard Constraints

- Target reading level: {{READING_LEVEL}}
- Never use a term from the Jargon List below. Say what you mean instead.
- Do not invent numbers, partners or results. Every fact must come from the group notes or the organization profile.
- Never exceed a funder's word or character limit.
- Name the community and the people served concretely. Do not write "stakeholders" or "beneficiaries".

## Sentence Rules

- Keep sentences to one idea and 25 words or fewer.
- Use active voice: "We will run 12 workshops", not "Workshops will be conducted".
- Write numbers as digits, with units: "40 families", "$3,200".
- Spell out every acronym on first use.

## Pacing

- Open each section with its main point in one sentence.
- Follow with evidence (numbers, a short example), then what the grant will change.
- Keep paragraphs to 3 to 5 sentences. Use a list only when the funder's format allows it.

## Jargon List

Terms the narrative audit rejects:

{{JARGON_LIST}}
</file>

<file path="community-grants/stages/01-requirements/CONTEXT.md">
# Stage 01: Requirements

Extract the funder's requirements from the call for proposals into one checklist.

## Inputs

| Source | File/Location | Section/Scope | Why |
|--------|--------------|---------------|-----|
| User (per run) | Call for proposals text, pasted at run start | Full text | The funder's rules to extract |
| Stage reference | `references/checklist-format.md` | Full file | Field list and how to mark "not stated in call" |

## Process

1. Ask the user to paste the call for proposals text and give a short project slug (lowercase-with-hyphens).
2. Extract the following:
   - Funder name and deadline.
   - Eligibility rules.
   - Budget limits: cap, match and disallowed costs.
   - Required sections, with word or character limits.
   - Scoring criteria and weights.
   - Required attachments and evaluation requirements.
   - Whether a letter of support is requested.
3. Mark any field the call does not cover as "not stated in call".
4. Write the checklist using the format in `references/checklist-format.md`.
5. **[Checkpoint]** Show the checklist; the user corrects any misread item.
6. Run the audit, then save.

## Checkpoints

| After Step | Agent Presents | Human Decides |
|------------|---------------|---------------|
| 4 | Draft requirements checklist | Corrections to any misread requirement |

## Audit

| Check | Pass Condition |
|-------|---------------|
| Field coverage | Every field in the checklist format has a value or "not stated in call" |
| Source fidelity | Every limit, date and amount appears in the call text as written |
| Support letter flag | "Letter of support requested" is explicitly yes or no |

## Outputs

| Artifact | Location | Format |
|----------|----------|--------|
| Requirements checklist | `output/[slug]-requirements-checklist.md` | Markdown checklist with one section per field group: Eligibility, Deadline, Budget Limits, Sections and Limits, Scoring, Attachments, Evaluation, Support Letter |
</file>

<file path="community-grants/stages/01-requirements/output/.gitkeep">
</file>

<file path="community-grants/stages/01-requirements/references/checklist-format.md">
# Checklist Format

Use these sections in this order.

- Every field gets a value, or the exact text `not stated in call`.
- Copy limits, dates and amounts exactly as the call writes them.
- Add a short quote or page/heading reference in brackets where possible.

```markdown
# Requirements Checklist: [Funder Name] - [slug]

## Eligibility
- [ ] Rule 1: ...
- [ ] Rule 2: ...

## Deadline
- Submission deadline (date, time, time zone): ...
- Submission method (portal, email, mail): ...

## Budget Limits
- Maximum request (cap): ...
- Minimum request: ...
- Match or cost share required: ...
- Disallowed costs: ...
- Indirect/overhead limit: ...
- Grant period: ...

## Sections and Limits
| # | Required Section | Limit (words/characters/pages) | Notes |
|---|------------------|-------------------------------|-------|

## Scoring
| Criterion | Weight/Points | What reviewers look for |
|-----------|---------------|-------------------------|

## Attachments
- [ ] Attachment: ... (format rules)

## Evaluation
- Evaluation requirements: ...
- Evaluation word limit: ...

## Support Letter
- Letter of support requested: yes / no
- Number of letters: ...
- Content or addressee rules: ...
```

If a call puts a field in an unusual place, it still goes in its field group above. The section order is fixed so that downstream stages can read single sections.
</file>

<file path="community-grants/stages/02-eligibility/CONTEXT.md">
# Stage 02: Eligibility

Check the group against each eligibility rule and give a verdict. The run stops if the group does not qualify.

## Inputs

| Source | File/Location | Section/Scope | Why |
|--------|--------------|---------------|-----|
| Previous stage | `../01-requirements/output/[slug]-requirements-checklist.md` | "Eligibility" section only | Rules to check |
| Shared context | `../../shared/organization-profile.md` | Full file | Facts about the group |
| User (per run) | Group notes | Full text | Project-specific facts relevant to eligibility |

## Process

1. Read each eligibility rule.
2. Mark each rule met, not met, or unclear, with the supporting fact from the profile or notes.
3. Give one verdict: QUALIFIES, DOES NOT QUALIFY, or NEEDS CONFIRMATION.
4. **[Checkpoint]** Present the rule table and verdict. The human resolves every unclear item and confirms the verdict.
5. Update the verdict after the human resolves the unclear items. If the verdict is DOES NOT QUALIFY, save the report and stop the run.
6. Run the audit, then save.

## Checkpoints

| After Step | Agent Presents | Human Decides |
|------------|---------------|---------------|
| 3 | Rule-by-rule table and draft verdict | Resolution of unclear items; confirm or change verdict |

## Audit

| Check | Pass Condition |
|-------|---------------|
| Rule coverage | Every eligibility rule in the checklist has a row |
| Evidence | Every met or not-met row cites a fact from the profile or notes |
| Final verdict | Verdict is QUALIFIES or DOES NOT QUALIFY; no unclear items remain |

## Outputs

| Artifact | Location | Format |
|----------|----------|--------|
| Eligibility report | `output/[slug]-eligibility-report.md` | `Verdict: QUALIFIES` or `Verdict: DOES NOT QUALIFY` line at top, then a table: Rule, Status, Evidence |
</file>

<file path="community-grants/stages/02-eligibility/output/.gitkeep">
</file>

<file path="community-grants/stages/02-eligibility/references/.gitkeep">
</file>

<file path="community-grants/stages/03-narrative/CONTEXT.md">
# Stage 03: Narrative

Draft the project narrative section by section in plain language, matched to the scoring criteria. The group must approve it before any later stage runs.

## Inputs

| Source | File/Location | Section/Scope | Why |
|--------|--------------|---------------|-----|
| Previous stage | `../01-requirements/output/[slug]-requirements-checklist.md` | "Sections and Limits" and "Scoring" sections | What to write and how it is scored |
| Previous stage | `../02-eligibility/output/[slug]-eligibility-report.md` | Verdict line only | Confirm the run may continue |
| Shared context | `../../shared/organization-profile.md` | Full file | Mission, service area, capacity, past grants |
| Shared context | `../../shared/voice-rules.md` | Full file | Plain-language rules and jargon list |
| Stage reference | `references/narrative-section-guide.md` | Full file | Typical sections, criterion mapping, what reviewers value |
| User (per run) | Group notes | Full text | Project facts |

## Process

1. Stop if the eligibility verdict is not QUALIFIES.
2. Outline the narrative: one entry per required section, naming the scoring criteria each one answers and its word limit.
3. **[Checkpoint]** Present the outline and criterion map; the human confirms or changes it.
4. Draft each section in plain language, within its word limit.
5. Run the audit and revise until it passes.
6. **[Checkpoint]** Present the full narrative; the group approves or requests changes. Repeat steps 4 to 6 until approved.
7. Save with the header line `Approval: APPROVED by [name], [date]`.

## Checkpoints

| After Step | Agent Presents | Human Decides |
|------------|---------------|---------------|
| 2 | Section outline with criterion map | Confirm the sections and criterion coverage |
| 5 | Full draft narrative with word counts | Approve, or list changes |

## Audit

| Check | Pass Condition |
|-------|---------------|
| Required sections | Every required section in the checklist is present |
| Word limits | Every section is at or under its limit |
| Criterion coverage | Every scoring criterion is addressed by at least one section |
| Plain language | No term from the jargon list in voice-rules.md appears |

## Outputs

| Artifact | Location | Format |
|----------|----------|--------|
| Project narrative | `output/[slug]-project-narrative.md` | Header with approval status line, then one heading per required section with word count noted |
</file>

<file path="community-grants/stages/03-narrative/output/.gitkeep">
</file>

<file path="community-grants/stages/03-narrative/references/narrative-section-guide.md">
# Narrative Section Guide

Map each funder-required section to the criteria it answers. Use the funder's section names and order. The typical sections below are only a fallback.

## Typical Sections and the Criteria They Answer

| Typical Section | Usually Answers | Contents |
|-----------------|-----------------|----------|
| Statement of Need | Need, community impact | Who is affected in the service area, how many, local evidence, why now |
| Project Description | Approach, feasibility | Goals, activities, who does what, timeline, people served |
| Goals and Activities | Clarity, measurability | 2 to 4 goals, each with the activities that achieve it. Later stages read these. |
| Organizational Capacity | Capacity, track record | Mission fit, past grants, volunteers and staff, partners |
| Sustainability | Long-term impact | How the work continues after the grant |
| Community Involvement | Equity, participation | How the people served shape the project |

If a criterion has no matching section, address it inside the closest section and name it in the outline.

## Label Goals and Activities Clearly

Stages 04 and 05 read goals and activities from this file. Write them as follows:

- **Goal 1:** one sentence.
  - Activity 1.1 ...
  - Activity 1.2 ...

## What Reviewers Value (Value Framework)

Small local foundations score proposals on these points:

1. **Local proof.** Name the neighborhood. Give a local number and a real (anonymized) example.
2. **Clear change.** State what will be different, and for whom, by the end of the grant period.
3. **Right size.** Show that the request fits the activities and the group's capacity.
4. **Trust.** Mention past grants completed and partners named.
5. **Weight follows points.** Give each criterion space in proportion to its scoring weight.

## Word Counting

- Count words per section and note the count under each heading as `(N / limit words)`.
- For character limits, count characters including spaces.
</file>

<file path="community-grants/stages/04-budget/CONTEXT.md">
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
6. Run the audit and revise until it passes.

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

<file path="community-grants/stages/04-budget/output/.gitkeep">
</file>

<file path="community-grants/stages/04-budget/references/budget-guide.md">
# Budget Guide

## Cost Categories

Use these categories in this order. Omit any that are empty. If the funder has its own categories, use the funder's instead.

1. Personnel (staff time, stipends)
2. Contracted services (facilitators, trainers, evaluators)
3. Supplies and materials
4. Equipment (only if the funder allows it)
5. Space and facilities
6. Travel and transportation
7. Outreach and printing
8. Evaluation
9. Indirect/overhead (only up to the funder's limit)

## Line Item Rules

- **Unit math.** Show the calculation in the Item column, e.g. "Facilitator, 12 sessions x $150".
- **Rounding.** Round each line to the nearest whole dollar, and compute totals from the rounded lines.
- **In-kind.** Volunteer time, donated space and donated goods go in the In-kind column, never in Request. Value volunteer time at the rate in the group notes, or mark it "rate to confirm".
- **Match.** If the funder requires a match, show it as a separate total.

## Table Shape

| Category | Item | Request | In-kind | Activity |
|----------|------|---------|---------|----------|
| ... | ... | $0 | $0 | Activity 1.1 |
| **Totals** | | **$0** | **$0** | |

Add a line under the table: "Funder cap: $X. Request: $Y. Under cap by $Z."

## Justification Format

One heading per line item, with 1 to 3 sentences covering:

- what the cost buys;
- which narrative activity it supports;
- how the amount was estimated.
</file>

<file path="community-grants/stages/05-evaluation/CONTEXT.md">
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
5. Run the audit and revise until it passes.

## Audit

| Check | Pass Condition |
|-------|---------------|
| Outcome count | 2 or 3 outcomes |
| Measurable | Each outcome has a numeric target, a timeframe and a data source |
| Traceable | Each outcome names the narrative goal it measures |
| Word limit | Plan is within the checklist limit, if one is stated |

## Outputs

| Artifact | Location | Format |
|----------|----------|--------|
| Evaluation plan | `output/[slug]-evaluation-plan.md` | Short intro, then an outcome table (Goal, Indicator, Target, Timeframe, Data Source) |
</file>

<file path="community-grants/stages/05-evaluation/output/.gitkeep">
</file>

<file path="community-grants/stages/05-evaluation/references/outcome-guide.md">
# Outcome Guide

## Pattern

> By [timeframe], [number or percent] of [who] will [observable change], measured by [data source].

The pattern has four parts:

- **Indicator:** the thing you count or observe (e.g. "families attending 3+ sessions").
- **Target:** a number or percent. Never "more" or "improved".
- **Timeframe:** a date or point in the grant period.
- **Data source:** a sign-in sheet, a short pre/post survey, a partner records count, or photos with dates.

## Rules for Small Groups

- Prefer data the group already collects. Each method must be doable by volunteers.
- Count outputs (people served) for one outcome at most. At least one outcome must show a change (skill, access, behavior).
- Set targets from the group notes or past results, not guesses. If no baseline exists, say so and set a modest target.
- If collection costs money (survey tool, evaluator), it must match an Evaluation line in the budget.

## Table Shape

| Goal | Indicator | Target | Timeframe | Data Source |
|------|-----------|--------|-----------|-------------|
| Goal 1: ... | ... | 75% of 40 participants | By month 6 | Pre/post survey |
</file>

<file path="community-grants/stages/06-support-letter/CONTEXT.md">
# Stage 06: Support Letter (optional)

Draft letters of support for partners to sign. This stage runs only when the checklist says "Letter of support requested: yes". Otherwise it is skipped, and stage 07 does not expect its output.

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
5. Run the audit, then save.

## Audit

| Check | Pass Condition |
|-------|---------------|
| Count | One letter per partner, and at least the number the funder requests |
| Specific | Each letter names the project and the partner's concrete role |
| Signature block | Each letter has a partner name and title line |

## Outputs

| Artifact | Location | Format |
|----------|----------|--------|
| Support letters | `output/[slug]-support-letters.md` | One heading per partner, letter text, signature block |
</file>

<file path="community-grants/stages/06-support-letter/output/.gitkeep">
</file>

<file path="community-grants/stages/06-support-letter/references/.gitkeep">
</file>

<file path="community-grants/stages/07-compliance/CONTEXT.md">
# Stage 07: Compliance

Assemble the application, check every checklist item, and export to PDF and Word only after all items pass.

## Inputs

| Source | File/Location | Section/Scope | Why |
|--------|--------------|---------------|-----|
| Previous stage | `../01-requirements/output/[slug]-requirements-checklist.md` | Full file | Every item to check |
| Previous stage | `../03-narrative/output/[slug]-project-narrative.md` | Full file | Assemble and check |
| Previous stage | `../04-budget/output/[slug]-budget.md` | Full file | Assemble and check |
| Previous stage | `../05-evaluation/output/[slug]-evaluation-plan.md` | Full file | Assemble and check |
| Previous stage (optional) | `../06-support-letter/output/[slug]-support-letters.md` | Full file, only if the checklist says a letter is requested | Assemble and check |
| Shared context | `../../shared/organization-profile.md` | Organization name and board chair fields | Cover and signature block |
| Stage reference | `references/libreoffice-setup.md` | Full file | Export commands and verification |

## Process

1. Assemble the application in the funder's required section order. Add a signature block with the "Board Chair Name" and "Board Chair Title" fields from the organization profile.
2. Check every checklist item:
   - sections present;
   - word limits;
   - budget cap;
   - attachments;
   - support letters (if required);
   - deadline not passed (compare with today's date).
3. Write the compliance report with pass or fail per item and a fix for each failure.
4. **[Checkpoint]** If any item fails, present the failures. The human fixes upstream files or approves fixes, then repeat from step 1.
5. Once all items pass, export `[slug]-application.md` to PDF and .docx with LibreOffice.
6. Run the audit.

## Checkpoints

| After Step | Agent Presents | Human Decides |
|------------|---------------|---------------|
| 3 | Compliance report | Fix failures, or confirm all pass and approve export |

## Audit

| Check | Pass Condition |
|-------|---------------|
| All items pass | Every checklist item is marked pass |
| No early export | No PDF or .docx exists while any item fails |
| Signature | Board chair name and title appear in the signature block |
| Deadline | Deadline is stated in the report and is not past |
| Export | PDF and .docx exist and open |

## Outputs

| Artifact | Location | Format |
|----------|----------|--------|
| Compliance report | `output/[slug]-compliance-report.md` | Table: Checklist Item, Status, Fix |
| Application | `output/[slug]-application.md` | Assembled application in required section order |
| Application PDF | `output/[slug]-application.pdf` | LibreOffice export |
| Application Word | `output/[slug]-application.docx` | LibreOffice export |
</file>

<file path="community-grants/stages/07-compliance/output/.gitkeep">
</file>

<file path="community-grants/stages/07-compliance/references/libreoffice-setup.md">
# LibreOffice Setup and Export

LibreOffice is required for stage 07 export. It runs headless through `soffice`.

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