# Documentation map

This directory separates durable knowledge from bounded work records.

- `CURRENT.md` is the current-state entry point.
- `architecture/` contains system boundaries, workflow, decisions, knowledge,
  and architecture evidence.
- `sessions/` contains auditable, bounded work-unit packets.
- `architecture/archify/` contains derived architecture evidence and receipts.

The existing top-level documents are compatibility pointers. `plans/`,
`reviews/`, and `handoffs/` are retained as historical work-record surfaces;
they are not deleted by this migration. New work should use GitHub Issues/PRs
and, when needed, a session packet rather than adding another parallel plan
or review namespace.

Canonical source paths are `CURRENT.md`, `architecture/workflow/operation.md`,
`architecture/agents.md`, and `architecture/decisions.md`. Root-level names
remain compatibility pointers for consumers that have not migrated.
