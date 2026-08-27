# Session packet contract

This is a lightweight record convention, not a workflow engine or universal
schema. Use YAML for machine-consumed records and Markdown for human review.

## Required links

`session.yaml` should identify:

```yaml
kind: codex.session-packet.v1
session_id: 20260826_migration-codex_001
repository_root: /absolute/repository/path
packet_root: documentation/sessions/20260826_migration-codex_001
canonical_records:
  issue: null
  plan: null
  pr: null
source_state:
  commit: <commit-or-uncommitted>
  recorded_at: <ISO-8601>
status: proposed
```

`context.md`, `spec.md`, `plan.md`, and `task.md` must use
`codex.session-artifact.v1` frontmatter with an artifact identity, lifecycle
status, source-commit/observation/recorder provenance, and reciprocal links to
their immediate upstream/downstream artifacts. Ticket and result records must
retain their existing Franky contract kinds; session linkage belongs in the
packet manifest and references rather than invented schema fields.
`references.yaml` may hold bounded source links with `path`, `kind`, `state`,
`commit_or_hash`, `observed_at`, and `relationship`.

## Franky records

`franky.ticket.yaml` must remain compatible with
`ops/schemas/franky-task.schema.yaml`; use the existing `franky.task.v1`
contract rather than inventing a session-specific task schema.

`franky.results.yaml` must remain compatible with
`ops/schemas/franky-result.schema.yaml`; include source-state-bound validation,
review status, rollback, limitations, and the exact human approval boundary.

The packet may reference these records; it must not redefine their authority.

## Lifecycle status

Use only statuses meaningful to the owning contract, for example `proposed`,
`in_progress`, `needs_review`, `blocked`, `acceptance_ready`, `closed`, or
`archived`. `closed` means the packet was recorded and reviewed as required;
it does not itself promote any canonical state.
