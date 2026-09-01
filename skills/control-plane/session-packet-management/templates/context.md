---
kind: codex.session-artifact.v1
artifact: context
session_id: 20260826_example-work_001
status: observed
provenance:
  source_commit: uncommitted
  observed_at: '2026-08-26T00:00:00Z'
  recorded_by: argus
upstream:
  - references.yaml
downstream:
  - spec.md
  - plan.md
---

# Context

Session: `20260826_example-work_001`

## Scope and source state

- Repository: `/absolute/repository/path`
- Source commit: `uncommitted`
- Observed at: `2026-08-26T00:00:00Z`
- Recovery agent: `argus`

## Recovered evidence

Record only bounded observations. Link every claim to `references.yaml`.

## Conflicts and unknowns

- None recorded.

## Recommended next inspection

- Confirm the current Issue/PLAN/PR before writing the ticket.
