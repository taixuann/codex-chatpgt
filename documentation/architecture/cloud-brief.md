---
id: CLOUD-BRIEF-CODEX-CONTROL-PLANE
status: active
updated: 2026-08-26
repository: taixuann/codex-chatpgt
branch: main
---

# Cloud brief

## Current objective

Operate the reconciled Codex control plane with a small capability-first
surface. Keep canonical role authority, generic handoffs/links, task
validation, and cloud handoff semantics explicit. Machine workflows remain
policy-gated and are not active unless a real persisted-state consumer is
proven.

## Current state

- The repository is public and contains only the allowlisted control-plane
  layer.
- Credentials, runtime databases, sessions, logs, caches, and linked project
  contents remain excluded by `.gitignore`.
- Canonical roles remain Feynman, Prometheus, and Franky according to the AI
  Labs registry.
- Argus and Athena are bounded non-canonical support adapters.
- Retired Franky wrappers and the unconsumed `workflows/franky/**` machine
  workflow tree are no longer discoverable. Repository role, skill, and
  lifecycle guidance remains the policy boundary; Issue/PLAN/task contracts
  and retained skills provide the active routing surface.
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
- Issue #7’s production Wiki Scientific Evidence MCP is registered in the
  local Codex runtime and now has a bounded model-mediated acceptance slice.
  With explicit user approval for the bounded export, fresh read-only
  Codex/OpenAI sessions selected `wiki.query` exactly once for factual,
  mechanism and comparison questions and preserved `wiki-evidence/v1`
  provenance. An unknown query remained `insufficient` with
  `abstain_or_verify`. Four local-only contrastive tasks and a fresh negative
  reload recorded zero Wiki calls; a fresh positive reload returned the same
  contract. The parent routing/stability boundary is accepted conditionally;
  richer Feynman/Athena adapter/model traces are not exposed by Codex. No
  duplicate retrieval layer or wrapper skill was introduced, and the
  historical Ollama fallback remains out of scope.
  The latest explicitly approved local export also returned a sufficient
  `wiki-evidence/v1` synthesis packet (5 evidence items across 3 distinct
  source IDs, no gaps); only metadata was retained and Wiki raw/knowledge
  files remained unchanged. A fresh host retry selected one `wiki.query` call
  but was cancelled before a packet returned, so this remains supplementary
  local evidence and does not alter the conditional host-runtime boundary.
  The newest approval-confirmed local rerun returned 5 evidence items across
  4 distinct source IDs with no gaps using the bounded biomaterial memristor
  synthesis query. The Wiki validator again confirmed immutable sources
  unchanged and no live knowledge changes; only packet metadata and
  repository-relative provenance were retained.
  The latest approval-confirmed MCP retry failed before returning a packet
  with `KeyError: 'edges'` while loading the Wiki NetworkX graph index;
  contract validation still passed and sources remained immutable. This is
  `NOT_ASSESSED/BLOCKED` runtime/index evidence, not a successful export.
  A fresh OpenCode model-execution attempt on a synthetic skill was rejected
  by the host privacy guard before execution; direct OpenCode behavior remains
  `NOT_ASSESSED`, while no-model catalog and precedence evidence remains valid.
- Issue #14’s external qualification matrix is recorded with exact artifact
  refs/licenses and runtime-fit findings. The installed Codex/OpenAI creator
  is reused; Anthropic/OSS candidates remain reference/deferred.
- Issue #38 is conditionally passed as the installed creator/admission gate.
  It has one real Codex dogfood result (`franky-guidance-manager` ->
  `instruction-maintenance` generalization) and a fresh explicit-disabled
  Codex baseline with no skill-tool event. The current model-visible catalog
  snapshot is 86 entries / 58 unique names with 13 duplicate-name groups. No
  side-by-side lift is claimed
  because a matching with-skill rerun would expose private host skill/config
  content without separate export approval; baseline delta, co-loaded
  selection, dynamic security, and direct OpenCode behavior remain
  `NOT_ASSESSED`.
- Issue #35 is conditionally reconciled: Tier 1 uses existing/generalized
  procedures, Tier 2 is policy/reference/deferred unless measured, Tier 3 is
  on-demand, and all seventeen unconsumed Franky machine workflows plus the
  workflow-organizer package are retired. No registry, marketplace,
  telemetry, dependency graph, or workflow engine was added. A disposable
  OpenCode probe confirmed configured-path discovery and project-local
  shadowing for a colliding skill ID; a second catalog-only comparison kept
  89/89 IDs while swapping the source root for 9 entries when external-skill
  scan flags were toggled. The external OpenCode overlay still exposes
  workflow-manager/install-workflow entries; repository retirement therefore
  does not claim cross-runtime retirement, and activation/cross-runtime
  behavior remain conditional under #12.
- Issue #9 is **NOT_PLANNED for the current horizon**. Historical AgentMemory
  0.9.28 reconnaissance and Phase A–E experiment evidence are retained as
  non-canonical support, but no mandatory memory runtime, memory skill,
  workflow, agent, mirror, or auto-promotion path exists. Reactivation requires
  a new measured continuity/retrieval need.
- The #12 portability handoff remains historical `NOT_EXECUTED`; portability
  is not currently active without an authorized secondary-harness consumer.

## Read next

- [`CURRENT.md`](../CURRENT.md)
- [`DECISIONS.md`](decisions.md)
- [`AGENTS.md`](../../AGENTS.md)
- [`agents/AGENTS.md`](../../agents/AGENTS.md)
- [`task-contract.schema.yaml`](../../ops/schemas/task-contract.schema.yaml)
- [`architecture reconciliation plan`](../plans/PLAN-ARW-ARCHITECTURE-RECONCILIATION-20260809-001.md)

## Validation evidence

The reconciliation change is validated with the Git allowlist, agent adapters,
skill interfaces/quality, scheduler definition, static routing fixture, focused
unit tests, YAML parsing, audit/context/task-contract checks, and Git whitespace
checks. No workflow-layout pass is claimed after the machine workflow tree was
retired. The final commit and remote ref are recorded in Git history.

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
agent or missing-frontmatter warnings. A fresh Codex 0.146.0 read-only probe
with provider connectivity returned `PROBE_OK` and reproduced those clean
adapter/frontmatter results. It also exposed unrelated environment/vendor
warnings (stale model-cache schema, optional plugin manifest fields,
rollout-db fallback, skill-description budget truncation, and an unavailable
optional Computer Use MCP); these do not prove or disprove the remaining
parent-resume/adapter-selection gate.
read-only Graph Engineering validator currently passes (12 pages, 21 Canvas
nodes, 6 edges) and a 16-file before/after hash check found no project
mutation; this remains conditional evidence until the upstream runtime gates
are observed. Future portability, research, memory, and project-inheritance
work remains separately gated by its own runtime evidence.
