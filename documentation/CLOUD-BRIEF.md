---
id: CLOUD-BRIEF-CODEX-CONTROL-PLANE
status: active
updated: 2026-08-09
repository: taixuann/codex-chatpgt
branch: main
---

# Cloud brief

## Current objective

Operate the reconciled Codex control plane with a small capability-first
surface. Keep canonical role authority, generic handoffs/links, retained
workflow contracts, task validation, and cloud handoff semantics explicit.

## Current state

- The repository is public and contains only the allowlisted control-plane
  layer.
- Credentials, runtime databases, sessions, logs, caches, and linked project
  contents remain excluded by `.gitignore`.
- Canonical roles remain Feynman, Prometheus, and Franky according to the AI
  Labs registry.
- Argus and Athena are bounded non-canonical support adapters.
- Retired Franky wrappers (`github-review`, `skill-installer`, `goal-session`,
  `workflow-factory`, and the old external/project-link wrappers) are no longer
  discoverable. Generic replacements and the retained deterministic workflow
  validator remain.
- Issue #19 now has a bounded file-first bootstrap implementation in PR #20:
  adaptive artifact maps, dry-run/explicit apply, brownfield-safe updates,
  immutable `data/raw/` handling, and external Wiki/OpenScience references.
  The current branch's focused discovery suite passes 9 tests, including the
  scientific CLI lifecycle fixture and path/symlink hardening. The reasoning
  procedure is now packaged as one `project-bootstrap` skill around the
  deterministic primitive; no workflow or second `file-workbench` skill was
  added.
- Issue #24 quality hardening is accepted through PR #30 (`c559f9a`): Franky
  workflow authority is scoped, retained skill contracts and descriptions are
  discriminative, scoped instruction files are explicit, and the static
  contrastive routing fixture is part of hosted CI. Behavioral runtime skill
  selection is not claimed because the active Codex surface exposes no trace.
- Issue #31 Phase A is accepted into `main` through PR #32 (`2cf7b80`): fresh
  orientation, event-driven selective reorientation, failure classification,
  acceptance-before-learning, bounded evolution observation, and logical
  session continuation semantics are now canonical. No session/evolution
  platform was introduced. Empirical runtime acceptance remains open because
  the available Codex probe does not expose AGENTS load timing, automatic
  closeout, compaction internals, or custom adapter selection.

## Read next

- [`CURRENT.md`](CURRENT.md)
- [`DECISIONS.md`](DECISIONS.md)
- [`AGENTS.md`](../AGENTS.md)
- [`agents/AGENTS.md`](../agents/AGENTS.md)
- [`task-contract.schema.yaml`](../ops/schemas/task-contract.schema.yaml)
- [`architecture reconciliation plan`](plans/PLAN-ARW-ARCHITECTURE-RECONCILIATION-20260809-001.md)

## Validation evidence

The reconciliation change is validated with the Franky allowlist, canonical
layout, skill-interface, workflow-layout, audit-record, unit-test, and Git
whitespace checks. The final commit and remote ref are recorded in Git history.

## Next decision

Issue #19 / PR #20 is now accepted: PR #20 was squash-merged into `main` as
`a87a948` and the Issue is closed. Do not add a second `file-workbench` skill or
duplicate OpenScience capabilities until a distinct reusable contract exists.
The #13/#21 rationalization is now applied to the control-plane baseline.
The next vertical proof is a fresh #2 context-acquisition run followed by #5
closure/validation, selective #6 review, and the real-project #10 pilot. The
read-only Graph Engineering validator currently passes (12 pages, 21 Canvas
nodes, 6 edges) and a 16-file before/after hash check found no project
mutation; this remains conditional evidence until the upstream runtime gates
are observed. Future portability, research, memory, and project-inheritance
work remains separately gated by its own runtime evidence.
