---
id: PLAN-ARW-SCIENTIFIC-EVIDENCE-20260809-001
issue: 7
status: conditional-pass
activation_gate: satisfied-by-production-wiki-mcp-handoff
scope: wiki-scientific-evidence-mcp-integration
updated: 2026-08-10
---

# Objective

Integrate the production-ready `taixuann/wiki` Scientific Evidence MCP into the local Codex control plane as a reusable, read-only scientific-literature evidence capability while preserving existing ownership boundaries:

```text
skills      = reusable procedures
agents      = roles / execution responsibility
MCP         = capability transport
Wiki        = evidence backend
OpenScience = scientific reasoning / execution
```

The target is routing and integration quality, not another Wiki/search subsystem.

# Activation evidence

The previous deferred gate is satisfied.

Wiki-side handoff reports:

- canonical read-only tools: `wiki.query`, `wiki.source`, `wiki.related`;
- stable return contract: `wiki-evidence/v1`;
- source-grounded retrieval with provenance, evidence metadata, bounded relations, sufficiency/abstention and gap semantics;
- Research Ticket lifecycle remains outside MCP/Wiki retrieval transport;
- CLI/JSON and multiple harness paths are validated;
- MCP usability and end-to-end agent-selection checks passed factual lookup, mechanism, comparison and insufficient-evidence cases;
- reported retrieval metrics are approximately recall/source coverage 0.979, MRR 0.906, nDCG 0.906.

Treat those as Wiki-side evidence. This PLAN must independently prove Codex-side registration, discovery, routing and behavioral selection.

# Current control-plane constraints

Preserve the current architecture:

- `documentation/OPERATING-WORKFLOW.md` remains the global semantic lifecycle;
- #16 remains the broader Research and Knowledge workflow owner;
- #8 remains the general execution/delegation/model-routing owner;
- Feynman remains the bounded scientific/evidence role;
- parent remains default orchestrator;
- no new Wiki agent, RAG/search skill, workflow family, registry, database or router service;
- do not add unsupported fields to agent TOML; runtime schema must be probed before configuration claims;
- GitHub is durable coordination state, while actual MCP registration is local Codex runtime configuration.

# Target architecture

```text
LOCAL CODEX
  |
  | global MCP registration / discovery
  v
Wiki Scientific Evidence MCP
  |  wiki.query / wiki.source / wiki.related
  v
wiki-evidence/v1
  |
  v
consuming parent / Feynman / bounded reviewer
  |
  v
scientific reasoning / #16 workflow / project decision
```

Policy remains capability-first:

```text
Need literature grounding?
  |- no  -> normal task path
  `- yes -> Wiki MCP -> evidence packet -> reasoning
