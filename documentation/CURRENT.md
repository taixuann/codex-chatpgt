---
id: CURRENT-CODEX-CONTROL-PLANE
status: active
updated: 2026-08-09
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

- **#2** — the earlier draft PR #3 was superseded and closed during cleanup; a
  fresh execution branch must be created from the current `main` if this proof
  is resumed.
- **#14** — external-skill qualification may run in parallel now.
- **#17** — PLAN exists but its initial proof must piggyback on a future #2
  implementation PR; the closed draft PR #3 is not an active proof.
- **#5/#6/#10** — backlog PLANs exist but remain blocked by upstream evidence.
- **#15** — evidence-collecting. Reactive path now has one accepted real slice through PR #18 (GitHub Actions validation repair/hardening); the workflow family is still open because a representative proactive system-change path and broader reuse/change-surface evidence remain unproven.
- **#16** — inventory-first; select one real research task and inspect existing Wiki/Personal Wiki/RAG-BM25/OpenScience/Typst interfaces before implementation.
- **#13** — bounded rationalization is implemented on the current branch; retired wrappers/workflow families are removed, generic replacements are tracked, and remaining deferred portability/migration capabilities stay unchanged.
- **#24** — control-plane quality hardening is implemented on
  `codex/issue24-quality-hardening`: Franky authority is explicitly scoped to
  the control plane, retained skill metadata/contracts are discriminative,
  scoped `AGENTS.md` guidance is present for agents/skills/workflows, and a
  small static contrastive routing fixture distinguishes metadata evidence from
  behavioral runtime selection. Final acceptance is pending PR/CI review.
- **#7/#8/#9/#11/#12** — backlog PLANs remain gated by their own runtime evidence.

## Planning state

`documentation/plans/` now contains backlog/activation-aware PLANs for open architecture Issues that previously lacked them. A PLAN file does not imply execution readiness. Status and activation gates are authoritative for readiness, and each PLAN must be revised near execution against current repository/runtime evidence.

Issue #2 and #17 also have branch-scoped execution PLANs tied to their active branches.

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

The immediate blocker to new core evidence is that #2 has not yet been run against the current repository/runtime baseline. Its draft PR branch predates several documentation and accepted CI updates and should be synced/reconciled before local runtime reconnaissance begins.
