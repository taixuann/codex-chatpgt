---
kind: codex.session-artifact.v1
artifact: tasks
session_id: 20260826_franky-structure_001
status: in_progress
provenance:
  source_commit: 67d21cc3bf14a4121e064d8edb3f999c830a9307
  observed_at: '2026-08-26T16:30:00+07:00'
  recorded_by: franky
upstream:
  - plan.md
  - franky.ticket.yaml
downstream:
  - franky.results.yaml
---

# Tasks

Session: `20260826_franky-structure_001`

- [x] Inspect current agents, docs, manifests, and ops ownership.
  - Acceptance: current files and dirty-state conflicts recorded in context.
  - Verify: scoped `git status`, `rg`, and file inspection.
  - Files: `agents/`, `documentation/`, `manifests/`, `ops/`
- [x] Add concise manifests-versus-ops ownership guidance.
  - Acceptance: docs state declarative versus executable responsibilities.
  - Verify: inspect `documentation/AGENT-BOUNDARIES.md`.
  - Files: `documentation/AGENT-BOUNDARIES.md`
- [x] Preserve KISS structure and archive boundaries.
  - Acceptance: no mega-manifest/index/router/workflow engine added; archive
    moves remain separately reviewable.
  - Verify: scoped diff and file inventory.
  - Files: `manifests/`, `ops/`, `documentation/archive/`
- [x] Run deterministic validation and return evidence for independent review.
  - Acceptance: validators/tests report pass or explicit limitation.
  - Verify: commands listed in `franky.results.yaml`.
  - Files: packet records
