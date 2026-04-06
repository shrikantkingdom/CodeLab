# Team Context: Confirms

> Load this file alongside `QA promptbook.md` when running the QA workflow for the Confirms team.

---

## Business Overview

The **Confirms** product generates and delivers trade confirmation documents to clients following executed trades. It supports equities, fixed income, derivatives, and FX instruments. Confirms are legally binding documents and must be delivered within regulatory time windows.

Core responsibilities:
- Generation of trade confirmation documents (PDF + structured data)
- Real-time and end-of-day delivery to clients and counterparties
- Regulatory reporting integration (MiFID II, EMIR, Dodd-Frank)
- Affirmation and matching with counterparty confirmations
- Dispute and exception management workflow

---

## Application Architecture

### Services Layer (Backend)

| Service | Role |
|---|---|
| `confirms-generator` | Core confirm document generation engine |
| `confirms-matching` | Counterparty affirmation and matching logic |
| `confirms-delivery` | Multi-channel delivery (SWIFT, email, portal, FTP) |
| `confirms-exceptions` | Exception queue management and dispute workflow |
| `trade-data-service` | Trade data provider (upstream — real-time feed) |
| `regulatory-reporter` | Sends reports to regulatory bodies (MiFID II, EMIR) |

- **Stack:** Java 17, Spring Boot 3.x, REST + event-driven
- **Messaging:** Apache Kafka (trade events, delivery status)
- **Database:** PostgreSQL (confirm metadata), Oracle (trade reference data)
- **Auth:** OAuth 2.0 / JWT; SWIFT credentials managed via HSM

### UI Layer (Frontend)

- **Stack:** React 18, TypeScript
- **Key screens:** Confirms dashboard, confirms search, confirm detail view, exception queue, matching status, delivery status
- **State management:** Redux Toolkit

---

## Key Links

| Resource | URL |
|---|---|
| Jira Board | https://shrikantpatil.atlassian.net/jira/software/projects/CONF/boards/1 |
| Jira Project Key | `CONF` |
| Services App Repo | https://github.com/shrikantkingdom/confirms |
| UI App Repo | https://github.com/shrikantkingdom/confirms-ui |
| Automation Repo | https://github.com/shrikantkingdom/playwright_project |
| Confluence (Docs) | https://shrikantpatil.atlassian.net/wiki/spaces/CONF |
| Monitoring Dashboard | https://grafana.internal/d/confirms-overview |
| Exception Queue Dashboard | https://grafana.internal/d/confirms-exceptions |
| CI/CD Pipeline | https://github.com/shrikantkingdom/confirms/actions |

---

## Jira Configuration

### Custom Fields (Confirms-specific)

| Field | Expected Values | When Required |
|---|---|---|
| `Instrument Type` | Equity / Fixed Income / Derivative / FX / All | Always |
| `Delivery Channel` | SWIFT / Email / Portal / FTP / All | Always |
| `Regulatory Scope` | MiFID II / EMIR / Dodd-Frank / None | If ticket touches regulatory reporting |
| `Risk Level` | Low / Medium / High / Critical | High if matching logic or SWIFT delivery is changed |
| `Exception Impact` | Yes / No | If changes affect the exception or dispute workflow |
| `STP Flag` | Yes / No | Flag if ticket changes straight-through processing logic |

### Labels to Apply

- `confirms` — always
- `regulatory` — any MiFID II, EMIR, or Dodd-Frank scope
- `swift` — if SWIFT delivery path is touched
- `matching` — if affirmation or counterparty matching logic changes
- `exception` — if the exception/dispute workflow is affected

### Components

- `Backend`, `Frontend`, `Matching`, `Delivery`, `Regulatory`, `Exceptions`

---

## Automation Framework (Playwright + Cucumber)

### Directory Structure in Automation Repo

```
playwright_project/
├── features/
│   └── confirms/             ← All Confirms feature files go here
│       ├── confirm_search.feature
│       ├── confirm_detail.feature
│       ├── exception_queue.feature
│       └── matching_status.feature
├── steps/
│   └── confirms/             ← Step definitions
├── pages/
│   └── confirms/             ← Page objects
└── test-data/
    └── confirms/             ← Trade data stubs, SWIFT message samples
```

