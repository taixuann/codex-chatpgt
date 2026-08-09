# Codex agent configuration guide

This directory contains runtime adapters. The canonical semantic roles remain
defined by `/Users/tai/ai-labs/ops/agents/agents.yaml`; adapters must not
rename, merge, or repurpose those roles.

## Runtime adapters

The registry defines the three canonical planning roles: Feynman, Prometheus,
and Franky. Argus and Athena are support adapters only; they do not expand the
canonical role registry and cannot own an independent workflow.

| Adapter | Function | Default boundary |
| --- | --- | --- |
| `argus` | non-canonical read-only exploration and repository mapping | `read-only` |
| `feynman` | bounded research and evidence work | `read-only` |
| `prometheus` | bounded implementation and code review handoff | `workspace-write` |
| `athena` | non-canonical independent review and critique | `read-only` |
| `franky` | Codex/AI Labs control-plane operation | `read-only`, no subagents |

Support adapters may be used only as bounded leaf workers under the selected
canonical role and workflow. If a task needs a new capability, add or reuse a
skill first; do not create a new role merely to hold domain expertise.

The retained adapters have distinct agent-specific reasons:

| Adapter | Why an agent is justified | Return boundary |
| --- | --- | --- |
| Argus | read-only context isolation for broad repository mapping | paths, evidence, and uncertainty only |
| Athena | independent judgment after execution/validation | severity-ranked critique, no edits |
| Feynman | evidence/provenance boundary and scientific read-only scope | sources, findings, disagreements, handoff |
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
active adapter. Validate every instantiated adapter with
`skills/franky-agent-installer/scripts/validate_agent_toml.py` before use.
