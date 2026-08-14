# Handoff contract

Create a concise Markdown handoff only when an explicit cross-context
provenance or reproducibility consumer cannot use the Issue, PR, CI, review, or
project-local result directly. Do not create one for every bounded execution or
duplicate natural evidence owners.

```markdown
---
id: HANDOFF-<PROJECT>-YYYYMMDD-NNN
work_unit: <Issue, PR, or justified PLAN reference>
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
