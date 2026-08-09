---
id: CURRENT-CODEX-CONTROL-PLANE
status: active
updated: 2026-08-10
---

# Current state

## Scope

This repository is the Codex-first control plane and cloud coordination bridge. It is deliberately separate from research-project contents.

## Canonical role authority

The AI Labs registry remains authoritative and defines exactly three canonical planning roles:

| Role | Ownership | Adapter |
| --- | --- | --- |
| Feynman | scientific evidence, methodology, and protocol review | `agents/feynman.toml` |
| Prometheus | implementation design, code review, testing, and execution handoff | `agents/prometheus.toml` |
| Franky | workflow routing, registry/platform maintenance, and control plane | `agents/franky.toml` |

`Argus` and `Athena` are non-canonical read-only support adapters. They are bounded leaf workers and do not alter the role registry:

- Argus: internal repository/context exploration.
- Athena: independent review and critique.

## Accepted operating baseline

- Runtime guidance and bounded delegation policy: [`AGENTS.md`](../AGENTS.md).
- Local cross-workspace discovery: when present, the ignored
  `$CODEX_HOME/ENVIRONMENT.md` map is read during fresh non-trivial orientation
  before capability routing. It names local availability and owner entrypoints
  only; it is neither portable control-plane state nor authority over external
  workspaces.
- Canonical human-readable general lifecycle: [`OPERATING-WORKFLOW.md`](OPERATING-WORKFLOW.md).
- Architecture decisions: [`DECISIONS.md`](DECISIONS.md).
- Cloud progressive-disclosure entrypoint: [`CLOUD-BRIEF.md`](CLOUD-BRIEF.md).
- Runtime adapter contracts: [`agents/AGENTS.md`](../agents/AGENTS.md).
- Active skill/workflow surface: [`../skills/`](../skills/) and [`../workflows/`](../workflows/). Retired Franky wrappers and proposal-only workflow families are no longer part of discovery.
- Canonical task contract: [`../ops/schemas/task-contract.schema.yaml`](../ops/schemas/task-contract.schema.yaml).
- Historical change/audit evidence: [`../ops/changes/`](../ops/changes/). New ordinary work does not create a CHG wrapper unless a named consumer requires one.
- Deterministic repository CI: [`../.github/workflows/franky-validate.yml`](../.github/workflows/franky-validate.yml), accepted through PR #18. It is path-filtered to control-plane/runtime surfaces, validates the canonical workflow surface rather than retired root files, resolves repository/local skills portably, permits unresolved optional external skills only on explicitly conditional steps, and leaves personal local-runtime scope checks outside hosted CI.
- The canonical task-contract schema is checked by
  [`../ops/scripts/validate_task_contract.py`](../ops/scripts/validate_task_contract.py)
  against the checked-in example under `ops/schemas/examples/` and by focused
  unit tests.

The shared operating lifecycle remains capability-first, bounded, validation-oriented, and review-selective. `OPERATING-WORKFLOW.md` is the human-readable semantic source; machine-readable workflows are justified only when runtime state/gate enforcement adds value.

## Proposed semantic surfaces under proof

The following documents exist as proposed shared semantics and are **not yet accepted runtime truth merely because they are documented**:

- [`SYSTEM-EVOLUTION-WORKFLOW.md`](SYSTEM-EVOLUTION-WORKFLOW.md) — System Configuration and Change workflow; proof tracked by #15.
- [`RESEARCH-KNOWLEDGE-WORKFLOW.md`](RESEARCH-KNOWLEDGE-WORKFLOW.md) — Research and Knowledge workflow; proof tracked by #16.
- [`GOAL-PLAN-GRAPH.md`](GOAL-PLAN-GRAPH.md) — Goal–Plan linking semantics; minimal proof tracked by #17.

Ownership boundaries currently intended for proof:

- #15 owns **how bounded system changes are handled**.
- #11 owns **when repeated/material evidence may become durable self-evolution**.
- #16 owns the **full research/knowledge lifecycle**.
- #7 owns only **external scientific evidence acquisition/critique capability** used by #16 when needed.

## Current execution sequence

Core proof remains:

```text
#2 Context acquisition
  -> #5 Bounded execution + deterministic validation
      -> #6 Independent review
          -> #10 One real project pilot
```

Current readiness:

- **#19** — bounded file-first scientific project bootstrap is merged to `main`
  through PR #20 (merge commit `a87a948`); Issue #19 is closed. The packaged
  `project-bootstrap` skill owns the agent-facing procedure around its
  deterministic helper and colocated tests. No workflow or second
  `file-workbench` skill exists.

- **#2** — bounded context acquisition is implemented and merged through PR #33
  (`edf446c`). The explicit-allowlist packet helper, schema-valid task fixture,
  deterministic tests, and hosted CI step are accepted as the v1 procedure.
  A fresh read-only run against the current `/Users/tai/ai-labs` baseline
  produced 3 canonical and 4 repository-evidence entries with no conflicts or
  uncertainties. Host-observable parent-resume/adapter traces remain
  unavailable, so the Issue is conditionally passed as v1 for deterministic
  behavior but remains open for host-level runtime acceptance.
- **#14** — external-skill qualification may run in parallel now.
- **#17** — PLAN exists but its initial proof must piggyback on a future #2
  implementation PR; the closed draft PR #3 is not an active proof.
- **#5** — accepted through the bounded execution/closure record in
  `PLAN-ARW-EXECUTION-VALIDATION-20260809-001.md`. PR #33 is the bounded
  change surface; its induced failure/repair, impact frontier, syntactic and
  semantic closure, whole-diff check, and revalidation are mapped there.
