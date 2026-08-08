---
id: CURRENT-CODEX-CONTROL-PLANE
status: active
updated: 2026-08-08
---

# Current state

## Scope

This repository is the Codex-first control plane and cloud coordination
bridge. It is deliberately separate from research-project contents.

## Canonical role authority

The AI Labs registry remains authoritative and defines exactly three canonical
planning roles:

| Role | Ownership | Adapter |
| --- | --- | --- |
| Feynman | scientific evidence, methodology, and protocol review | `agents/feynman.toml` |
| Prometheus | implementation design, code review, testing, and execution handoff | `agents/prometheus.toml` |
| Franky | workflow routing, registry/platform maintenance, and control plane | `agents/franky.toml` |

`Argus` and `Athena` are non-canonical read-only support adapters. They are
bounded leaf workers and do not alter the role registry:

- Argus: internal repository/context exploration.
- Athena: independent review and critique.

## Operating kernel

The shared lifecycle is:

```text
RECALL → ORIENT → REASON → PLAN → CRITIQUE PLAN → DELEGATE/EXECUTE
→ VALIDATE → REVIEW → SYNTHESIZE → FINAL CRITIQUE → COMMIT KNOWLEDGE
```

Workflows are organized by lifecycle and task, not by persona. Skills contain
reusable procedures; agents provide permission and context isolation; the
task contract connects the three.

## Implemented baseline

- Global guidance and bounded delegation policy: [`AGENTS.md`](../AGENTS.md).
- Runtime adapter contracts: [`agents/AGENTS.md`](../agents/AGENTS.md).
- Franky lifecycle, installation, maintenance, and factory workflow branches:
  [`workflows/franky/`](../workflows/franky/).
- Franky control-plane skill family and validation scripts:
  [`skills/`](../skills/).
- Change and audit evidence: [`ops/changes/`](../ops/changes/).
- Cloud handoff entrypoint: [`CLOUD-BRIEF.md`](CLOUD-BRIEF.md).
- Canonical task contract: [`../ops/schemas/task-contract.schema.yaml`](../ops/schemas/task-contract.schema.yaml).

## Known gaps

1. Global capability skills for context strengthening, repository exploration,
   research, implementation, validation, and knowledge promotion are not yet
   standardized as a separate capability layer.
2. Project-specific lifecycle adapters are not yet deployed in this bridge.
3. Agentmemory is an available substrate but is not yet treated as accepted
   canonical state; memory observations require explicit promotion.
4. Self-evolution remains proposal-first and human-gated.

These gaps are deliberately deferred until the reconciled contracts are used
in a small vertical slice.
