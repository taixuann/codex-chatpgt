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

# Intended runtime and provider path

The intended behavioral acceptance and deployment path for this PLAN is the normal ChatGPT/Codex OpenAI model provider used by Codex.

```text
local Wiki corpus
  -> local Wiki MCP
  -> bounded wiki-evidence/v1 packet
  -> local Codex host
  -> normal OpenAI/ChatGPT Codex provider
  -> model tool-selection + scientific reasoning
```

This boundary is normative for Issue #7:

- Ollama, qwen, or another local-model provider is **not** an implementation dependency, deployment target, required fallback, or substitute acceptance path.
- The previous qwen3-14b/Ollama attempt is historical diagnostic evidence only. Do not repair, install, configure, optimize, or otherwise pursue Ollama/`llama-server` for this Issue.
- If the normal Codex/OpenAI provider is unreachable because of provider/network/DNS/auth/runtime conditions, classify the acceptance run as `BLOCKED` on the Codex/provider path rather than redirecting implementation work into Wiki or a local model.
- If an acceptance run requires Wiki evidence to enter the Codex/OpenAI model context, resolve the applicable explicit data-export permission/policy for that bounded evidence. Do not silently avoid the intended provider by substituting another model.
- The Wiki corpus remains local. Only the bounded evidence/context actually supplied through Codex follows the selected model-provider data path.

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

Treat those as Wiki-side evidence. This PLAN must independently prove Codex-side registration, discovery, routing and behavioral selection through the intended Codex/OpenAI provider path.

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
  | normal OpenAI/ChatGPT Codex model provider
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

Global registration means **globally available**, not **globally mandatory**. Do not set the Wiki server as a hard global runtime dependency merely because it is reusable across projects. A Wiki outage must not prevent unrelated coding, configuration, plotting, fitting, or local-analysis sessions from starting. Literature-grounded tasks may still become `BLOCKED`/`LIMITED` when the required capability is unavailable.

# Phase 0 — Reorient and probe actual local runtime

Before changing repository guidance or local configuration:

1. Reorient from current `main`, applicable AGENTS chain, Issue #7 and this PLAN.
2. Inspect the actual local Codex version and current `~/.codex/config.toml` MCP surface.
3. Confirm the active/default Codex model-provider path is the intended normal OpenAI/ChatGPT Codex provider. Do not switch to or repair a local provider for this Issue.
4. Run supported MCP discovery commands such as the installed runtime's equivalent of `codex mcp list` and inspect help/schema before assuming syntax.
5. Inspect the Wiki MCP launch/connection contract from the local Wiki checkout/handoff.
6. Confirm whether the Wiki server is local stdio, HTTP/streamable HTTP, or another supported transport.
7. Probe whether current Codex supports per-agent MCP/tool permission configuration. Do not infer this from documentation or invent TOML keys.
8. Record the actual MCP protocol version/lifecycle negotiated or supported by the runtime and Wiki server. Do not assume the current `initialize` handshake is a permanent protocol invariant.
9. Record runtime limitations separately from repository semantics.

Stop if the Wiki MCP cannot be started/discovered in the current runtime; report the exact transport/config/runtime blocker rather than building a wrapper. If Wiki transport works but the normal Codex/OpenAI provider path is unavailable or data-export policy blocks the acceptance run, stop as a provider/policy blocker rather than substituting Ollama.

# Phase 1 — Minimal MCP registration and discovery

Preferred default:

- register Wiki MCP once in the user's local/global Codex configuration because the same evidence backend is reusable across research projects;
- keep it enabled/discoverable without making it a hard global startup requirement unless future evidence demonstrates that such strictness is actually desirable;
- constrain the normal agent-facing surface to exactly `wiki.query`, `wiki.source`, and `wiki.related` when the installed runtime supports an allowlist;
- do not commit machine-specific absolute paths, credentials or secrets as canonical repository truth;
- if a portable example or installation procedure is useful, place it under an existing configuration/ops owner rather than creating a new top-level subsystem;
- keep the semantic capability name stable even if the runtime-specific MCP server identifier later changes.

Validation:

