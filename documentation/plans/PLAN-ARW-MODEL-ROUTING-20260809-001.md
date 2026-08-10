---
id: PLAN-ARW-MODEL-ROUTING-20260809-001
issue: 8
status: ready-for-bounded-opencode-proof
activation_gate: representative-runtime-tasks-from-2-5-6-now-available
scope: execution-routing-and-opencode-lane
updated: 2026-08-10
---

# Objective

Prove a small portable execution-routing policy that can use OpenCode as a bounded secondary executor/accelerator without creating a second orchestration platform.

The routing policy must keep these concerns distinct:

```text
task/capability
!= executor/runtime
!= model
!= reasoning effort
!= session
!= validation
!= review
```

Codex/main remains the primary orchestrator and final acceptance authority. OpenCode is an optional execution lane for work whose boundedness, repeatability, cost/latency profile, or parallelism makes external execution useful.

# Why this PLAN is active now

Issue #8 originally deferred routing until representative #2/#5/#6 work existed. That evidence now exists: bounded context acquisition, execution/validation, independent review, Wiki capability routing, and AgentMemory runtime probes provide real task classes and runtime constraints.

The next useful proof is not another abstract model table. It is one bounded OpenCode lane that exercises executor choice, model choice, explicit working-directory affinity, session reuse/fork/fresh behavior, deterministic validation, and graceful fallback.

# Existing capability audit

## `skills/external-handoff`

The repository already contains `skills/external-handoff`.

Use it only for its intended boundary:

```text
approved task crosses runtime/tool/team boundary
-> prepare bounded role-neutral handoff
-> explicit scope / evidence / approval / rollback
```

Do **not** turn this skill into the OpenCode executor. Its current contract explicitly says it does not execute the external action and ordinary parent-to-worker delegation stays in the task contract.

The current SKILL text mentions a "bundled runner", but the checked-in skill directory currently contains only `SKILL.md` and `agents/openai.yaml`; no runner is present. Treat this as a contract/documentation inconsistency to resolve during qualification, not as evidence that an executor already exists.

## Reuse rule

Reuse existing task-contract, validation, external-handoff, and session-closeout semantics where applicable. Do not create a new `opencode-handoff` skill, workflow, agent persona, or routing daemon merely for symmetry.

A new reusable OpenCode-specific skill/helper is eligible only after runtime evidence shows a stable trigger plus stable input/output that cannot be expressed cleanly through the existing task contract + a small deterministic adapter.

# Target execution model

```text
TASK / TASK CONTRACT
        |
        v
EXECUTION ROUTING GATE
  |- deterministic shell/script
  |- Codex parent / bounded Codex worker
  `- OpenCode bounded lane
        |
        v
EXECUTION IDENTITY
(repo, logical objective, lane, model family)
        |
        v
SESSION POLICY
reuse | fork | fresh
        |
        v
EXPLICIT REPO ROOT / WORKING DIRECTORY
        |
        v
EXECUTE
        |
        v
DETERMINISTIC VALIDATION
        |
        v
PARENT SYNTHESIS / ACCEPTANCE
```

# OpenCode lane responsibilities

A minimal OpenCode execution adapter, if proven necessary, owns only:

1. resolve the exact repository/project root;
2. choose a bounded execution lane and explicit model from policy;
3. resolve session policy (`reuse`, `fork`, or `fresh`) against the logical objective;
4. invoke OpenCode in the intended directory/session/model;
5. return compact execution result, session identity, changed-surface evidence, and validation evidence to the parent.

It does not own architecture decisions, canonical acceptance, persistent memory, GitHub truth, general scheduling, or self-evolution.

# Information ownership and access model

Do not use `codex-chatpgt/documentation/` as a dump for all execution/runtime information.

Use five distinct information owners:

```text
1. codex-chatpgt / GitHub
   = canonical durable coordination and accepted state

2. local control-plane runtime state
   = machine-specific bookkeeping and indexes

3. OpenCode
   = actual execution-session history and message/diff/event state

4. AgentMemory
   = cross-session historical experience and reusable lessons

5. target project repositories
   = actual code/data/project truth and Git history
