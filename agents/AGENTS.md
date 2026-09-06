# Codex agent configuration guide

This directory contains runtime adapters. The external AI Labs registry is the
deployment authority for canonical role identity when available, but its
absolute local path is runtime-only and not portable repository authority. The
portable semantic reference is this file plus
the root `AGENTS.md`; adapters must not rename, merge, or repurpose roles.

## Runtime adapters

The retained local control-plane surface is Prometheus, Athena, and Franky.
Athena is a bounded support adapter and does not own an independent workflow.
This checkout carries no Argus or Feynman adapter and makes no local contract
claim for either role; external deployment identity, when available, remains
outside this repository's authority.

| Adapter | Function | Default boundary |
| --- | --- | --- |
| `prometheus` | bounded implementation and code review handoff | `workspace-write` |
| `athena` | non-canonical independent review and critique | `read-only` |
| `franky` | Codex/AI Labs control-plane operation | `read-only`, no subagents |

Support adapters may be used only as bounded leaf workers under the selected
canonical role and workflow. If a task needs a new capability, add or reuse a
skill first; do not create a new role merely to hold domain expertise.

## Authority precedence and update procedure

The authority chain is intentionally one-way:

1. The external AI Labs deployment registry and definitions, when available,
   supply canonical role identity for deployment. The local path
   `/Users/tai/ai-labs/ops/agents/agents.yaml` is a runtime hint only.
2. This file and the root `AGENTS.md` are the portable semantic reference for
   the three roles and their boundaries.
3. `agents/*.toml` are runtime adapters. They may express permission, input,
   output, delegation, and escalation boundaries, but they cannot create,
   rename, or redefine a canonical role.
4. Root `AGENTS.md` is runtime policy for this repository and cannot override
   the canonical registry or expand adapter authority.
5. `skills/` contains reusable capabilities; skill packages do not redefine
   roles or own lifecycle state.

If these surfaces disagree, stop and report the conflict. Update the owning
external definition when deployment semantics are changing, then reconcile the
portable reference, adapter, and explanatory documentation in one reviewed
work unit. Do not add synchronization automation or silently infer a
canonical-role change from a local adapter edit.

The retained adapters have distinct agent-specific reasons:

| Adapter | Why an agent is justified | Return boundary |
| --- | --- | --- |
| Athena | independent judgment after execution/validation | severity-ranked critique, no edits |
| Prometheus | bounded workspace-write execution boundary | changed paths, tests, deviations, rollback |
| Franky | control-plane permission/workflow boundary | scope, findings, validation, approval boundary |

Skill hints are deliberately kept out of the TOML adapters because the active
Codex runtime rejects unknown profile keys. Route skills through task packets,
role instructions, and the normal discovery surface instead. If a requested
skill is not installed on the active runtime, the parent must report that
limitation and use the task contract or an available capability instead.

Names are personality labels; descriptions and developer instructions are the
machine-readable routing contract. Model and reasoning are runtime defaults,
not personality semantics. The parent may select a different supported tier
when the task contract and validation policy justify it.

## Delegation contract

The parent should delegate only a bounded packet:

```yaml
task: concise action
scope: exact paths or question boundary
inputs: concrete files or artifacts
constraints: permission and scientific boundaries
output: finding or named artifact
acceptance: observable pass conditions
validation: deterministic command or review criterion
stop: completion or escalation condition
```

The Franky-specific packet is serialized as `franky.task.v1`; its structured
return is `franky.result.v1`. The result carries a thin ordered evidence
envelope (`REQUEST` through `ACCEPTANCE_READY`), not an executable workflow
engine. Franky may compose one primary capability, only impact-triggered
supporting capabilities, and the lifecycle closeout capability for consequential
work. It must not spawn recursively or independently system-accept its own
consequential changes.

The minimal global Codex baseline is:

```toml
[agents]
enabled = true
max_concurrent_threads_per_session = 4
interrupt_message = true
```

Runtime precedence is explicit spawn override → custom-agent setting →
`[agents]` default → parent/session setting. The actual user config remains
local runtime state and is not canonical repository state.
Subagents do not re-plan the parent request, widen scope, or make final
scientific/control-plane decisions. Skills provide procedure and expertise;
agents provide execution topology and permission isolation.

## Contract quality

Every retained adapter must state why it is an agent rather than a skill or
normal parent behavior, when it is used, its authority and write scope, the
task input contract, local autonomy, return contract, non-goals, and
escalation condition. Model and reasoning defaults are resource policy, not
role identity. The parent remains responsible for synthesis, conflict
resolution, acceptance, and durable-state promotion.

## Configuration locations

Codex adapters can be placed in:

- Global: `/Users/tai/.codex/agents/*.toml`
- Project-scoped: `<project>/.codex/agents/*.toml`

The `templates/agent.toml` file is an inert source template and is not an
active adapter. Validate every instantiated adapter against the active task
contract and CI checks before use. This checkout no longer carries the retired
`runtime-adapter-management` validator.
