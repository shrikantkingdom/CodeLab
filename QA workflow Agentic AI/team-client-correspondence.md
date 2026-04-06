# Team Context: Client Correspondence

> Load this file alongside `QA promptbook.md` when running the QA workflow for the Client Correspondence team.

---

## Business Overview

The **Client Correspondence** product manages the generation, personalisation, and delivery of all non-transactional communications sent to clients — including welcome letters, regulatory notices, product change notifications, marketing opt-in/opt-out acknowledgements, and compliance disclosures.

Core responsibilities:
- Template-driven letter and notice generation (PDF + HTML)
- Personalisation engine (merge client data into templates)
- Multi-channel delivery: postal print queue, email, secure portal, SMS
- Bulk broadcast campaigns (regulatory notices, product updates)
- Delivery tracking, audit trail, and suppression list management
- GDPR / marketing preference enforcement

---

## Application Architecture

### Services Layer (Backend)

| Service | Role |
|---|---|
| `correspondence-generator` | Template rendering and PDF/HTML generation |
| `personalisation-engine` | Merges client profile data into templates |
| `correspondence-delivery` | Routes letters to postal, email, portal, or SMS channels |
| `template-management` | Template CRUD, versioning, and approval workflow |
| `suppression-service` | Manages opt-out, GDPR suppression, and do-not-contact lists |
| `audit-trail` | Immutable log of every correspondence sent |
| `client-profile-service` | Client data provider (upstream dependency) |

- **Stack:** Java 17, Spring Boot 3.x, REST APIs
- **Messaging:** Apache Kafka (correspondence dispatch events)
- **Database:** PostgreSQL (correspondence metadata, audit), S3 (rendered PDFs/HTML)
- **Print Queue:** Integration with third-party print vendor API (async)
- **Auth:** OAuth 2.0 / JWT

### UI Layer (Frontend)

- **Stack:** React 18, TypeScript
- **Key screens:** Correspondence history, letter preview, template manager, bulk broadcast, delivery status, suppression list viewer, audit log
- **State management:** Redux Toolkit

---

## Key Links

| Resource | URL |
|---|---|
| Jira Board | https://shrikantpatil.atlassian.net/jira/software/projects/CORCX/boards/1 |
| Jira Project Key | `CORCX` |
| Services App Repo | https://github.com/shrikantkingdom/client-correspondence |
| UI App Repo | https://github.com/shrikantkingdom/correspondence-ui |
| Template Repo | https://github.com/shrikantkingdom/correspondence-templates |
| Automation Repo | https://github.com/shrikantkingdom/playwright_project |
| Confluence (Docs) | https://shrikantpatil.atlassian.net/wiki/spaces/CORCX |
| Monitoring Dashboard | https://grafana.internal/d/correspondence-overview |
| Delivery Status Dashboard | https://grafana.internal/d/correspondence-delivery |
| CI/CD Pipeline | https://github.com/shrikantkingdom/client-correspondence/actions |

---

## Jira Configuration

### Custom Fields (Client Correspondence-specific)

| Field | Expected Values | When Required |
|---|---|---|
| `Correspondence Type` | Welcome / Regulatory Notice / Product Change / Marketing / Compliance Disclosure | Always |
| `Delivery Channel` | Email / Postal / Portal / SMS / All | Always |
| `Regulatory Scope` | GDPR / FCA / PSD2 / None | If correspondence is legally mandated or contains opt-out logic |
| `Bulk Broadcast` | Yes / No | If ticket involves sending to > 1,000 clients |
| `Template Change` | Yes / No | If letter/notice template content or layout is modified |
| `Risk Level` | Low / Medium / High | High if GDPR suppression, opt-out, or audit trail logic is affected |
| `Audit Impact` | Yes / No | If the immutable audit log is affected |

### Labels to Apply

- `correspondence` — always
- `regulatory` — any GDPR, FCA, or PSD2 scope
- `template` — if template content or versioning changes
- `bulk` — if broadcast or bulk processing is involved
- `suppression` — if opt-out or suppression list logic changes
- `audit` — if audit trail or delivery tracking changes

### Components

- `Backend`, `Frontend`, `Templates`, `Delivery`, `Suppression`, `Audit`

---

## Automation Framework (Playwright + Cucumber)

### Directory Structure in Automation Repo

```
playwright_project/
├── features/
│   └── correspondence/             ← All Correspondence feature files
│       ├── letter_generation.feature
│       ├── template_management.feature
│       ├── bulk_broadcast.feature
│       ├── delivery_tracking.feature
│       └── suppression_list.feature
├── steps/
│   └── correspondence/             ← Step definitions
├── pages/
│   └── correspondence/             ← Page objects
└── test-data/
    └── correspondence/             ← Template samples, client profile stubs
```

