# Documentation map

This directory separates durable knowledge from bounded work records.

- `CURRENT.md` is the current-state entry point.
- `architecture/` contains system boundaries, workflow, decisions, knowledge,
  and architecture evidence.
- `sessions/` contains preserved historical packets and archived records;
  new live packets use the repository-local `.agents/sessions/` convention.
- `architecture/archify/` contains derived architecture evidence and receipts.

The existing top-level documents are compatibility pointers. Legacy plans and
reviews are preserved under `sessions/records/`; `handoffs/` has been retired.
New work should use GitHub Issues/PRs and, when needed, a complete session
packet rather than adding another parallel work-record namespace. See
`sessions/records/README.md` for the exact mapping.

Canonical source paths are `CURRENT.md`, `architecture/workflow/operation.md`,
`architecture/agents.md`, and `architecture/decisions.md`. Root-level names
remain compatibility pointers for consumers that have not migrated.
