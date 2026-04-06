# Team Context: Statements

> Load this file alongside `QA promptbook.md` when running the QA workflow for the Statements team.

---

## Business Overview

The **Statements** product generates and delivers periodic account statements to clients. It supports multiple delivery channels (PDF download, email, portal view) and covers a range of account types including savings, current, investment, and loan accounts.

Core responsibilities:
- Generation of statement PDFs from transaction data
- Scheduling and batching of statement runs (monthly, quarterly, ad-hoc)
- Delivery via email, client portal, and file export (CSV/XLSX)
- Archival and retrieval of historical statements
- Regulatory compliance (data retention, format mandates)

---

## Application Architecture

### Services Layer (Backend)

| Service | Role |
|---|---|
| `statement-generator` | Core PDF/CSV generation engine |
| `statement-scheduler` | Batch scheduling and run management |
| `statement-delivery` | Email + portal push logic |
| `statement-archive` | Storage, retrieval, and retention policy |
| `account-data-service` | Transaction data provider (upstream dependency) |

- **Stack:** Java 17, Spring Boot 3.x, REST APIs
- **Messaging:** Apache Kafka (statement run events)
- **Database:** PostgreSQL (statement metadata), S3 (PDF storage)
- **Auth:** OAuth 2.0 / JWT via internal Identity Service

### UI Layer (Frontend)

- **Stack:** React 18, TypeScript
- **Key screens:** Statement list, statement viewer (PDF embed), download, date-range filter, account selector
- **State management:** Redux Toolkit

---

## Key Links

| Resource | URL |
|---|---|
| Jira Board | https://shrikantpatil.atlassian.net/jira/software/projects/SCRUM/boards/1 |
| Jira Project Key | `SCRUM` |
| Services App Repo | https://github.com/shrikantkingdom/statements |
| UI App Repo | https://github.com/shrikantkingdom/sow_ui |
| Automation Repo | https://github.com/shrikantkingdom/playwright_project |
| Confluence (Docs) | https://shrikantpatil.atlassian.net/wiki/spaces/STMT |
| Monitoring Dashboard | https://grafana.internal/d/statements-overview |
| CI/CD Pipeline | https://github.com/shrikantkingdom/statements/actions |
| Test Results (Xray) | https://shrikantpatil.atlassian.net/jira/software/projects/SCRUM/boards/1?selectedIssue=xray |

---

## Jira Configuration

### Custom Fields (Statements-specific)

| Field | Expected Values | When Required |
|---|---|---|
| `Statement Type` | Monthly / Quarterly / Ad-hoc / Tax | Always |
| `Delivery Channel` | Email / Portal / Export / All | Always |
| `Account Type` | Savings / Current / Investment / Loan / All | Always |
| `Regulatory Flag` | Yes / No | If AC mentions compliance, audit, or data retention |
| `Risk Level` | Low / Medium / High | High if changes touch PDF generation or archival |
| `Batch Job Impact` | Yes / No | If changes affect scheduler or batch processing |

### Labels to Apply

- `statements` — always
- `regulatory` — if the ticket has a compliance/audit element
- `pdf-generation` — if the ticket touches PDF layout or content
- `batch` — if scheduler or batch run logic is changed

### Components

- `Backend`, `Frontend`, `Scheduler`, `Archive`, `Delivery`

---

## Automation Framework (Playwright + Cucumber)

### Directory Structure in Automation Repo

```
playwright_project/
├── features/
│   └── statements/           ← All Statements feature files go here
│       ├── statement_list.feature
│       ├── statement_download.feature
│       └── statement_filters.feature
├── steps/
│   └── statements/           ← Step definitions
├── pages/
│   └── statements/           ← Page objects
└── test-data/
    └── statements/           ← Test data files (JSON/CSV)
```

### Naming Conventions

- Feature files: `snake_case.feature`
- Step definitions: `snake_case_steps.ts`
- Page objects: `PascalCasePage.ts`
- Tags: `@statements`, `@smoke`, `@regression`, `@pdf`, `@batch`

### Existing Reusable Steps (Common)

- `I am logged in as {string}` — authentication
- `I navigate to the Statements page` — navigation
- `I select account {string}` — account selector
- `I set date range from {string} to {string}` — date filter
- `I download the PDF for {string}` — download action

---

## Key Business Rules & QA Focus Areas

These are experienced-based rules that are not always documented in Jira:

1. **PDF date range** — Statement PDFs must always include transactions from the first to last day of the period (inclusive). Off-by-one bugs have previously appeared here.
2. **Zero-transaction handling** — If there are no transactions in a period, a "no activity" statement must still be generated, not an error or empty file.
3. **Tax statement format** — Tax statements have a strict column order that is legally mandated. Changes here must always include a regulatory review comment in Jira.
4. **Batch run idempotency** — Re-running a batch for the same period and account must not create duplicate statement records. Always test this edge case.
5. **Archival retention** — Statements older than 7 years should be soft-deleted, not hard-deleted. A hard-delete is a data compliance violation.
6. **PDF vs portal consistency** — The downloaded PDF and the portal-embedded view must be byte-for-byte identical. Bugs have appeared when the embed path cached an older version.
7. **Email delivery failure** — If email delivery fails, the statement must remain accessible on the portal. Never mark the job as failed if only the email step fails.

---

## QA Focus Areas by Ticket Type

| Ticket touches... | Focus on... |
|---|---|
| PDF generation | Layout, column ordering, date ranges, zero-transaction cases |
| Scheduler / batch | Idempotency, re-run safety, job status transitions |
| Email delivery | Retry logic, failure fallback, template rendering |
| Archive / retrieval | Retention dates, soft-delete, search accuracy |
| UI filters | Date boundary handling, account type filtering, pagination |
| Auth / access | Role-based access (client vs admin), token expiry on download |

---

## Test Environments

| Env | Purpose | URL |
|---|---|---|
| Dev | Active development | https://dev.statements.internal |
| QA | Test execution | https://qa.statements.internal |
| UAT | User acceptance | https://uat.statements.internal |

---

## Team Contacts

| Role | Name / Handle |
|---|---|
| QA Lead | @qa-lead-statements |
| Dev Lead | @dev-lead-statements |
| Scrum Master | @scrum-master |
| PR Reviewers | @dev-lead-statements, @qa-lead-statements |
| Slack Channel | `#team-statements-alerts` |

---

## Glossary

| Term | Meaning |
|---|---|
| Statement Run | A scheduled or ad-hoc execution that generates statements for a set of accounts |
| Delivery Channel | The method by which a statement reaches a client (email, portal, export) |
| Tax Statement | End-of-year statement used for tax filing — stricter format requirements |
| Archival | Long-term storage of statements with retention policy enforcement |
| Batch Job | Background job that processes multiple accounts in a single run |
