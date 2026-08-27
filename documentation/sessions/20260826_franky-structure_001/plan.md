---
kind: codex.session-artifact.v1
artifact: plan
session_id: 20260826_franky-structure_001
status: in_progress
provenance:
  source_commit: 67d21cc3bf14a4121e064d8edb3f999c830a9307
  observed_at: '2026-08-26T16:30:00+07:00'
  recorded_by: franky
upstream:
  - context.md
  - spec.md
downstream:
  - task.md
  - franky.ticket.yaml
canonical_records:
  issue: null
  plan: null
---

# Plan

Session: `20260826_franky-structure_001`

This is a bounded work packet, not a competing Issue or PLAN authority.

## Ordered steps

1. Inspect live agent, documentation, manifest, and ops ownership.
2. Record the KISS boundary and archive/consumer limitations.
3. Update explanatory boundary documentation only where the live contract is
   underspecified.
4. Validate role boundaries, Franky contracts, documentation impact, and this
   packet; report native runtime behavior separately.
5. Hand the result to the parent for Athena review and acceptance.

## Approval gate

The current user-authorized thread/request explicitly authorizes this bounded
control-plane documentation and packet repair. It does not authorize staging,
commit, push, archive, deletion, final acceptance, or promotion. Record this
approval as evidence and retain the independent Athena and parent-acceptance
gates.

## Risks and mitigations

- Risk: merging declarative and executable surfaces creates ambiguity.
  Mitigation: preserve separate directories and explicit ownership language.
- Risk: stale archive moves are mistaken for accepted canonical changes.
  Mitigation: retain them as uncommitted evidence and require separate review.
- Risk: static checks are overclaimed as runtime proof. Mitigation: mark native
  dispatch/loading/permission behavior `NOT_ASSESSED`.

## Verification checkpoints

- All changed paths are inside the assigned control-plane scope.
- Existing `ops/changes/` remains present.
- No index, router, or workflow engine is introduced.
- Deterministic validators pass after packet completion.
