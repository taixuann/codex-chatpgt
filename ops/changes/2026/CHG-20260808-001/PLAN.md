# Codex-first agent routing — Setup 1

## Objective

Establish a small, measured Codex reference implementation for delegation and
model/reasoning routing. This phase is intentionally local to `.codex`.

## In scope

- Runtime-profile mapping for explorer, executor, and reviewer work.
- A bounded subagent task-packet contract.
- Deterministic validation and escalation policy.
- Read-only runtime probes of supported agent/model/reasoning behavior.
- Minimal adapter and guidance changes only after an exact approved preview.

## Out of scope

- New canonical semantic roles or changes to the AI Labs role registry.
- OpenCode, DeepSeek, or other harness deployment.
- Skills redesign, research-project work, credentials, MCP configuration,
  scheduler changes, remotes, and automatic publication.

## Baseline evidence

- `agents/code_mapper.toml`, `agents/feynman.toml`, `agents/franky.toml`, and
  `agents/prometheus.toml` pass the local agent schema validator.
- `workflows/franky/franky.yaml` passes the canonical-layout validator.
- `agents/codex_agent_template.toml` declares `pr_explorer` and fails the
  filename/name validator. It is preserved as an unresolved user-work collision.
- Existing role adapters use GPT-5.4-family names; GPT-5.6 runtime support must
  be observed before migration.

## Proposed runtime policy

| Runtime profile | Capability tier | Default reasoning | Intended use |
| --- | --- | --- | --- |
| explorer | Luna | low or medium | Read-only discovery, extraction, inventory |
| executor | Luna | high | Clear, bounded implementation with deterministic checks |
| reviewer | Terra | high | Independent review, risk assessment, and escalation decisions |
| parent | Terra | medium or high | Scope, synthesis, approval boundaries, and final judgment |

`Sol` and `max` are escalation-only and require a demonstrated quality need.
These are routing targets, not claims that all targets are currently available
as persistent adapter models.

## Subagent task packet

Every delegation must state:

```yaml
task: concise action
scope: exact paths or question boundary
inputs: concrete files, artifacts, or facts
constraints: read-only or permitted mutation boundary
output: returned finding or named artifact
acceptance: observable pass conditions
validation: deterministic command or review criterion
stop: completion or escalation condition
```

The parent retains synthesis and any approval decision. A child neither widens
scope nor delegates again unless the selected workflow explicitly allows it.

## Validation and escalation

1. Run deterministic checks first.
2. For judgment-bearing or non-trivial work, use the reviewer profile.
3. Escalate only after repeated validation failure, reviewer disagreement, an
   architectural change, or material scientific/control-plane risk.
4. Human approval remains required for configuration, destructive, external,
   scientific, and scope-expanding changes.

## Runtime probes before migration

1. Observe which configured/custom agent names the active Codex runtime exposes.
2. Run one read-only, bounded exploration task through the existing explorer
   profile and record model/effort evidence returned by the runtime.
3. Run one read-only review task through the prospective reviewer profile only
   after its adapter exists and has passed schema validation.
4. Compare task completion, acceptance coverage, latency, and observed model/
   reasoning metadata; do not treat a successful spawn alone as acceptance.

## Exact configuration preview required before apply

The next preview must decide, with no implicit overwrite:

1. Whether `agents/codex_agent_template.toml` is renamed into a valid active
   adapter, converted into a valid inert template, or removed by an explicitly
   approved destructive action.
2. Which existing adapters, if any, move from GPT-5.4 to observed-supported
   GPT-5.6 model names.
3. Whether runtime profiles are represented as new adapters or as routing
   guidance over existing adapters. No new canonical role is created.

## Rollback

Each approved adapter change is reversible by restoring its exact prior TOML.
The change record will list before-state hashes and no remote action is allowed.

## Applied result

- `argus.toml` is now the read-only exploration adapter, replacing the legacy
  `code_mapper.toml` path.
- `athena.toml` is now the independent read-only reviewer profile.
- `feynman.toml`, `prometheus.toml`, and `franky.toml` retain their canonical
  semantic boundaries with GPT-5.6 Terra/Luna defaults.
- The prior invalid `codex_agent_template.toml` is now the inert,
  schema-valid `templates/agent.toml`.
- `agents/AGENTS.md` now documents personality labels, task packets, and the
  skill-versus-agent boundary.
- All active adapters now use the five-part instruction contract: ROLE,
  BOUNDARIES, LOCAL AUTONOMY, SKILL POLICY, and RETURN CONTRACT.
- Adapters expose `preferred_skills` without claiming skill ownership; task
  packets may still provide `required_skills`.
- Routing remains conditional: the parent delegates only when isolation,
  parallelism, independent judgment, or permission separation adds value.
- The global operating kernel now records conditional AI-loops, bounded fresh
  context, dynamic role/model/effort routing, and final-critique requirements.
- Agentmemory is already wired into Codex MCP; its desktop hook workaround is
  now installed with reversible backups, and the local service is healthy.

## Memory integration result

The five knowledge planes are now explicit in global guidance:

```text
AGENTS.md → behavior and boundaries
CURRENT/DECISIONS/PLAN → canonical state
agentmemory → prior observations and recurring patterns
Wiki → compiled reviewed knowledge
RAG/source corpus → original evidence
```

`agentmemory` is configured at `/Users/tai/.codex/config.toml`, its hooks are
merged into `/Users/tai/.codex/hooks.json`, and backups were created under
`/Users/tai/.agentmemory/backups/`. Startup initially reported a healthy local
service and a listener is present on localhost:3111, but a later CLI status
reported unknown health with zero sessions and observations. A new Codex
session is required before lifecycle capture can be verified end-to-end. No LLM
provider key was added, so capture currently uses zero-LLM BM25/on-device
behavior.

## Validation result

Passed: all active adapter TOMLs, the inert template, canonical Franky layout,
audit record, change record, changelog, and `git diff --check`.

An actual spawned-child probe was not run from this Franky control-plane turn:
the canonical Franky adapter explicitly has `subagents: disabled`. The adapter
configuration is therefore complete and statically validated; a live spawn
probe should be run under a permitted execution/review workflow as a separate
bounded test.