```

# Phase 0 — Reorient and probe actual local runtime

Before changing repository guidance or local configuration:

1. Reorient from current `main`, applicable AGENTS chain, Issue #7 and this PLAN.
2. Inspect the actual local Codex version and current `~/.codex/config.toml` MCP surface.
3. Run supported MCP discovery commands such as the installed runtime's equivalent of `codex mcp list` and inspect help/schema before assuming syntax.
4. Inspect the Wiki MCP launch/connection contract from the local Wiki checkout/handoff.
5. Confirm whether the Wiki server is local stdio, HTTP/streamable HTTP, or another supported transport.
6. Probe whether current Codex supports per-agent MCP/tool permission configuration. Do not infer this from documentation or invent TOML keys.
7. Record runtime limitations separately from repository semantics.

Stop if the Wiki MCP cannot be started/discovered in the current runtime; report the exact transport/config/runtime blocker rather than building a wrapper.

# Phase 1 — Minimal MCP registration and discovery

Preferred default:

- register Wiki MCP once in the user's local/global Codex configuration because the same evidence backend is reusable across research projects;
- do not commit machine-specific absolute paths, credentials or secrets as canonical repository truth;
- if a portable example or installation procedure is useful, place it under an existing configuration/ops owner rather than creating a new top-level subsystem;
- keep the semantic capability name stable even if the runtime-specific MCP server identifier later changes.

Validation:

- server appears in actual Codex MCP discovery;
- exactly the intended read-only tools are exposed for the normal agent-facing surface;
- tool schemas/descriptions resolve successfully;
- no write/promotion/ingestion/Research-Ticket operations are accidentally exposed through the normal surface.

# Phase 2 — Tool-selection policy in existing owners

Implement the smallest durable routing rule in existing instruction/research owners.

Positive Wiki triggers:

- literature-grounded factual lookup;
- mechanism question requiring literature evidence;
- scientific comparison;
- competing/contradictory mechanism analysis;
- source trace/provenance request;
- evidence-sufficiency judgment.

Negative Wiki triggers:

- pure computation;
- coding;
- local plotting;
- fitting supplied/local data;
- ordinary configuration/workflow work;
- scientific tasks already fully grounded in supplied local evidence.

Do not create a `wiki-search`, `scientific-rag`, or equivalent wrapper skill unless a later repeated procedure exists beyond simple tool selection.

Prefer updating the existing Research and Knowledge/source-routing semantics and only the minimal agent/runtime guidance needed for actual selection. Avoid duplicating the same policy in root AGENTS, Feynman TOML, skill bodies and project files.

# Phase 3 — Agent and subagent boundary

Target behavior:

- **Parent/main agent:** may use Wiki MCP directly when literature grounding is needed and delegation would add no value.
- **Feynman:** primary bounded specialist for literature/evidence work when context isolation or scientific evidence review is useful.
- **Athena:** may use Wiki only when an independent scientific review explicitly needs fresh literature grounding; otherwise review supplied evidence.
- **Prometheus:** implementation worker; do not turn it into a research agent. Return scientific-evidence needs to parent/Feynman when material.
- **Franky:** control-plane operator; Wiki is outside ordinary Franky maintenance scope.
- **Argus:** repository/context exploration does not imply literature retrieval.

If runtime supports reliable per-agent tool allowlists, use the smallest evidence-backed restriction compatible with these boundaries.

If runtime does not support such allowlists, do not simulate them with unsupported TOML. Rely on:

- read-only Wiki MCP surface;
- scoped instructions/task contracts;
- parent authority and review;
- explicit runtime evidence about what is and is not enforceable.

# Phase 4 — Bounded subagent context

Do not bloat task packets with Wiki architecture or benchmark history.

When a bounded child needs scientific evidence, the parent should pass only what is material, conceptually:

```yaml
task: <scientific question/review>
required_capability: scientific-literature-evidence
available_provider: Wiki MCP
constraints:
  - preserve provenance
  - preserve insufficiency/abstention
  - do not widen into ingestion/promotion
