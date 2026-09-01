# Legacy handoff records

This directory is retained for historical handoff records and compatibility.
New bounded execution records belong under
`documentation/sessions/<session-id>/`; do not delete or relocate an existing
handoff until its provenance and consumers are reconciled.

## Handoff contract

Create one concise Markdown handoff for each completed bounded execution:

```markdown
---
id: HANDOFF-<PROJECT>-YYYYMMDD-NNN
plan: <plan id or path>
status: completed | partial | blocked
repository: <repository>
branch: <branch>
commit: <sha>
---

# Objective

# Changes

# Validation

# Decisions and discoveries

# Deviations

# Unresolved issues

# Recommended next step
```

Handoffs summarize evidence; they do not replace canonical `CURRENT.md` or
`DECISIONS.md`, and they must not contain credentials or runtime state.
