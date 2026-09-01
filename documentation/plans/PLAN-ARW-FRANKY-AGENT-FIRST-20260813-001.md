---
id: PLAN-ARW-FRANKY-AGENT-FIRST-20260813-001
issue: 56
status: conditional-pass-runtime-gated
updated: 2026-08-13
owner: Franky
---

# Issue #56 — agent-first Franky contract

## Scope

Implement the smallest coherent agent-first surface for the current Codex
control plane: an approved/eligible capability repertoire, an explicit
parent-to-Franky task/result boundary, Franky's one-call closure obligation,
and deterministic contract/evaluation checks. Issue #38 remains authoritative
for skill existence, admission, trigger quality, utility, safety, portability,
and skill-quality evaluation.

The change deliberately does not add a router service, a catch-all Franky
skill, a second workflow engine, one agent per skill, recursive delegation, or
a universal `agent.task.v1` abstraction.

## Accepted semantic model

```text
USER
  ↓ explicit named agent or capability-first parent routing
PARENT
  ↓ bounded franky.task.v1
FRANKY
  ↓ admission → primary capability → impact-triggered support → closure
franky.result.v1
  ↓ evidence gate → independent review when justified → parent acceptance
```

Franky returns `acceptance_ready`, never `system_accepted`, for consequential
self-authored changes. `shared-session-closeout` is lifecycle-required for
consequential work, while the skill-authoring/quality capability resolves
through #38 and is not represented as a locally owned `skill-creator` package.

## Runtime evidence

- Installed runtime: `codex-cli 0.147.0-alpha.6.5`.
- Current official Codex documentation supports `[agents]`, custom-agent
  `skills.config`, and custom-agent inheritance/precedence. The repository
  records only the minimal global contract as a fixture; the actual user config
  remains local runtime state.
- `codex --strict-config -c
  'agents.franky.skills.config=[{path="skills/control-plane/control-plane-audit/SKILL.md",enabled=false}]'
  --version`: `PASS` for configuration parsing.
- A live `codex exec --json --ephemeral --sandbox read-only` probe started a
  thread but could not complete a model turn because DNS/network access to
  `chatgpt.com` and Docs MCP was unavailable. Native `@franky` dispatch and
  per-agent skill enable/disable are therefore `NOT_ASSESSED`/`BLOCKED`, not
  claimed behavioral passes.
- v1 uses explicit required-capability task references and bounded developer
  instructions as the fallback until a completed child-agent trace proves
  native scoping behavior.

## Validation and evaluation

Deterministic checks:

- `python ops/scripts/validate_franky_contracts.py`
- `python ops/scripts/validate_codex_runtime_config.py ops/schemas/examples/codex-agents-settings.toml`
- `python ops/scripts/evaluate_franky_agent.py ops/scripts/fixtures/franky-agent-evaluation.yaml`
- `PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s ops/scripts/tests -v`
- `python skills/control-plane/runtime-adapter-management/scripts/validate_agent_toml.py agents/<name>.toml` for all adapters
- `python skills/control-plane/control-plane-audit/scripts/validate_agent_changelog.py agents`
- `git diff --check`
- CI-equivalent tracked and on-demand skill quality, bootstrap, project-link,
  audit-record, scheduler, inventory, allowlist, and control-plane test gates
- independent Athena read-only review and bounded re-review; no High/Critical
  findings remain, with three Medium consistency findings repaired

The evaluation fixture is a deterministic contract oracle, not a runtime
router. It covers explicit audit, skill repair, agent-adapter mutation,
out-of-scope scientific work, automatic capability-first routing, and missing
mutation authority. Model-mediated selection remains a separate evidence gate.

## Closure matrix

| Surface | Disposition | Evidence |
| --- | --- | --- |
| Franky adapter and return contract | UPDATED | `agents/franky.toml` |
| Retained adapter boundaries | UPDATED | `agents/*.toml`, `agents/AGENTS.md` |
| Approved capability repertoire | UPDATED | `manifests/agent-capability-repertoires.yaml` |
| Franky task/result schemas and fixtures | UPDATED | `ops/schemas/` |
| Runtime settings reference/validator | UPDATED | `ops/schemas/examples/codex-agents-settings.toml`, `ops/scripts/validate_codex_runtime_config.py` |
| Agent-level deterministic evaluation | UPDATED | `ops/scripts/evaluate_franky_agent.py`, fixture |
| Root and workflow guidance | UPDATED | `AGENTS.md`, `documentation/OPERATING-WORKFLOW.md` |
| Current/decision/plan state | UPDATED | `documentation/CURRENT.md`, `documentation/DECISIONS.md`, this plan |
| #38 skill admission/utility ownership | UNCHANGED_VALID | existing catalog/evidence surfaces; no local `skill-creator` admission |
| Native `@franky` dispatch | NOT_ASSESSED | installed CLI exposes no native exec option; no completed model trace |
| Native per-agent `skills.config` behavior | NOT_ASSESSED | parser PASS only; live model turn blocked by network |
| Independent review | UPDATED | Athena read-only re-review: conditional pass; no High/Critical findings; repaired capability-reference, mutation-evaluator, and lifecycle-scope gaps |

## Bounded evolution observation

`NO ACTION`: the requested contract is a one-agent invocation boundary and
closure composition. No recurring evidence justifies a router, catch-all skill,
duplicate lifecycle engine, or generalized task envelope at this time.