```

## Canonical GitHub state

`codex-chatpgt` should retain only durable reviewed semantics and accepted evidence, such as:

- routing policy;
- execution-lane semantics;
- session reuse/fork/fresh rules;
- model-tier policy;
- validation and fallback contracts;
- Issue / PLAN / PR links;
- accepted runtime limitations or decisions.

Do not commit machine-specific runtime noise such as:

- OpenCode session IDs;
- local absolute paths;
- per-run latency samples;
- raw model responses;
- every tool event;
- local session registries;
- transient execution logs.

## Local runtime index

Machine/runtime bookkeeping belongs in ignored local state, not canonical Git state.

A minimal session registry may map:

```text
(repo, objective, lane)
-> session_id
-> model/provider attribute
-> last_used / status
```

A minimal append-only run record may store per invocation:

```text
run_id
repo / objective
executor
session_id
session_action: reuse | fork | fresh
requested model
actual model where observable
status
changed surface
validation result
parent disposition
```

Prefer JSON/JSONL or another simple local format before considering SQLite. Do not mirror transcripts, embeddings, or repository content into this runtime index.

The actual path is a local implementation detail to probe before creation. Do not canonize a path merely because an example uses `~/.local/state/...`.

## OpenCode session ownership

OpenCode itself should remain the owner of actual execution-session content:

```text
session id
-> messages
-> tool events
-> diffs
-> compaction/session history
```

Do not copy raw OpenCode transcripts into `codex-chatpgt` for continuity. Use explicit session IDs and the runtime/API/CLI to retrieve deeper execution context only when needed.

## AgentMemory ownership

AgentMemory owns reusable historical experience such as:

- recurring runtime failures;
- useful implementation lessons;
- routing outcomes;
- repeated workarounds;
- material executor/model observations.

It is not a per-run telemetry database and must not become the canonical OpenCode session registry.

## Target project truth

The target project repository remains authoritative for the actual implementation state:

```text
code / data / tests / Git history / PR
```

The control plane should reference accepted outcome evidence, not mirror every project diff or artifact into `codex-chatpgt`.

# Progressive context access

The parent should retrieve information according to the question rather than loading every store at session start:

```text
What is currently accepted?
-> CURRENT / DECISIONS / Issue / PLAN / live Git

Which execution session belongs to this objective?
-> local runtime session registry / OpenCode session list

What exactly happened in that execution?
-> OpenCode session/messages/diff/events

Have we encountered this problem before?
-> targeted AgentMemory recall

What actually exists in the project?
-> target project repository/runtime
```

This is an access policy, not a requirement to build a new aggregate database.

A future convenience command may present one context view that joins pointers from these owners, for example:

```text
objective context view
|- canonical Issue / PLAN / status
|- active OpenCode session pointer
|- latest bounded execution result
|- relevant memory lessons
`- target-repo state pointer
```

Such a command is eligible only if repeated use proves value. It should remain a view over existing owners, not become a new source of truth.

# Directory affinity

OpenCode execution must never depend on whatever shell directory the caller happens to occupy.

Every external execution must resolve and pass the intended repository/project root explicitly. The same logical objective must not silently jump across repositories because a previous shell session changed directory.

Directory affinity is part of execution identity because it controls applicable project instructions/configuration, file discovery, session namespace, and validation scope.

# Session affinity

Do not use an implicit "last session" rule in automation.

Prefer an explicit mapping:

```text
(repo, logical objective, lane/model family)
-> OpenCode session ID
```

Reuse a session only when:

- repository/project is unchanged;
- logical objective is materially the same;
- execution lane/model family remains appropriate;
- context is healthy enough that reuse reduces reconstruction cost rather than importing stale state.

Fork when prior context is useful but execution independence, reviewer independence, model escalation, or a changed sub-objective benefits from a clean branch of context.

Create a fresh session when the objective changes materially, authoritative state invalidates prior assumptions, independent judgment is required, or the existing session is materially noisy/stale.

Do not put the session registry in canonical Git state. It is local runtime state and may be reconstructed from the runtime where practical.

# Model routing

Canonical policy should use semantic tiers first:

```text
economy
balanced
strong
strongest
```

The OpenCode adapter may map these tiers to currently available provider/model identifiers only after probing the installed runtime and account/provider surface.

Initial hypotheses to test:

- deterministic extraction / repetitive bounded edits / test-fix loops: economy;
- normal bounded multi-file implementation with strong validation: economy or balanced;
- ambiguous or difficult implementation: balanced/strong or keep in Codex;
- architecture, consequential synthesis, scientific judgment, or final acceptance: keep in parent/Codex by default;
- independent review: use a separate review context/model only when #6 justifies it.

