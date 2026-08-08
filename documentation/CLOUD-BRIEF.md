---
id: CLOUD-BRIEF-CODEX-CONTROL-PLANE
status: active
updated: 2026-08-08
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

After this baseline is reviewed, build a small vertical slice for
`context-strengthening` and `repository-exploration`. Do not add domain agents
or duplicate OpenScience capabilities without a routing need.
