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
- Issue #2’s bounded context-acquisition procedure is merged through PR #33
  (`edf446c`): explicit allowlist, deterministic packet hashes, sensitive-path
  and symlink rejection, task-contract fixture, focused tests, and hosted CI
  validation. A fresh read-only run against the current `/Users/tai/ai-labs`
  baseline produced 3 canonical and 4 repository-evidence entries with no
  conflicts or uncertainties. It is conditionally accepted as v1 for
  deterministic behavior; host-observable parent-resume and adapter-selection
  traces remain unavailable.
- The Graph Engineering #10 pilot now consumes that helper read-only. An
  earlier live Issue comment records 2 canonical + 3 project-evidence entries;
  the current rerun intentionally used a broader explicit allowlist and
  produced 3 canonical + 4 project-evidence entries, with validator pass (12
  pages, 21 Canvas nodes, 6 edges) and selected project/instruction files
  unchanged by before/after hashes. No project override, lifecycle adapter,
  project-specific skill/agent, or evolution signal was needed (`NO ACTION`).
  Exact rerun hashes and the conditional
  independent-review disposition are recorded in the #6 review PLAN. This
  remains conditional only for host-runtime acceptance.

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
The #5 execution/closure slice is accepted in
`plans/PLAN-ARW-EXECUTION-VALIDATION-20260809-001.md`; its host-level runtime
uncertainty remains scoped to #2/#6. The selective #6 review against the
#5/#10 evidence is conditionally passed in
the bounded read-only review recorded in
`plans/PLAN-ARW-INDEPENDENT-REVIEW-20260809-001.md`; host-runtime acceptance
remains open and must not be inferred from deterministic checks. #5 closure,
#10 pilot integration, and #31 evolution observation are recorded as
conditional evidence in their existing PLANs; no new machinery was added.
The first local review probe also found unsupported `preferred_skills` keys in
all agent adapters; PR #34 (`200b606`) repaired that runtime-schema defect and
the follow-up probe reported zero malformed-role warnings. External review
execution remains approval-gated because it would transmit repository content.
The local discovery-root probe is now clean: both legacy skills with missing
frontmatter were repaired and the follow-up startup reported zero malformed-
agent or missing-frontmatter warnings.
read-only Graph Engineering validator currently passes (12 pages, 21 Canvas
nodes, 6 edges) and a 16-file before/after hash check found no project
mutation; this remains conditional evidence until the upstream runtime gates
are observed. Future portability, research, memory, and project-inheritance
work remains separately gated by its own runtime evidence.
