---
id: CLOUD-BRIEF-CODEX-CONTROL-PLANE
status: active
updated: 2026-08-09
repository: taixuann/codex-chatpgt
branch: main
---

# Cloud brief

## Current objective

Reconcile the Codex control plane before adding the next capability layer.
Keep canonical role authority, runtime support adapters, skills, workflows,
task contracts, and cloud handoff semantics explicit and reviewable.

## Current state

- The repository is public and contains only the allowlisted control-plane
  layer.
- Credentials, runtime databases, sessions, logs, caches, and linked project
  contents remain excluded by `.gitignore`.
- Canonical roles remain Feynman, Prometheus, and Franky according to the AI
  Labs registry.
- Argus and Athena are bounded non-canonical support adapters.
- Franky workflows and skills are established; global capability skills are
  the next planned layer, not part of this reconciliation change.
- Issue #19 now has a bounded file-first bootstrap implementation in PR #20:
  adaptive artifact maps, dry-run/explicit apply, brownfield-safe updates,
  immutable `data/raw/` handling, and external Wiki/OpenScience references.
  The current branch's focused discovery suite passes 9 tests, including the
  scientific CLI lifecycle fixture and path/symlink hardening. The reasoning
  procedure is now packaged as one `project-bootstrap` skill around the
  deterministic primitive; no workflow or second `file-workbench` skill was
  added.

## Read next

- [`CURRENT.md`](CURRENT.md)
- [`DECISIONS.md`](DECISIONS.md)
- [`AGENTS.md`](../AGENTS.md)
- [`agents/AGENTS.md`](../agents/AGENTS.md)
- [`task-contract.schema.yaml`](../ops/schemas/task-contract.schema.yaml)
- [`latest reconciliation plan`](../ops/changes/2026/CHG-20260808-003/PLAN.md)

## Validation evidence

The reconciliation change is validated with the Franky allowlist, canonical
layout, skill-interface, workflow-layout, audit-record, unit-test, and Git
whitespace checks. The final commit and remote ref are recorded in Git history.

## Next decision

Issue #19 / PR #20 is now accepted: PR #20 was squash-merged into `main` as
`a87a948` and the Issue is closed. Do not add a second `file-workbench` skill or
duplicate OpenScience capabilities until a distinct reusable contract exists.
The next bounded step is the #13/#21 rationalization handoff; it does not
authorize mass cleanup without runtime evidence.