Do not bind one permanent model to OpenCode or to a persona. Explicit model selection should be stable within a logical execution session when possible; model escalation should prefer a fork/fresh execution rather than silently changing the model inside a reused session when that would invalidate cache/context assumptions.

# Prompt/cache affinity

Prompt caching is provider/runtime behavior, not a correctness guarantee. Treat it as an optimization.

Increase cache/context reuse probability by keeping stable, where appropriate:

- provider/model family;
- logical session;
- system/project instruction surface;
- tool/permission surface;
- repository root;
- bounded command/task shape.

Do not sacrifice correctness to chase cache hits. Fresh authoritative state wins over reused conversational context.

# When OpenCode earns a call

OpenCode is favored only when all are reasonably true:

1. the work is bounded enough to express with an explicit contract;
2. expected useful model work exceeds invocation/session-management overhead;
3. output can be deterministically validated or independently checked;
4. using a second execution context improves latency, cost, parallelism, or parent-context cleanliness;
5. the task does not require continuous parent architecture decisions.

Good candidate task classes:

- bounded test/fix loops;
- repetitive edits/refactors with strong validation;
- log/result extraction and classification;
- repository checks and bounded maintenance;
- memory health/reconciliation audits;
- implementation slices whose Issue/PLAN already fixes scope and acceptance criteria;
- independent parallel inspection where branches do not mutate the same surface.

Keep work in Codex/main when:

- architecture or canonical decision-making dominates;
- task scope is still changing;
- validation is weak relative to consequence;
- execution requires constant synthesis of intermediate results;
- coordination cost exceeds likely speed/cost benefit.

# Parallelism

OpenCode is primarily an accelerator when a bounded task can run independently while the parent performs other work.

Use parallel lanes only when dependencies and write surfaces are independent. Two executors must not concurrently mutate the same file/branch surface unless an explicit merge/ownership strategy exists.

Candidate pattern:

```text
Codex parent: architecture / integration judgment
OpenCode: bounded implementation or repetitive inspection
shell: validators / deterministic probes
-> parent joins compact evidence
```

# OpenCode commands and skills

Do not begin by creating a broad command collection.

OpenCode commands are convenience entrypoints, not canonical workflow ownership. Candidate commands such as repo checks or memory audits should be introduced only after the underlying procedure proves recurring and stable.

The repository's existing `external-handoff` skill should remain a handoff-contract skill. If runtime proof later justifies a reusable OpenCode execution procedure, first prefer a small deterministic adapter invoked from ordinary routing policy; create a skill only when agent-facing trigger/instructions add repeatable value beyond the adapter.

# Runtime probing requirements

Before any broad configuration, probe the actual local OpenCode installation and record:

- version;
- available provider/model identifiers;
- non-interactive execution syntax actually accepted;
- explicit working-directory control;
- session list/create/resume/fork behavior;
- agent/permission controls used by the intended lane;
- structured/JSON output availability;
- server/headless mode availability if later considered;
- project/global command and skill discovery surfaces;
- actual AgentMemory plugin/MCP wiring and whether native capture fires;
- observed prompt/cache metrics only where the provider exposes them;
- failure/fallback behavior when session/model/runtime controls are invalid.

Advertised features are hypotheses until the installed runtime proves them.

# Phase A — audit before configuration

1. Inspect the installed OpenCode runtime, global/project config, commands, agents, skills/plugins, MCP wiring, and model/provider inventory.
2. Determine whether a suitable existing command/skill/helper already performs bounded external execution.
3. Reconcile the `external-handoff` bundled-runner wording with the actual checked-in contents; fix the contract only if runtime/repository evidence confirms the intended behavior.
4. Inventory where OpenCode stores session state and which API/CLI surface can recover session IDs/messages/diffs without a duplicate mirror.
5. Inventory existing local control-plane state owners before creating any session registry or run log.
6. Do not mutate global configuration merely to make the architecture diagram prettier.

# Phase B — first bounded execution lane

7. Select one representative real task with strong deterministic validation.
8. Route it intentionally among shell vs Codex vs OpenCode and record why OpenCode adds value.
9. Execute OpenCode with explicit repo root, explicit model, explicit session policy, and bounded task contract.
10. Record actual session ID, requested vs actual model/runtime route where observable, changed surface, validation result, latency/cost indicators where observable, and parent acceptance outcome.
11. Keep raw execution/session content in OpenCode; write only minimal ignored local bookkeeping needed to recover the session and recent run result.

