---
kind: codex.session-artifact.v1
artifact: tasks
session_id: 20260826_franky-skills_001
status: needs_review
provenance:
  source_commit: 67d21cc3bf14a4121e064d8edb3f999c830a9307-uncommitted
  observed_at: '2026-08-26T10:40:00Z'
  recorded_by: franky
upstream:
  - plan.md
  - franky.ticket.yaml
downstream:
  - franky.results.yaml
---

# Tasks

- [x] Audit all seven Franky-relevant skill packages.
  - Acceptance: trigger, input, output, boundary, stop, and validation
    contracts are present or a gap is recorded.
  - Verify: quality and interface validators.
- [x] Repair external-handoff approved-root guidance.
  - Acceptance: consequential runner use requires `--repo-root` for the exact
    approved control-plane root.
  - Verify: focused contract and runner tests.
- [x] Record static validation and runtime limitations.
  - Acceptance: packet validator passes and result names the untracked catalog
    limitation plus native runtime `NOT_ASSESSED` surfaces.
  - Verify: packet validator and Franky contract validator.
