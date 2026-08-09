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
  scientific CLI lifecycle fixture and path/symlink hardening.

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

First obtain maintainer review/acceptance of Issue #19 / PR #20, with AC-10
remaining an explicit human gate. Do not add a project-bootstrap skill or
duplicate OpenScience capabilities until that packaging and boundary decision
is accepted. Afterward, resume the planned `context-strengthening` and
`repository-exploration` slice.
