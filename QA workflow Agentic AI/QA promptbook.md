# Agentic AI QA Workflow — Generic Instructions

> **How to use:** Load this file + your team's context file (e.g., `team-statements.md`) when running the QA workflow.
> See `QUICK-START.md` for the runnable prompt and how to inject additional one-time instructions.

---

## Objective

Automate end-to-end QA analysis for any team's Jira tickets or release versions:

1. Extract & validate Jira ticket quality
2. Verify code alignment against requirements
3. Generate test cases (manual + BDD)
4. Create automation artifacts and raise a PR
5. Produce a unified QA report

---

## Prerequisites

- VS Code with GitHub Copilot (Agent Mode enabled)
- MCP servers configured: **Jira**, **GitHub**, **Playwright**
- Team context file loaded (see `team-template.md` to create one)

---

## Stage 1 — Jira Data Extraction

**Trigger:** Jira ticket ID(s) or release version label.

Connect to the Jira MCP server and extract:

| Field | Required |
|---|---|
| Summary | Yes |
| Description | Yes |
| Acceptance Criteria | Yes |
| Priority | Yes |
| Assignee | Yes |
| Labels / Components | Yes |
| Linked Commits / PRs | If available |
| Team-specific custom fields | Per team context file |

> The Jira project key, board URL, and any custom fields are defined in the team context file.

---

## Stage 2 — Jira Quality Validation & Scoring

Score each ticket 0–100 using the weighted model below.

### Scoring Weights

| Parameter | Weight |
|---|---|
| Description quality | 25% |
| Acceptance criteria completeness | 30% |
| Field completeness | 20% |
| Clarity / no ambiguity | 15% |
| Traceability (linked commits/PRs) | 10% |

### Validation Checks

- All mandatory fields are populated
- Acceptance criteria are testable and unambiguous
- No contradictions between description and AC
- Business context is present or inferable from team context file
- Custom field rules from the team context file are applied

### Output

- Quality score with breakdown
- List of missing or weak fields
- Improvement suggestions (comment on Jira if score < 70)

---

## Stage 3 — Code Alignment Verification

Pull commit/PR links from the Jira ticket. Fetch diffs via GitHub MCP.

### Validate

- Code implements the described functionality
- All acceptance criteria have corresponding code coverage
- No unrelated changes (scope creep)
- Architecture patterns match those described in team context file

### Output

| Status | Meaning |
|---|---|
| ✅ Aligned | Code matches requirements |
| ⚠️ Partial | Minor gaps or unclear areas |
| ❌ Misaligned | Significant discrepancy — flag to dev lead |

> App repo links and service/UI architecture are defined in the team context file.

---

## Stage 4 — Test Case Generation

Generate full coverage across all scenario types.

### Test Types

- Happy path (primary flows)
- Negative / invalid input scenarios
- Edge cases (boundary values, empty/null states, concurrent access)
- Regression impact (related existing functionality)

### Output Format — Xray-compatible Table

| Test ID | Scenario | Pre-conditions | Steps | Expected Result | Type |
|---|---|---|---|---|---|
| TC-001 | | | | | Happy Path |
| TC-002 | | | | | Negative |
| TC-003 | | | | | Edge Case |

> Upload via Jira MCP or Xray API. Team-specific components/labels to attach are in the team context file.

---

## Stage 5 — BDD + Automation Artifacts

### Gherkin Feature File

```gherkin
Feature: <Feature Name from Jira summary>
  As a <user role>
  I want <capability>
  So that <business value>

  Background:
    Given <common precondition>

  Scenario: <Happy path scenario>
    Given ...
    When ...
    Then ...

  Scenario: <Negative scenario>
    Given ...
    When ...
    Then ...
```

### Step Definitions

- Scan existing automation repo for reusable steps before creating new ones
- Follow the naming conventions defined in the team context file
- Avoid duplicate step definitions (search before creating)

### Page Objects / Selectors (UI tests)

- Reference existing page objects from the automation repo
- Create new ones only when genuinely missing

> Automation repo path and framework conventions are in the team context file.

---

## Stage 6 — Automation Repo Integration

1. Create branch: `qa/JIRA-<ticket-id>-<short-description>`
2. Add: feature file, step definitions, any new page objects
3. Run a dry-check for duplicate steps
4. Raise a Pull Request with:
   - Title: `[QA] JIRA-<id>: <summary>`
   - Body: linked Jira ticket, generated test summary, reviewer list from team context file

---

## Stage 7 — QA Report Generation

Generate an HTML report saved locally and attached to the Jira ticket.

### Report Sections

1. **Jira Summary** — ticket details, version, team
2. **Quality Score** — overall + per-parameter breakdown
3. **Validation Issues** — missing fields, ambiguities
4. **Code Alignment** — status matrix per acceptance criterion
5. **Test Coverage** — count by type, coverage gaps
6. **Recommendations** — prioritised action items

### Notifications

Notify (Slack/email) the stakeholders listed in the team context file at report completion.

---

## Additional Instructions (Session Overrides)

When running the workflow you can append a `+notes` block to your prompt for any one-time context that isn't documented anywhere. This is for experiential knowledge, specific Jira field rules, areas to focus on, or business logic only a seasoned engineer would know.

Format:
```
+notes
- <instruction 1>
- <instruction 2>
```

Examples:
- "Add label `Regulatory` if any AC mentions compliance or audit"
- "Focus test generation on the PDF rendering path — bugs historically appear there"
- "Jira field `Risk Level` must be set to High if the ticket touches the pricing engine"
- "Ignore the legacy `v1` endpoints in code alignment — they are deprecated but not yet removed"

These notes override or extend the defaults for this run only. They are **not saved** back to any file.

---

## Feedback Loop

| Trigger | Action |
|---|---|
| Jira score < 70 | Comment on ticket with improvement suggestions |
| Code alignment ❌ | Flag to dev lead via Jira comment |
| Missing AC | Request update from ticket owner |
| Duplicate step definitions found | Warn in PR description |

Human review is mandatory before merging any PR or uploading test cases.

---

## Folder Structure Reference

```
QA workflow Agentic AI/
├── QA promptbook.md              ← This file (generic instructions)
├── QUICK-START.md                ← Runnable prompt + usage guide
├── team-statements.md            ← Statements team context
├── team-confirms.md              ← Confirms team context
├── team-client-correspondence.md ← Client Correspondence team context
└── team-template.md              ← Blank template for new teams
```

---

## FAQ

**Q: How is consistency ensured across teams?**
All teams use the same 7-stage workflow from this file. Team files only add context, they do not change the process.

**Q: Can the workflow handle a full release (multiple tickets)?**
Yes — pass the Jira release version label. The agent processes each ticket in order and consolidates the final report.

**Q: What if code changes are not linked in Jira?**
Stage 3 will flag this and attempt a branch/commit search by ticket ID. If nothing is found, alignment check is skipped with a warning.

**Q: Is human review required?**
Always. The AI produces analysis and artifacts — a QA engineer must review test cases, approve the PR, and make final decisions.