# Phase C — session/model affinity proof

12. Continue the same logical objective in the same session and measure whether reuse reduces reconstruction/context overhead without importing stale state.
13. Exercise one fork/fresh case for changed objective, model escalation, or independent judgment.
14. Confirm directory affinity by demonstrating that a call from an unrelated caller cwd still executes against the explicit intended repo root.
15. Confirm that session lookup works from the local pointer/index plus OpenCode runtime without consulting canonical documentation for machine-specific state.
16. Record prompt/cache behavior only if surfaced by the provider/runtime; otherwise mark it unobservable rather than inferred.

# Phase D — acceleration / parallelism proof

17. Exercise one independent parallel candidate where OpenCode can work while the parent or deterministic tooling performs another independent branch.
18. Compare elapsed/coordination cost qualitatively or quantitatively against sequential parent-only execution.
19. Reject parallelism explicitly if join/coordination cost exceeds the benefit.
20. Confirm that parent synthesis can retrieve deeper execution evidence from OpenCode on demand rather than ingesting the entire session into its context.

# Phase E — packaging decision

21. Decide `NO NEW COMPONENT`, `SMALL ADAPTER`, or `ADAPTER + QUALIFIED SKILL/COMMAND`.
22. Prefer no new component when explicit CLI/runtime controls plus existing task/external-handoff semantics are sufficient.
23. If a small adapter is justified, keep its contract executor-neutral where practical so future harnesses can reuse the semantic routing boundary without forcing a plugin framework.
24. If local runtime bookkeeping is required, keep it ignored, minimal, reconstructable where practical, and separate from canonical documentation.
25. Do not create a long-running routing service unless repeated evidence demonstrates process-start/session-resolution overhead is materially important and a persistent OpenCode server actually improves it.
26. Do not create a new aggregate context database; if a unified context command is useful, implement it as a read-only view over existing owners.

# Validation matrix

| Area | Required evidence |
| --- | --- |
| Existing skill audit | `external-handoff` boundary understood; no duplicate executor skill created |
| Runtime | exact OpenCode version and actual supported controls recorded |
| Directory | explicit intended repo root used independent of caller cwd |
| Session | explicit reuse plus one fork/fresh case observed |
| Session ownership | raw execution history remains in OpenCode rather than copied into canonical docs |
| Runtime index | any local session/run bookkeeping is ignored, minimal, and not treated as canonical truth |
| Model | requested vs actual model route recorded where observable |
| Validation | bounded task output deterministically checked |
| Economics | at least one case tests whether cheaper/faster execution is acceptable under strong validation |
| Parallelism | one independent candidate tested or rejected with evidence |
| Fallback | invalid/unsupported executor/model/session control degrades predictably |
| Parent authority | architecture and final acceptance remain with parent |
| Memory | AgentMemory may observe execution but is not canonical session registry or truth |
| Project truth | target repository remains authoritative for actual code/data/project state |
| Progressive access | deeper OpenCode/AgentMemory context is retrieved only when relevant rather than bootstrapped wholesale |
| Packaging | no workflow/router service/agent/aggregate context database created without repeated evidence |

# Stop conditions

Stop or fall back to Codex/main when:

- OpenCode runtime controls required by the lane are unsupported or not observable enough for safe use;
- explicit directory/session affinity cannot be guaranteed;
- model routing is unstable or silently ignored;
- validation is too weak for the consequence of the task;
- session reuse imports materially stale/conflicted context;
- coordination overhead exceeds the acceleration benefit;
- runtime bookkeeping begins duplicating OpenCode sessions, AgentMemory, or project Git truth;
- packaging pressure starts creating a second orchestration framework.

# Definition of done

Issue #8 has a proven execution-routing slice when a real bounded task demonstrates that OpenCode can be selected intentionally as a secondary executor with explicit directory, model, and session affinity; its result is independently validated; reuse/fork/fresh semantics are evidenced; runtime execution history remains owned by OpenCode; only minimal local pointers/bookkeeping are introduced where needed; canonical GitHub retains durable accepted semantics rather than runtime exhaust; progressive context retrieval works; fallback to Codex remains clean; and the final implementation is no larger than the runtime evidence justifies.
