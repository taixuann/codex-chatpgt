# Documentation map

This directory separates durable knowledge from bounded work records.

- `CURRENT.md` is the current-state entry point.
- `architecture/` describes system boundaries and ownership.
- `workflow/` describes the accepted operating lifecycle.
- `knowledge/` contains compiled knowledge-plane guidance.
- `decisions/` indexes accepted architecture decisions.
- `sessions/` contains auditable, bounded work-unit packets.
- `archify/` contains derived architecture evidence and receipts.

The existing top-level documents, `plans/`, `reviews/`, and `handoffs/` are
retained as compatibility and historical surfaces. They are not deleted by
this migration. New work should use GitHub Issues/PRs and, when needed, a
session packet rather than adding another parallel plan or review namespace.

Canonical source pointers remain `CURRENT.md`, `OPERATING-WORKFLOW.md`,
`AGENT-BOUNDARIES.md`, and `DECISIONS.md` until consumers complete a later,
explicit path migration.