### Naming Conventions

- Feature files: `snake_case.feature`
- Step definitions: `snake_case_steps.ts`
- Page objects: `PascalCasePage.ts`
- Tags: `@correspondence`, `@smoke`, `@regression`, `@template`, `@bulk`, `@suppression`, `@gdpr`

### Existing Reusable Steps (Common)

- `I am logged in as {string}` — authentication
- `I navigate to the Correspondence history page` — navigation
- `I search for correspondence by client ID {string}` — search
- `I preview the latest letter for client {string}` — preview action
- `I check the delivery status for correspondence {string}` — delivery status check

---

## Key Business Rules & QA Focus Areas

These are experienced-based rules that are not always documented in Jira:

1. **GDPR suppression is absolute** — If a client is on the suppression list, NO correspondence must be generated or delivered, regardless of correspondence type. Even regulatory notices must be checked against suppression (only court-ordered communications bypass this). This rule has the highest compliance risk.
2. **Template versioning lock** — Once a template is approved and in use for a live correspondence, it must be versioned. The existing version must not be modified in-place; a new version must be created. Changes to in-use templates that bypass versioning are a compliance violation.
3. **Postal queue cut-off** — The print vendor API has a 3pm GMT daily cut-off. Correspondence submitted after cut-off is batched to the following business day. Tests that check delivery date must account for this. Do not test postal SLA expectations with same-day times.
4. **Personalisation null safety** — If a client profile field used in a template is null (e.g., preferred name, account number), the letter must fall back to a safe default (e.g., "Valued Client"). A null value must never appear in the rendered letter.
5. **Bulk broadcast throttling** — Bulk broadcasts to > 10,000 clients are throttled to 1,000/minute to protect downstream services. Tests for bulk jobs must validate that the throttle is respected and that the job completes correctly across batches.
6. **Audit trail immutability** — Audit log records must never be updated or deleted, only inserted. Any code change that adds UPDATE or DELETE to the audit schema must be flagged and rejected.
7. **Duplicate dispatch prevention** — If the same correspondence (same type, same client, same effective date) is triggered twice within 24 hours (e.g., due to a retry), only one delivery must occur. Test idempotency keys on all retry paths.
8. **Opt-out confirmation** — When a client opts out of marketing, an opt-out confirmation letter must be sent via the client's registered email — even if marketing email is suppressed. This is a legal requirement.
9. **HTML vs PDF consistency** — The email HTML version and the portal PDF version of the same letter must be functionally identical (same content, same dates, same figures). Visual difference is acceptable, content difference is not.

---

## QA Focus Areas by Ticket Type

| Ticket touches... | Focus on... |
|---|---|
| Template content / layout | Versioning, null personalisation, HTML vs PDF parity |
| Delivery routing | Channel selection logic, postal cut-off, retry handling |
| Suppression / opt-out | Absolute suppression check, opt-out confirmation letter |
| Bulk broadcast | Throttling, batch completeness, duplicate prevention |
| Audit trail | Insert-only enforcement, completeness per delivery event |
| GDPR / regulatory | Suppression bypass rules, consent tracking, data minimisation |
| Template manager UI | Approval workflow, version history, preview rendering |

---

## Test Environments

| Env | Purpose | URL |
|---|---|---|
| Dev | Active development | https://dev.correspondence.internal |
| QA | Test execution | https://qa.correspondence.internal |
| UAT | User acceptance | https://uat.correspondence.internal |
| Print Vendor Sandbox | Postal integration testing | https://printvendor-sandbox.internal |

---

## Team Contacts

| Role | Name / Handle |
|---|---|
| QA Lead | @qa-lead-correspondence |
| Dev Lead | @dev-lead-correspondence |
| Scrum Master | @scrum-master |
| PR Reviewers | @dev-lead-correspondence, @qa-lead-correspondence |
| Compliance Reviewer | @compliance-team (tag on any GDPR / regulatory tickets) |
| Slack Channel | `#team-correspondence-alerts` |

---

## Glossary

| Term | Meaning |
|---|---|
| Correspondence | Any document or message sent to a client (letter, notice, email) |
| Template | A reusable document structure with placeholders for personalisation |
| Personalisation | Replacing template placeholders with actual client-specific data |
| Suppression | A flag preventing any or specific types of correspondence being sent to a client |
| Postal Queue | The batch sent to the print vendor for physical letter dispatch |
| Bulk Broadcast | Sending the same correspondence type to a large group of clients simultaneously |
| Audit Trail | An immutable log of every correspondence generated and delivered |
| Opt-out | A client's instruction to stop receiving a category of correspondence |
| GDPR | General Data Protection Regulation — governs client data use and consent |
| FCA | Financial Conduct Authority — regulatory body whose rules apply to many notices |