### Naming Conventions

- Feature files: `snake_case.feature`
- Step definitions: `snake_case_steps.ts`
- Page objects: `PascalCasePage.ts`
- Tags: `@confirms`, `@smoke`, `@regression`, `@swift`, `@matching`, `@exceptions`

### Existing Reusable Steps (Common)

- `I am logged in as {string}` — authentication
- `I navigate to the Confirms dashboard` — navigation
- `I search for confirm by trade ID {string}` — search action
- `I filter confirms by instrument type {string}` — instrument filter
- `I view the exception queue` — exceptions navigation

---

## Key Business Rules & QA Focus Areas

These are experienced-based rules that are not always documented in Jira:

1. **Regulatory delivery window** — Confirms must be delivered within T+1 for equities (MiFID II). Any change to the delivery pipeline must be tested against this SLA. Test with late-arriving trade events.
2. **SWIFT message format** — MT515/MT518 formats are strictly validated by recipient banks. A single field length violation causes the entire delivery to fail silently. Always test SWIFT output format when the delivery service changes.
3. **Matching tolerance** — Price matching has a configurable tolerance (default ±0.0001). Do not hardcode this value in tests — use the config-driven value.
4. **Exception escalation** — If a confirm remains unmatched for > 4 hours, it auto-escalates to the exception queue. This timer-based logic is frequently broken by timezone configuration changes.
5. **Regulatory reporting idempotency** — Regulatory reports (EMIR/MiFID II) must not be re-sent on system restart. Check idempotency keys whenever the reporter service is changed.
6. **Cancelled trade handling** — A cancellation event must suppress the confirm generation for that trade. If a confirm was already delivered, a cancellation notice must be generated and delivered through all the same channels.
7. **FX confirm rounding** — FX notional amounts must be rounded to the currency's standard decimal places (e.g., JPY = 0 decimals, USD = 2). This has been a source of counterparty disputes.
8. **Counterparty BIC validation** — BIC codes must be validated against the internal reference data store before SWIFT dispatch. Stale reference data has caused failed deliveries in the past.

---

## QA Focus Areas by Ticket Type

| Ticket touches... | Focus on... |
|---|---|
| Document generation | Format correctness, field completeness, instrument-specific layouts |
| SWIFT delivery | Message format (MT515/MT518), BIC validation, failure handling |
| Matching logic | Tolerance values, unmatched escalation, partial match scenarios |
| Exception queue | Auto-escalation timer, manual override, resolution workflow |
| Regulatory reporting | Idempotency, submission window, report schema validation |
| Cancellation handling | Suppression of original confirm, cancellation notice delivery |
| UI search / filter | Trade ID lookup, date range, instrument type, status filters |

---

## Test Environments

| Env | Purpose | URL |
|---|---|---|
| Dev | Active development | https://dev.confirms.internal |
| QA | Test execution | https://qa.confirms.internal |
| UAT | User acceptance | https://uat.confirms.internal |
| SWIFT Sandbox | SWIFT integration testing | https://swift-sandbox.internal |

---

## Team Contacts

| Role | Name / Handle |
|---|---|
| QA Lead | @qa-lead-confirms |
| Dev Lead | @dev-lead-confirms |
| Scrum Master | @scrum-master |
| PR Reviewers | @dev-lead-confirms, @qa-lead-confirms |
| Slack Channel | `#team-confirms-alerts` |

---

## Glossary

| Term | Meaning |
|---|---|
| Trade Confirm | A legally binding document confirming the terms of an executed trade |
| Affirmation | Client's acknowledgement that the confirm matches their trade record |
| Matching | Automated comparison of client and counterparty confirm details |
| Exception | A confirm that failed matching or delivery and requires manual intervention |
| STP | Straight-Through Processing — automated end-to-end without manual intervention |
| MT515 / MT518 | SWIFT message types for trade confirmation and settlement instruction |
| EMIR | European Market Infrastructure Regulation — requires trade reporting |
| MiFID II | Markets in Financial Instruments Directive — regulatory reporting framework |