- **#6** — the consequential slice now has a bounded independent read-only
  review in a separate Athena-style context, recorded in
  `PLAN-ARW-INDEPENDENT-REVIEW-20260809-001.md` as `CONDITIONAL-PASS`. The
  review added judgment beyond deterministic checks and documented a concrete
  low-risk skip case. The current host still does not expose parent-resume or
  adapter-selection traces, so runtime acceptance remains conditional. A
  local Codex review probe found and repaired unsupported `preferred_skills`
  adapter fields in PR #34 (`200b606`); the local discovery root was also
  repaired for two legacy skills missing frontmatter, with follow-up startup
  reports showing zero malformed-agent and missing-frontmatter warnings. A
  fresh Codex 0.146.0 read-only probe with provider connectivity returned
  `PROBE_OK` and reproduced no malformed-agent/frontmatter warnings; it did
  expose unrelated environment/vendor warnings (stale model-cache schema,
  optional plugin manifest fields, rollout-db fallback, skill-description
  budget truncation, and an unavailable optional Computer Use MCP). These are
  recorded as runtime observations, not silently counted as acceptance.
- **#10** — the Graph Engineering pilot has conditionally passed the selected
  read-only integration slice. It consumed the merged #2 helper in
  read-only mode. An earlier live Issue comment records 2 canonical + 3
  repository-evidence entries; the current rerun intentionally used a broader
  explicit allowlist and produced 3 canonical + 4 repository-evidence
  entries. The project validator passed (12 pages, 21 Canvas nodes, 6 edges),
  and the selected project/instruction file hashes were unchanged before and
  after execution. It found no project override, lifecycle adapter,
  project-specific skill/agent, or evolution signal (`NO ACTION`). This
  remains conditional only for host-runtime limitations; the exact rerun hashes
  and review disposition are recorded in the #6 review PLAN.
- **#15** — evidence-collecting. Reactive path now has one accepted real slice through PR #18 (GitHub Actions validation repair/hardening); the workflow family is still open because a representative proactive system-change path and broader reuse/change-surface evidence remain unproven.
- **#16** — inventory-first; select one real research task and inspect existing Wiki/Personal Wiki/RAG-BM25/OpenScience/Typst interfaces before implementation.
- **#7** — the production Wiki Scientific Evidence MCP is registered once in
  the local global Codex configuration. Wiki-side contract, read-only surface,
  four behavioral cases, portability, and repository validators pass. Codex
  discovery is confirmed, but the available non-interactive/interactive probes
  did not return a live evidence packet because MCP approval and provider/DNS
  startup failed. A direct stdio JSON-RPC probe did return a valid
  `wiki-evidence/v1` packet for both a grounded lookup and an insufficient
  query, proving transport and abstention semantics but not model routing. A
  network-enabled Codex retry was withheld by the data-export safety boundary.
  An offline Codex fallback entered the local `qwen3-14b` provider session but
  could not infer because the Ollama installation lacks `llama-server`; no
  model/tool-selection trace was produced.
  No duplicate retrieval layer or wrapper skill was added; host-runtime use
  and routing remain conditional gates.
- **#13** — bounded rationalization is implemented on the current branch; retired wrappers/workflow families are removed, generic replacements are tracked, and remaining deferred portability/migration capabilities stay unchanged.
- **#24** — control-plane quality hardening is accepted through PR #30
  (`c559f9a`). Franky authority is explicitly scoped to the control plane,
  retained skill metadata/contracts are discriminative, scoped `AGENTS.md`
  guidance is present for agents/skills/workflows, and a small static
  contrastive routing fixture distinguishes metadata evidence from behavioral
  runtime selection. Hosted CI passed; behavioral selection remains an
  explicit runtime limitation.
- **#31 Phase A** — session-continuity semantics are conditionally passed
  through PR #32
  (`2cf7b80`). Fresh orientation, event-driven selective reorientation,
  authority ordering, failure reclassification, acceptance-before-learning,
  bounded evolution observation, and logical-session continuation guidance are
  now part of the canonical operating surface. The #10 pilot returned
  `NO ACTION` for evolution observation and produced no natural reorientation
  event. No session manager, checkpoint
  store, evolution database, or new skill/workflow was added. Issue #31 stays
  open for empirical runtime acceptance; the available Codex probe does not
  expose AGENTS load timing, automatic closeout, compaction internals, or
  custom adapter selection.
- **#7/#8/#9/#11/#12** — backlog PLANs remain gated by their own runtime evidence.

## Planning state

`documentation/plans/` now contains backlog/activation-aware PLANs for open architecture Issues that previously lacked them. A PLAN file does not imply execution readiness. Status and activation gates are authoritative for readiness, and each PLAN must be revised near execution against current repository/runtime evidence.

Issue #2 and #17 now link to current live/revised PLANs; historical PR #3 is
not an active proof fixture. #5 is accepted against the merged #2 contract;
host-level runtime acceptance remains explicitly open under #2/#6.

## Anti-overengineering state

The current design intentionally preserves semantic distinctions while delaying machinery:

- no custom goal graph database;
- no one-Issue-per-task policy;
- no workflow-per-persona/tool;
- no mandatory memory layer;
- no model-router platform before representative tasks;
- no project lifecycle adapter unless real project evidence requires it;
- no plugin/harness abstraction before stable behavior exists;
- #13/#21 cleanup rules are now active for this control-plane baseline; each
  retained abstraction has a named consumer and historical proof-only records
  remain read-only provenance.

Simplification should remove duplicate machinery or unclear ownership, not collapse distinctions that preserve provenance, authority, validation, or review independence.

## Known execution gap

The bounded #2 helper has now been rerun against the current repository/runtime
baseline and the read-only Graph Engineering pilot remains hash-stable. The
remaining gap is host-observable parent-resume/adapter behavior; neither
should be inferred from deterministic tests, the project validator, or the
bounded independent review.
