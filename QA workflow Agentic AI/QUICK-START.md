# QA Workflow — Quick Start

> One file. Three steps. Zero setup beyond loading your context files.

---

## The Prompt (Copy → Fill in → Run)

```
Using the QA workflow in #file:QA promptbook.md and team context in #file:team-[TEAM].md,
run the complete QA workflow for [TICKET / VERSION].
```

That's it. Replace `[TEAM]` and `[TICKET or VERSION]` — done.

---

## Fill-in Reference

| Placeholder | Replace with | Example |
|---|---|---|
| `[TEAM]` | Your team's context file name | `statements` → `team-statements.md` |
| `[TICKET]` | Jira ticket ID | `SCRUM-123` |
| `[VERSION]` | Jira release version label | `v2.4.1` |

---

## Ready-to-Use Examples

### Single ticket — Statements team
```
Using the QA workflow in #file:QA promptbook.md and team context in #file:team-statements.md,
run the complete QA workflow for SCRUM-123.
```

### Release version — Confirms team
```
Using the QA workflow in #file:QA promptbook.md and team context in #file:team-confirms.md,
run the complete QA workflow for version v3.1.0.
```

### Single ticket — Client Correspondence team
```
Using the QA workflow in #file:QA promptbook.md and team context in #file:team-client-correspondence.md,
run the complete QA workflow for CORCX-88.
```

---

## Adding Extra Instructions (the `+notes` block)

Use `+notes` when you have one-time context that isn't in any file:
- Domain knowledge from experience
- A specific Jira field value that must be set for this ticket
- An area that historically has bugs (worth extra test focus)
- A logic rule that is obvious to you but not written anywhere
- Something that changed in this sprint but hasn't been documented yet

### Format

```
Using the QA workflow in #file:QA promptbook.md and team context in #file:team-[TEAM].md,
run the complete QA workflow for [TICKET / VERSION].

+notes
- [Your instruction 1]
- [Your instruction 2]
- [Your instruction 3]
```

### Examples of good `+notes`

```
+notes
- Focus test generation on the PDF rendering path — bugs appear there most often
- Set Jira field "Risk Level" to High — this ticket changes the batch scheduler
- The new field `effectiveDate` is stored as UTC but displayed in the client's local timezone — test both sides of midnight carefully
- Rule 3 from team-statements.md applies here (batch idempotency) — make sure it's covered
- Ignore changes to the `LegacyExportService` — it is deprecated and will be removed next sprint
```

```
+notes
- Regulatory label must be added to this ticket — the AC mentions MiFID II reporting
- MT515 message format is being changed — always test with the SWIFT sandbox environment, not just unit mocks
- Counterparty BIC "TESTGB2L" is available in the SWIFT sandbox for testing
- PM confirmed that partial match should still create an exception at 50% tolerance, not 60% — the ticket description has an error
```

```
+notes
- GDPR suppression check is mandatory — client 87654 is on the suppression list; use them to test suppression enforcement
- The template version was bumped to v4 this sprint — ensure all tests reference v4, not v3
- Bulk broadcast limit is being raised from 10,000 to 25,000 this sprint — add a test at the new upper boundary
- Do not test postal channel delivery SLA — print vendor integration is down in QA environment until next week
```

---

## What the Agent Does with Your Prompt

| Input | What happens |
|---|---|
| `#file:QA promptbook.md` | Loads the 7-stage workflow instructions |
| `#file:team-[TEAM].md` | Loads team-specific repos, Jira config, business rules, contacts |
| `TICKET / VERSION` | Fetches Jira data and starts the workflow |
| `+notes` lines | Applied as session overrides — extend or replace defaults for this run only |

---

## Multi-ticket Run

Pass a comma-separated list or a version label. The agent processes each ticket in sequence and produces a consolidated report.

```
Using the QA workflow in #file:QA promptbook.md and team context in #file:team-statements.md,
run the complete QA workflow for SCRUM-101, SCRUM-102, SCRUM-103.
```

```
Using the QA workflow in #file:QA promptbook.md and team context in #file:team-confirms.md,
run the complete QA workflow for version v3.2.0.
```

---

## New Team Onboarding

1. Copy `team-template.md`
2. Rename to `team-<your-team-name>.md`
3. Fill in all sections (check the checklist at the bottom of the template)
4. Use the prompt above with your new file name

No other configuration needed.

---

## Cheat Sheet

```
# Minimal
Using the QA workflow in #file:QA promptbook.md and team context in #file:team-statements.md,
run the complete QA workflow for SCRUM-99.

# With notes
Using the QA workflow in #file:QA promptbook.md and team context in #file:team-confirms.md,
run the complete QA workflow for CONF-45.

+notes
- This ticket changes SWIFT delivery — test with MT515 format specifically
- Set "Risk Level" = High in Jira

# By version (multiple tickets)
Using the QA workflow in #file:QA promptbook.md and team context in #file:team-client-correspondence.md,
run the complete QA workflow for version v2.1.0.
```
