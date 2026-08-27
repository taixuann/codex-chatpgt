---
kind: codex.session-artifact.v1
artifact: plan
session_id: 20260826_franky-skills_001
status: in_progress
provenance:
  source_commit: 67d21cc3bf14a4121e064d8edb3f999c830a9307-uncommitted
  observed_at: '2026-08-26T10:40:00Z'
  recorded_by: franky
upstream:
  - context.md
  - spec.md
downstream:
  - task.md
  - franky.ticket.yaml
---

# Plan

1. Inspect the seven approved Franky skill packages and their focused tests.
2. Run quick validation, quality gates, interface checks, routing checks, and
   package tests.
3. Repair the demonstrated external-handoff root-scope guidance gap.
4. Validate the packet and record static/runtime limitations for parent review.

## Risks and mitigations

- Existing uncommitted changes can contaminate evidence; record the source
  state and report the catalog tracking limitation explicitly.
- Native runtime behavior cannot be inferred from static checks; keep it
  `NOT_ASSESSED`.

## Verification checkpoints

- `quick_validate.py` for all seven packages.
- `validate_skill_quality.py` for all seven packages.
- `validate_skill_interfaces.py skills`.
- Static routing fixture and focused package tests.
- `validate_session_packet.py` for this packet.
