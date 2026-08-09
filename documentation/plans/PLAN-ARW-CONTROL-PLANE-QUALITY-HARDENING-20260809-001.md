---
id: PLAN-ARW-CONTROL-PLANE-QUALITY-HARDENING-20260809-001
issue: 24
status: in-progress
date: 2026-08-09
scope: control-plane quality hardening
---

# Control-plane quality hardening

## Objective

Make the reconciled control plane discoverable, composable, scoped, and
routable without expanding the architecture. The execution order is:

```text
workflow authority
→ capability existence
→ retained-skill naming
→ description/body quality
→ contrastive routing fixture
→ scoped AGENTS
→ agent contracts
→ component linking
→ review
→ validation/CI
```

## Decisions

- `documentation/OPERATING-WORKFLOW.md` remains the canonical global semantic
  lifecycle.
- `workflows/franky/franky.yaml` remains the canonical Franky entrypoint only
  within `franky_control_plane`; its stronger gates are for governed
  control-plane operations with named consumers.
- The eleven tracked skills are retained after capability-existence review;
  each has a deliberate KEEP NAME disposition recorded in `DECISIONS.md`.
- No new agent, router, workflow engine, universal schema, registry, or
  proof-only artifact family is introduced.
- Static routing fixtures are evidence about metadata and neighbor boundaries,
  not proof of LLM runtime selection.

## Implementation surface

- Add specialized workflow authority metadata and validate the global semantic
  source link.
- Add `skills/AGENTS.md`, `workflows/AGENTS.md`, and contract-quality guidance
  under `agents/AGENTS.md`; keep root guidance concise.
- Harden retained skill descriptions and contracts with trigger, inputs,
  outputs, boundary, stop, and validation semantics.
- Add the minimal static contrastive fixture and deterministic validator/test.
- Keep deterministic workflow/link/bootstrap validators colocated with their
  capabilities and preserve existing safety boundaries.
- Update `CURRENT.md`, `DECISIONS.md`, and `OPERATING-WORKFLOW.md` only for
  accepted durable semantics.

## Acceptance mapping

- AC-01: specialized Franky authority is explicit and points to the global
  semantic lifecycle.
- AC-02/03: every tracked skill has KEEP/RENAME disposition before metadata
  changes; no rename is warranted in this pass.
- AC-04/05: retained descriptions and bodies expose discriminative triggers,
  boundaries, reusable procedures, and validation.
- AC-06: fixture covers positive, negative, nearest-neighbor, none, and
  ambiguous cases and prints the behavioral-observability limitation.
- AC-07/08: scoped instruction files and agent contract map are explicit.
- AC-09: component linking is documented in `OPERATING-WORKFLOW.md`.
- AC-10: deterministic validators, focused tests, allowlist, diff check, and
  hosted control-plane CI pass.
- AC-11: no quality bureaucracy or new runtime framework is introduced.

## Validation

Run the existing skill, agent, workflow, IO/cache, task-contract, bootstrap,
project-link, scheduler, allowlist, and CI checks plus:

```text
python skills/franky-maintenance/scripts/validate_skill_routing.py . skills/franky-maintenance/scripts/fixtures/skill-routing.yaml
python -m unittest discover -s skills/franky-maintenance/tests -p 'test_skill_routing.py' -v
```

Behavioral skill selection remains an explicit runtime limitation unless the
active Codex surface exposes an observable selection trace.
