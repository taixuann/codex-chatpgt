---
kind: codex.session-artifact.v1
artifact: spec
session_id: 20260826_franky-structure_001
status: proposed
provenance:
  source_commit: 67d21cc3bf14a4121e064d8edb3f999c830a9307
  observed_at: '2026-08-26T16:30:00+07:00'
  recorded_by: franky
upstream:
  - context.md
downstream:
  - plan.md
---

# Specification

Session: `20260826_franky-structure_001`

## Objective

Make the control-plane structure understandable and KISS: manifests describe
declarative eligibility/evidence, ops owns executable validation/probes, and
documentation explains the boundary without introducing a mega-manifest,
router, or workflow engine.

## Assumptions

- Existing canonical role authority and Issue/PLAN/PR lifecycle remain intact.
- Prometheus remains general-purpose; Argus and Athena remain bounded support
  adapters.
- The current dirty worktree belongs to the parent and other workstreams.

## Success criteria

- Documentation states the distinct purpose and ownership of manifests and ops.
- No speculative `manifests/INDEX.yaml`, merged registry, or new workflow engine
  is created.
- `ops/changes/` remains preserved and exceptional rather than mandatory.
- Agent descriptions remain aligned with the canonical role boundaries.
- A linked packet and reproducible validation evidence are recorded.

## Boundaries

- Always: preserve authority precedence, source state, and unrelated edits.
- Ask first: global policy changes, external registry changes, archival or
  publication decisions, and any runtime/security mutation.
- Never: edit skill packages in this stream, linked projects, credentials,
  private sessions, remotes, or perform final acceptance.

## Open questions

- Whether the parent wants the pending archive moves accepted as a separate
  reviewed work unit remains unresolved.