- server appears in actual Codex MCP discovery;
- exactly the intended read-only tools are exposed for the normal agent-facing surface;
- tool schemas/descriptions resolve successfully and remain discriminative enough for model selection without duplicating workflow prose;
- read-only/safety annotations, when present, match actual behavior but are not treated as enforcement;
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

Keep failure classes distinct.

## Wiki MCP transport/runtime failure

Examples: MCP unavailable, startup failure, tool discovery failure, schema/runtime mismatch, negotiated-protocol incompatibility.

Behavior:

- record as MCP/runtime capability failure;
- if literature grounding is required, return blocked/limited unless equivalent supplied evidence makes the call unnecessary;
- do not silently answer from unsupported memory/model knowledge;
- do not classify transport failure as `bad_retrieval`, `corpus_gap`, or `scientific_gap`.

## Codex/OpenAI provider or evidence-export failure

Examples: normal Codex/OpenAI provider unavailable, DNS/network/auth failure, model execution failure, or the bounded Wiki evidence cannot be sent to the intended provider under current approval/policy.

Behavior:

- record as a Codex/provider or data-policy acceptance blocker, not a Wiki failure;
- preserve the already-proven Wiki transport evidence;
- do not repair or switch to Ollama/local models as a workaround inside Issue #7;
- resume behavioral acceptance only when the intended provider path and applicable permission are available.

## Successful Wiki query with evidence-state outcome

Preserve Wiki semantics:

- `bad_retrieval`;
- `corpus_gap`;
- `scientific_gap`;
- sufficient/abstention as defined by `wiki-evidence/v1`.

Do not automatically trigger ingestion or architecture expansion from one gap.

# Phase 7 — Behavioral selection evaluation

Static policy quality is insufficient. Exercise the actual Codex runtime using the intended normal OpenAI/ChatGPT Codex model provider.

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
- active intended model/provider path;
- actual tool call(s) if observable;
- selected Wiki tool;
- evidence contract/provenance outcome for positive cases;
- abstention/gap outcome when applicable;
- unnecessary call count/duplicate calls;
- runtime limitation if hidden selection behavior is not exposed.

Pass criteria:

- the run uses the normal intended Codex/OpenAI provider rather than a substituted local model;
- positive cases select Wiki appropriately;
- negative cases do not invoke Wiki merely because they are scientific;
- provenance is preserved;
- insufficient evidence remains insufficient;
- no duplicate search path is invoked unnecessarily;
- no unsupported claims are made about hidden runtime selection.

Use the existing Wiki-side 4-case benchmark as a comparison/reference, but Codex-side validation must be an independent consumer-side run.

# Phase 8 — Deployment and stability acceptance

After one successful host-mediated behavioral run through the intended provider, prove that the integration survives ordinary runtime lifecycle events without adding a monitoring platform.

Use four gates:

```text
transport/contract
  -> Codex/OpenAI host integration
  -> routing/responsibility
  -> stability/regression
```

Minimum stability slice:

1. start a fresh Codex session with the normal intended provider and verify the Wiki server/tool surface is discoverable;
2. run the bounded positive + negative behavioral matrix from Phase 7;
3. restart/reload the MCP server or start another fresh Codex session so discovery is rebuilt;
4. rerun at least one positive and one negative case;
5. verify the positive case still returns `wiki-evidence/v1` with provenance and the negative case still avoids Wiki;
6. record startup/tool/provider failures, duplicate calls, and observed latency only if measurable;
7. tune startup/tool timeouts only when observed failures justify it rather than guessing values;
8. do not introduce daemon health checks, telemetry databases, a bespoke deployment framework, or a local-model fallback for this local read-only capability.

If official MCP conformance tooling can exercise the Wiki server's actual transport/version without creating a second test framework, prefer using it or a bounded equivalent. Protocol-version/backcompat validation belongs primarily to the Wiki server/runtime boundary; `codex-chatpgt` should record the compatibility evidence rather than reimplement protocol conformance.

# Phase 9 — Portability check

Keep canonical semantics harness-neutral:

