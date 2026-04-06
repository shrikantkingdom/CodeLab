# Jira & Agile

## Key Concepts
- **Epic**: Large body of work.
- **Story**: Feature from user perspective.
- **Task**: Technical work.
- **Bug**: Defect.
- **Sprint**: Time‑boxed iteration (usually 2 weeks).

## JQL Examples
```
project = "MYPROJ" AND status = "In Progress"
assignee = currentUser() AND sprint in openSprints()
```

## Agile Ceremonies
- Daily Stand‑up
- Sprint Planning
- Sprint Review / Demo
- Retrospective
