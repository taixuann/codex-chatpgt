---
kind: codex.session-artifact.v1
artifact: context
session_id: 20260826_franky-structure_001
status: observed
provenance:
  source_commit: 67d21cc3bf14a4121e064d8edb3f999c830a9307
  observed_at: '2026-08-26T16:30:00+07:00'
  recorded_by: franky
upstream:
  - references.yaml
downstream:
  - spec.md
  - plan.md
---

# Context

Session: `20260826_franky-structure_001`

## Scope and source state

- Repository: `/Users/tai/.codex`
- Source commit: `67d21cc3bf14a4121e064d8edb3f999c830a9307`
- Working tree: uncommitted changes were present before this run.
- Scope: control-plane agents, documentation, manifests, and ops surfaces.
- Excluded: `skills/**`, linked projects, credentials, runtime/private state,
  remotes, push, staging, deletion, and recursive delegation.

## Recovered evidence

- `agents/AGENTS.md` defines canonical roles and states that manifests record
  eligibility while adapters remain runtime-facing; it does not need a new
  role or router for this question.
- `documentation/AGENT-BOUNDARIES.md` already separates canonical roles from
  Argus/Athena support adapters. This run adds a concise ownership note for
  `manifests/` versus `ops/`.
- `manifests/` contains separate skill admission/evidence and agent repertoire/
  shared-contract records. They are declarative and are consumed by validators.
- `ops/` contains schemas, examples, deterministic scripts/tests, schedulers,
  on-demand procedures, and the exceptional `ops/changes/` history. It is the
  executable/checking surface, not a second registry or workflow engine.
- Existing `ops/changes/` is referenced by repository guidance and must remain.
- Existing `documentation/archive/20260826/` moves are uncommitted evidence;
  this packet does not decide whether protected/current/decision material is
  eligible for archival.

## Conflicts and unknowns

- The new `session-packet-management` package is outside this stream and
  remains untracked; catalog validation therefore depends on the other stream
  resolving its package admission state.
- Native dispatch, native skill loading, and host permission enforcement remain
  `NOT_ASSESSED`; static validators cannot establish them.
- No real consumer currently requires a `manifests/INDEX.yaml`; adding one
  would be speculative.

## Human approval evidence

- The parent-authorized follow-up request in this thread explicitly permits
  updating the assigned control-plane guidance and structure packet, while
  prohibiting staging, commit, push, archive, deletion, and changes to skills,
  manifests, or ops schemas. This is mutation authority for this bounded run,
  not final acceptance or promotion.
- Approval source: current user-authorized thread/request, observed
  2026-08-26; the parent retains Athena review and final acceptance.

## Recommended next inspection

- Run the deterministic role, contract, documentation-impact, and packet
  validators after the parent reconciles both Franky streams.
- Obtain independent Athena review before acceptance or promotion.
