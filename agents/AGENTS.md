# Codex agent configuration guide

This directory contains runtime adapters. The canonical semantic roles remain
defined by `/Users/tai/ai-labs/ops/agents/agents.yaml`; adapters must not
rename, merge, or repurpose those roles.

## Runtime adapters

| Adapter | Function | Default boundary |
| --- | --- | --- |
| `argus` | read-only exploration and repository mapping | `read-only` |
| `feynman` | bounded research and evidence work | `read-only` |
| `prometheus` | bounded implementation and code review handoff | `workspace-write` |
| `athena` | independent review and critique | `read-only` |
| `franky` | Codex/AI Labs control-plane operation | `read-only`, no subagents |

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

## Configuration locations

Codex adapters can be placed in:

- Global: `/Users/tai/.codex/agents/*.toml`
- Project-scoped: `<project>/.codex/agents/*.toml`

The `templates/agent.toml` file is an inert source template and is not an
active adapter. Validate every instantiated adapter with
`skills/franky-agent-installer/scripts/validate_agent_toml.py` before use.
