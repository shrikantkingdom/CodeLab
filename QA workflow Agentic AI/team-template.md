# Team Context: [TEAM NAME HERE]

> **How to use this template:**
> 1. Copy this file and rename it `team-<your-team-name>.md`
> 2. Fill in every section below — replace all `[placeholder]` values
> 3. Delete any section that is not applicable to your team
> 4. Keep business rules and QA focus areas up to date — these are the most valuable parts
>
> Load this file alongside `QA promptbook.md` when running the QA workflow.

---

## Business Overview

> Describe what this team's application does. 2–5 sentences is enough.
> Include: what problem it solves, who the end users are, and what the key outputs/deliverables are.

[TEAM NAME] is responsible for [describe the application's purpose].

Core responsibilities:
- [Responsibility 1]
- [Responsibility 2]
- [Responsibility 3]
- [Add more as needed]

---

## Application Architecture

### Services Layer (Backend)

| Service | Role |
|---|---|
| `[service-name]` | [What it does] |
| `[service-name]` | [What it does] |
| `[upstream-dependency]` | [What data/events it provides] |

- **Stack:** [e.g., Java 17 / Spring Boot 3.x / Node.js 20 / Python 3.12]
- **Messaging:** [e.g., Kafka / RabbitMQ / SQS / None]
- **Database:** [e.g., PostgreSQL / MySQL / DynamoDB / Oracle]
- **Auth:** [e.g., OAuth 2.0 / JWT / SAML]

### UI Layer (Frontend)

- **Stack:** [e.g., React 18 / Angular 17 / Vue 3]
- **Key screens:** [List the main UI screens or pages]
- **State management:** [e.g., Redux / NgRx / Zustand / None]

---

## Key Links

| Resource | URL |
|---|---|
| Jira Board | [URL] |
| Jira Project Key | `[PROJ-KEY]` |
| Services App Repo | [GitHub/GitLab URL] |
| UI App Repo | [GitHub/GitLab URL] |
| Automation Repo | [GitHub/GitLab URL] |
| Confluence / Docs | [URL] |
| Monitoring Dashboard | [Grafana/Datadog/etc. URL] |
| CI/CD Pipeline | [GitHub Actions / Jenkins / etc. URL] |

> Add more links rows as needed (e.g., separate dashboards, sandbox environments, design specs).

---

## Jira Configuration

### Custom Fields (Team-specific)

> List any Jira fields that are specific to your team's project — not standard fields.
> Include what values are valid and when the field is required.

| Field | Expected Values | When Required |
|---|---|---|
| `[Field Name]` | [Value 1 / Value 2 / Value 3] | [Always / When X applies] |
| `[Field Name]` | [Value 1 / Value 2] | [Always / When Y applies] |

### Labels to Apply

- `[team-name]` — always
- `[label]` — when [condition]
- `[label]` — when [condition]

### Components

- [Component 1], [Component 2], [Component 3]

---

## Automation Framework (Playwright + Cucumber)

### Directory Structure in Automation Repo

> Replace `[team-name]` with the actual subfolder name used in the repo.

```
playwright_project/
├── features/
│   └── [team-name]/           ← Feature files for this team
│       └── [example].feature
├── steps/
│   └── [team-name]/           ← Step definitions
├── pages/
│   └── [team-name]/           ← Page objects
└── test-data/
    └── [team-name]/           ← Test data files
```

### Naming Conventions

- Feature files: `snake_case.feature`
- Step definitions: `snake_case_steps.ts`
- Page objects: `PascalCasePage.ts`
- Tags: `@[team-name]`, `@smoke`, `@regression`, `@[feature-tag]`

### Existing Reusable Steps

> List the most commonly reused step definitions your team already has.
> This helps the AI avoid creating duplicates.

- `I am logged in as {string}` — standard auth step (shared)
- `[Step description]` — [what it does]
- `[Step description]` — [what it does]

---

## Key Business Rules & QA Focus Areas

> **This is the most important section.** Document rules and knowledge that:
> - Are not written in Jira or Confluence
> - Come from experience or past bugs
> - Are legally or compliance mandated
> - Catch subtle bugs that automated checks miss
>
> Number each rule so it can be referenced in `+notes` blocks.

1. **[Rule name]** — [Describe the rule and why it matters. Include any edge cases or past failures it relates to.]
2. **[Rule name]** — [Description]
3. **[Rule name]** — [Description]
4. **[Add more as you discover them]**

---

## QA Focus Areas by Ticket Type

> Map ticket characteristics to which area of the application deserves the most scrutiny.

| Ticket touches... | Focus on... |
|---|---|
| [Feature area] | [Specific test concerns] |
| [Feature area] | [Specific test concerns] |
| [Feature area] | [Specific test concerns] |

---

## Test Environments

| Env | Purpose | URL |
|---|---|---|
| Dev | Active development | [URL] |
| QA | Test execution | [URL] |
| UAT | User acceptance | [URL] |

---

## Team Contacts

| Role | Name / Handle |
|---|---|
| QA Lead | @[handle] |
| Dev Lead | @[handle] |
| Scrum Master | @[handle] |
| PR Reviewers | @[handle], @[handle] |
| Slack Channel | `#[channel-name]` |

> Add a Compliance Reviewer row if your team handles regulatory or GDPR concerns.

---

## Glossary

> Define domain-specific terms that the AI might not know but will encounter in Jira ticket descriptions and acceptance criteria.

| Term | Meaning |
|---|---|
| [Term] | [Definition] |
| [Term] | [Definition] |
| [Term] | [Definition] |

---

## Checklist Before First Use

- [ ] All `[placeholder]` values replaced
- [ ] Jira project key confirmed
- [ ] At least one service repo link added
- [ ] Automation repo path and naming conventions confirmed
- [ ] At least 3 business rules documented under "Key Business Rules"
- [ ] Team contacts and Slack channel populated
- [ ] File renamed to `team-<your-team-name>.md`