```text
required capability: scientific-literature-evidence
provider contract: wiki-evidence/v1
current adapter: Codex MCP
intended model runtime for this acceptance: normal Codex/OpenAI provider
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
- A direct stdio JSON-RPC probe of the registered launch command completed
  `initialize`, `tools/list`, and positive/negative `wiki.query` calls. The
  positive case returned a `wiki-evidence/v1` packet with three
  source-grounded evidence items; the contrastive case returned
  `insufficient`/`abstain_or_verify` with an explicit gap. This is
  transport-level evidence only, not proof that the Codex model selected the
  tool. Treat the observed handshake as evidence for the negotiated/supported
  protocol path used by that probe, not as a permanent MCP lifecycle contract.
- The Codex control-plane validators, task-contract checks, focused project
  bootstrap tests, and whitespace checks pass on the current `main` state.
- The user explicitly approved a bounded Wiki evidence export for this
  acceptance run. Fresh `codex exec --ephemeral` sessions used the normal
  Codex/OpenAI provider path, read-only sandboxing, and a temporary config that
  enabled only the registered Wiki server. The model-mediated trace recorded
  exactly one successful `wiki.query` call for each positive case:
  - mechanism: 5 evidence items, `wiki-evidence/v1`, sufficient;
  - comparison: 8 evidence items, `wiki-evidence/v1`, sufficient;
  - factual lookup: 5 evidence items, `wiki-evidence/v1`, sufficient;
  - unknown query: zero evidence, `insufficient`, one gap,
    `abstain_or_verify`.
- Four contrastive fresh sessions (computation, plotting, fitting and coding)
  recorded zero Wiki MCP calls. A further fresh computation session also
  recorded zero calls, while the fresh factual lookup returned a valid
  `wiki-evidence/v1` packet. This is the bounded reload/stability slice.
- Event traces showed one `wiki.query` lifecycle (`in_progress` then
  `completed`) per positive case and no duplicate retrieval calls. The compact
  model JSON for the first lookup reported `duplicate_calls: 0`; the event
  trace is the authoritative count (one call).
- The model/provider identity is not exposed as a richer host event, so this
  evidence proves the normal Codex/OpenAI execution path and tool behavior but
  does not claim hidden adapter/model metadata. Feynman/Athena-specific
  host-side selection remains governed by their existing bounded role
  contracts rather than an invented per-agent MCP configuration.
- No unsupported per-agent MCP fields, duplicate retrieval layer, Wiki
  mutation path, or new wrapper skill/workflow was added.
- A qwen3-14b/Ollama fallback was previously attempted and failed because that
  installation lacked `llama-server`. **This is historical diagnostic evidence
  only. Ollama/local-model repair is explicitly out of scope and must not be
  treated as the next execution step or an acceptance dependency.**

The implementation is therefore a **conditional pass with the Codex host
behavioral slice accepted**: registration, discovery, transport, contract,
positive/negative routing, provenance/abstention, and fresh-session stability
are evidenced. The remaining limitation is host observability: Codex does not
expose richer adapter/model metadata or a separate Feynman/Athena selection
trace, so those boundaries remain policy-level rather than runtime-proven.

## Latest bounded export re-probe — 2026-08-10

The user explicitly approved a bounded Wiki evidence export for this probe.
The local read-only CLI path was exercised with one synthesis query and
returned the following metadata without exporting the corpus or committing
source excerpts:

```yaml
contract_version: wiki-evidence/v1
intent: synthesis
evidence_count: 5
source_ids:
  - sources/raw/markdown/zhou-2022-natural-biomaterial-memristor-bearing.md
  - sources/raw/markdown/wang2019-surface-diffusion.md
  - sources/raw/markdown/lee2016-tuning-ionic-transport.md
  - sources/raw/markdown/europepmc_PMID_32973166.md