acceptance: <observable evidence/review condition>
```

Use the MCP tool descriptions/schema for detailed invocation semantics. Do not copy a static tool catalog into every agent profile.

# Phase 5 — OpenScience integration boundary

Preserve:

```text
Wiki MCP -> evidence packet
OpenScience / consuming agent -> reasoning, synthesis, investigation, Research Ticket lifecycle, artifacts and decisions
```

Do not:

- start/finalize Research Tickets inside MCP transport configuration;
- duplicate Wiki ranking/retrieval logic;
- convert evidence return directly into accepted Wiki knowledge;
- route every scientific task through OpenScience/Wiki by ceremony.

# Phase 6 — Failure semantics

Keep two failure classes distinct.

## Transport/runtime failure

Examples: MCP unavailable, startup failure, tool discovery failure, schema/runtime mismatch.

Behavior:

- record as MCP/runtime capability failure;
- if literature grounding is required, return blocked/limited unless equivalent supplied evidence makes the call unnecessary;
- do not silently answer from unsupported memory/model knowledge;
- do not classify transport failure as `bad_retrieval`, `corpus_gap`, or `scientific_gap`.

## Successful Wiki query with evidence-state outcome

Preserve Wiki semantics:

- `bad_retrieval`;
- `corpus_gap`;
- `scientific_gap`;
- sufficient/abstention as defined by `wiki-evidence/v1`.

Do not automatically trigger ingestion or architecture expansion from one gap.

# Phase 7 — Behavioral selection evaluation

Static policy quality is insufficient. Exercise the actual Codex runtime.

Use at least these positive cases:

1. factual literature lookup;
2. mechanism question;
3. scientific comparison;
4. insufficient-evidence question.

Use at least these negative/contrastive cases:

1. pure computation over supplied values/data;
2. plotting supplied local data;
3. fitting/analyzing an existing local dataset;
4. coding/configuration request with no literature need.

For each case record only observable evidence:

- prompt/task;
- whether Wiki was expected;
- actual tool call(s) if observable;
- selected Wiki tool;
- evidence contract/provenance outcome for positive cases;
- abstention/gap outcome when applicable;
- unnecessary call count/duplicate calls;
- runtime limitation if hidden selection behavior is not exposed.

Pass criteria:

- positive cases select Wiki appropriately;
- negative cases do not invoke Wiki merely because they are scientific;
- provenance is preserved;
- insufficient evidence remains insufficient;
- no duplicate search path is invoked unnecessarily;
- no unsupported claims are made about hidden runtime selection.

Use the existing Wiki-side 4-case benchmark as a comparison/reference, but Codex-side validation must be an independent consumer-side run.

# Phase 8 — Portability check

Keep canonical semantics harness-neutral:

```text
required capability: scientific-literature-evidence
provider contract: wiki-evidence/v1
current adapter: Codex MCP
```

Do not introduce a cross-harness plugin framework in this Issue. Future #12 work may bind another harness to the same evidence capability once the Codex integration is stable.

# Expected repository change surface

Keep the diff minimal and evidence-driven. Likely owners to inspect/update include:

- `documentation/RESEARCH-KNOWLEDGE-WORKFLOW.md` source routing;
- minimal applicable `AGENTS.md` / `agents/AGENTS.md` guidance if runtime behavior requires it;
- Feynman adapter instructions only if one concise routing boundary materially improves tool use;
- existing deterministic/runtime validation surfaces if a reusable MCP configuration/probe check is justified;
- `documentation/CURRENT.md` / `DECISIONS.md` only after actual runtime acceptance.

Do not assume all listed files must change. Closure should identify actual consumers before mutation.

# Validation and closure

## Current Codex-side evidence (2026-08-10)

- The Wiki MCP is registered once in the local global Codex configuration;
  `codex mcp list --json` reports the documented stdio server and launch
  command. The machine-specific registration is intentionally not committed
  to this repository.
- The Wiki-side contract, read-only tool surface, four behavioral cases, and
  portability checks pass independently. The exposed tools are exactly
  `wiki.query`, `wiki.source`, and `wiki.related`.
- The Codex control-plane validators, task-contract checks, focused project
  bootstrap tests, and whitespace checks pass on the current `main` state.
- A non-interactive Codex probe discovered `wiki.query`, but the MCP call was
  cancelled before an evidence packet was returned. An interactive retry was
  interrupted by provider/DNS and MCP-startup failures. No end-to-end Codex
  evidence packet or consumer-selection trace was observed.
- No unsupported per-agent MCP fields, duplicate retrieval layer, Wiki
  mutation path, or new wrapper skill/workflow was added.

The implementation is therefore a **conditional pass for registration,
discovery, and contract evidence**, while the host-runtime acceptance gate
remains open. Do not mark Issue #7 complete until a live Codex session records
one successful Wiki query with provenance/abstention semantics and the
required positive/negative routing cases.

After implementation:

1. validate agent TOML against the actual Codex runtime schema;
2. validate skills/workflows remain unchanged or pass existing validators if touched;
3. run repository CI/control-plane validation;
4. run MCP discovery/startup probe;
5. run positive + negative behavioral selection cases;
6. verify read-only MCP surface and absence of duplicate retrieval implementation;
7. inspect whole diff for prompt/policy duplication;
8. use independent review when material;
9. reconcile Issue #7 criterion-by-criterion;
10. add a bounded evidence comment to #16 explaining what capability is now available to the broader research workflow;
11. add a routing observation to #8 only if this run yields useful general execution-routing evidence.

# Stop / escalation conditions

Stop or narrow rather than adding machinery if:

- Codex MCP transport support differs from assumptions;
- per-agent MCP permissions are unavailable;
- behavioral tool selection cannot be observed reliably;
- a proposed new skill only wraps MCP tools;
- a proposed config helper duplicates standard Codex configuration;
- a change starts duplicating Wiki/OpenScience retrieval/reasoning;
- one runtime-specific workaround threatens to become canonical architecture;
- negative cases reveal broad over-triggering that should be repaired in policy/description rather than by introducing a router service.

# Definition of done

Issue #7 is complete when the actual local Codex runtime can discover and use the Wiki Scientific Evidence MCP through the minimal read-only surface, appropriate parent/Feynman/reviewer paths select it for real literature-grounded tasks and avoid it for contrastive local-only tasks, provenance and insufficiency semantics survive end-to-end, MCP transport failure is handled honestly, no duplicate scientific search/reasoning layer exists in `codex-chatpgt`, and the accepted capability boundary remains portable as `scientific-literature-evidence -> wiki-evidence/v1`.