gaps: []
```

The normal Codex/OpenAI host was then invoked with the same single-query,
read-only constraint. Codex selected exactly one `wiki.query` call, but the
host cancelled the MCP call before a packet was returned; the runtime also
reported MCP startup `No such file or directory`. This is recorded as
`NOT_ASSESSED/BLOCKED` for this fresh host attempt, not as a Wiki retrieval or
provider success. The earlier accepted host-mediated slice above remains the
active Issue #7 evidence; this re-probe does not replace it and does not
justify a local-model fallback.

### Approved bounded export audit — 2026-08-10

The user re-approved the bounded export for this probe. A fresh local
read-only `wiki.query` lookup was executed once for the same biomaterial
memristor question and returned a sufficient `wiki-evidence/v1` packet with
five evidence items, five source IDs, and no gaps. Only packet metadata was
retained here; the Wiki corpus and source excerpts were not copied into this
repository.

The intended normal Codex/OpenAI run was retried with network access and the
same one-call constraint. Codex selected exactly one `wiki.query` call, but
the MCP call was cancelled before a packet was returned. The resulting
provider trace is therefore `NOT_ASSESSED/BLOCKED` for this attempt, and does
not upgrade or replace the previously accepted host-mediated evidence.

### Bounded export execution — 2026-08-10 (current approval)

The user approved a bounded Wiki evidence export for this probe. The export
was limited to one read-only synthesis query and packet metadata; no Wiki
corpus, source excerpts, or source files were copied into `codex-chatpgt`.

The canonical local Wiki CLI returned a `wiki-evidence/v1` packet with:

```yaml
intent: synthesis
evidence_count: 2
source_count: 2
gaps: []
sufficiency: sufficient
retrieval_mode: hybrid
methods: [bm25, lexical_fallback]
```

The returned source IDs were retained only as repository-relative provenance:

```text
sources/raw/markdown/zhou-2022-natural-biomaterial-memristor-bearing.md
sources/raw/markdown/kumar-2024-metal-ion-proton-coupled-electron-transfer.md
```

The registered MCP adapter was then invoked once with the same bounded query.
It failed before returning a packet because the Wiki runtime raised
`KeyError: 'edges'` while loading its NetworkX graph index
(`.rag/query.py::_load_indexes`). This is recorded as a Wiki-runtime/index
failure, not as a successful host-mediated export. No repair or fallback was
attempted in this Issue, and the earlier accepted Codex/OpenAI slice remains
the active host evidence.

After implementation:

1. validate agent TOML against the actual Codex runtime schema;
2. validate skills/workflows remain unchanged or pass existing validators if touched;
3. run repository CI/control-plane validation;
4. confirm the normal Codex/OpenAI provider path and applicable evidence-export permission are usable;
5. run MCP discovery/startup probe and record supported/negotiated protocol lifecycle where observable;
6. run positive + negative behavioral selection cases through the intended provider;
7. run the bounded fresh-session/reload stability slice;
8. verify read-only MCP surface and absence of duplicate retrieval/local-model implementation;
9. inspect whole diff for prompt/policy duplication;
10. use independent review when material;
11. reconcile Issue #7 criterion-by-criterion;
12. add a bounded evidence comment to #16 explaining what capability is now available to the broader research workflow;
13. add a routing observation to #8 only if this run yields useful general execution-routing evidence.

# Stop / escalation conditions

Stop or narrow rather than adding machinery if:

- Codex MCP transport support differs from assumptions;
- the normal Codex/OpenAI provider path is unavailable or evidence-export policy prevents the intended acceptance run;
- per-agent MCP permissions are unavailable;
- behavioral tool selection cannot be observed reliably;
- a proposed fix starts repairing/configuring Ollama or another local model for this Issue;
- a proposed new skill only wraps MCP tools;
- a proposed config helper duplicates standard Codex configuration;
- a change starts duplicating Wiki/OpenScience retrieval/reasoning;
- one runtime-specific workaround threatens to become canonical architecture;
- negative cases reveal broad over-triggering that should be repaired in policy/description rather than by introducing a router service;
- protocol-version drift is detected and belongs in the Wiki MCP implementation rather than the Codex control plane.

# Definition of done

Issue #7 is complete when the actual local Codex runtime using the normal intended Codex/OpenAI provider can discover and use the Wiki Scientific Evidence MCP through the minimal read-only surface, appropriate parent/Feynman/reviewer paths select it for real literature-grounded tasks and avoid it for contrastive local-only tasks, provenance and insufficiency semantics survive end-to-end, the bounded fresh-session/reload stability check passes, MCP transport/protocol failure remains distinct from Codex/provider/data-policy failure and Wiki evidence gaps, no local-model fallback or duplicate scientific search/reasoning layer exists in `codex-chatpgt`, and the accepted capability boundary remains portable as `scientific-literature-evidence -> wiki-evidence/v1`.
