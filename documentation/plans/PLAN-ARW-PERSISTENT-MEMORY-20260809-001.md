---
id: PLAN-ARW-PERSISTENT-MEMORY-20260809-001
issue: 9
status: deferred
activation_gate: repeated-continuity-or-retrieval-gap-after-core-orientation
scope: persistent-memory-promotion
preferred_candidate: agentmemory
candidate_status: experimental-substrate-only
---

# Objective

Integrate persistent memory only if real repeated work shows a continuity/history or targeted-retrieval gap that CURRENT/DECISIONS/Git/Goal–Plan links, Project Memory, and normal scoped orientation do not already solve.

Persistent memory is an experience/history context source. It is not canonical authority, scientific evidence, or a replacement for repository orientation.

If AgentMemory is already installed or running locally, treat it as an existing external capability to probe and consume rather than reinstalling, vendoring, or rebuilding a memory subsystem in this repository.

# Current design decision

The preferred experimental substrate is **AgentMemory**, not a new in-house memory service.

This is a candidate selection, not an accepted runtime dependency.

Why it is the current best fit:

- it is explicitly built for persistent memory across coding-agent sessions;
- it already supports Codex CLI and OpenCode through hooks/plugins plus MCP;
- it supports scoped lessons/observations and selective recall rather than requiring raw-history replay;
- one shared memory service can support multiple harnesses without copying memory into this control-plane repository;
- it can be evaluated behind an existing runtime boundary and removed if the value is not demonstrated;
- upstream already exposes health, sessions, recall/search, replay/import, consolidation/backfill, and provenance-oriented surfaces that should be reused before custom machinery is considered.

Alternatives reviewed:

- **Mem0**: strong general memory layer and useful benchmark work, but its open-source MCP server is archived and its broader product direction is less directly aligned with the local multi-harness control-plane boundary.
- **Letta / Letta Code**: sophisticated stateful-agent and memory-first harness, but adopting it would introduce a competing agent runtime and self-modifying context model rather than a bounded memory substrate.
- **Graphiti**: strong temporal context-graph retrieval with provenance and bi-temporal facts, but it introduces graph infrastructure that is not justified by the present continuity problem and would violate the current no-duplicate-memory-graph discipline.
- **LangGraph Memory Service**: conceptually relevant, but the example repository is archived and should not become a new dependency.

Do not create a custom vector database, graph database, memory agent, memory workflow engine, raw-chat mirror, or mandatory observation database merely because these projects demonstrate those patterns.

# Governing memory model

Use three runtime primitives only:

```text
CAPTURE
RECONCILE
RECALL
```

Their responsibilities are deliberately distinct:

```text
CAPTURE
= collect useful runtime observations while work occurs

RECONCILE
= verify recent memory/session completeness and repair safe gaps

RECALL
= retrieve a small relevant historical packet only when planning/review needs it
```

Do not equate capture success with consolidation success, and do not equate either with current truth.

# Activation gate

Do not activate persistent memory merely because AgentMemory exists or because Project Memory is imperfect.

Activation requires evidence after #2 and #31/session-orientation semantics are exercised:

1. at least one **repeated** continuity failure, or a measurable targeted-retrieval gap, survives normal orientation from scoped instructions + accepted/live canonical state;
2. the missing context is genuinely historical/experiential rather than current repository truth or scientific source evidence;
3. targeted retrieval is likely to change planning/review quality enough to justify runtime and synchronization cost.

If AgentMemory is already running locally, the activation work becomes a **reuse experiment**, not an installation project. Probe the existing runtime first.

Project Memory is treated as cheap opportunistic recall, not as a complete/queryable history database. A gap exists only when explicit selective historical retrieval would materially improve the task.

# Intended session integration

Use a progressive, token-efficient recall path:

```text
TASK
→ Project/runtime conversational recall when available
→ orient from minimal canonical/live state
→ context sufficient?
    → YES: reason/plan directly
    → NO: classify the missing context
         → current repository/state gap: #2 / canonical acquisition
         → historical experience gap: targeted AgentMemory recall
         → scientific evidence gap: Wiki/RAG source evidence
         → external/current gap: appropriate external source
→ compact context packet
→ parent reason / plan / critique
```

Memory should therefore be **on-demand retrieval**, not a mandatory session-bootstrap dump.

# Runtime capture policy

Capture should be automatic where the host integration is reliable, but AgentMemory must remain non-blocking for the core control plane.

Preferred operating mode:

```text
CAPTURE = ON where validated
AUTO CONTEXT INJECTION = OFF or conservative by default
RECALL = on demand
MEMORY FAILURE = degraded capability, not task failure
```

A memory outage must not prevent ordinary coding, configuration, local analysis, or repository work from continuing when memory is not required for correctness.

Do not rely on manual `/remember` as the primary capture mechanism. Manual remember/commit-context/history actions are useful for important recovery or explicit promotion candidates, not as the normal event stream.

# Runtime health assertion

Seeing an MCP tool is not sufficient proof that the durable AgentMemory service is healthy.

A local acceptance probe must distinguish:

```text
real AgentMemory server reachable
vs
MCP fallback/local-only mode
vs
server unavailable
```

The first bounded runtime reconnaissance should record:

- installed AgentMemory version;
- persistent data directory;
- server health/liveness;
- full-server versus local-fallback MCP mode;
- actually exposed MCP tools;
- connected hosts (Codex CLI/Desktop, OpenCode, Hermes, others if relevant);
- actually firing hooks/events for each host;
- whether automatic context injection is enabled;
- project naming/scoping behavior;
- agent isolation settings where used;
- restart persistence behavior.

Prefer deterministic shell/API probes for this inventory. Do not use model inference when the runtime can answer directly.

## Local reconnaissance record — 2026-08-10

The existing local installation was probed in place; no package, configuration,
hook, or repository runtime surface was added.

| Check | Result | Interpretation |
| --- | --- | --- |
| installed version | AgentMemory `0.9.28` | existing substrate confirmed |
| server liveness | `GET /agentmemory/livez` returned `status=ok` | real local server, not MCP-only fallback |
| provider/embedding mode | provider `noop`; BM25-only; auto-compress and context injection off | deterministic degraded/zero-LLM mode |
| persisted state | one previously captured memory and one completed synthetic session loaded; the same memory ID was present across two fresh service starts | restart persistence observed for this fixture |
| capture fixture | the earlier bounded hook lifecycle produced one completed `.codex` session with two observations | hook-to-server path works when explicitly invoked; native host auto-capture remains unproven |
| useful recall | targeted `smart-search` returned the bounded canonical-state memory | selective recall path works |
| no-recall | unrelated query returned an empty result set | ordinary no-memory path remains valid |
| provenance | `POST /agentmemory/verify` succeeded but returned `citationCount=0` | this fixture is not source-provenance evidence |
| diagnostics | 14 checks passed; one warning reported that the only latest memory has no project scope | scope/attribution is not accepted |
| scope comparison | REST search returned the unscoped fixture for both `.codex` and `/tmp/unrelated-project` filters | project isolation is not proven and currently leaks unscoped records |

The probe therefore demonstrates a healthy, persistent experimental substrate,
bounded capture/recall behavior, and explicit degradation modes. It does not
demonstrate automatic Codex/OpenCode host capture, consolidation, project or
agent isolation, contradiction handling, or a material repeated continuity gap.
The synthetic record remains a test fixture in the external AgentMemory store;
it is not canonical repository state and is not deleted without explicit
confirmation.

# Memory lifecycle integrity states

Treat recent sessions conceptually as having three independent integrity levels:

```text
CAPTURED
= raw observations/events exist

CONSOLIDATED
= session summary/lessons/memory artifacts exist where expected

VERIFIED
= session is visible in the intended project/scope and can be recalled from the durable service
```

Examples:

- observations exist but summary is missing → captured, not consolidated;
- summary exists under wrong project scope → consolidated but not verified;
- known host session has no AgentMemory session/observations → capture gap;
- AgentMemory has a session but the service is in fallback/nonpersistent mode → not accepted as durable capture.

Do not collapse these states into a single `saved=true` claim.

# Failure taxonomy

Classify memory failures before repair:

## Capture gap

A host session/work period occurred but expected observations are absent.

Likely causes include missing/silent hooks, daemon outage, host lifecycle mismatch, wrong project resolution, or integration breakage.

## Consolidation gap

Raw observations exist but summarization/crystallization/consolidation did not complete or produced no durable higher-level memory.

This may often be safely backfilled if the raw observations remain available.

## Scope / attribution gap

Observations exist but are attached to the wrong project, agent, or session identity, making later recall misleading or invisible.

## Historical gap

An older session predates AgentMemory capture or was never observed by it.

Recovery depends on surviving host transcripts or durable external evidence. Do not fabricate missing original-session content.

## Persistence / fallback gap

The MCP surface appears available but durable server state is unavailable, fallback storage is active, or restart loses state.

Treat this as degraded memory even if individual MCP calls succeed.

# Reconciliation loop

Do not rely solely on host end-of-session hooks. Host lifecycle events are not guaranteed to map cleanly to a logical work-session boundary.

Use a lightweight periodic or end-of-active-work reconciliation pass:

```text
AgentMemory health
→ recent AgentMemory sessions
→ compare against available host/session activity metadata when possible
→ classify each anomaly
→ repair deterministic/safe cases
→ flag unrecoverable or ambiguous gaps
→ NO ACTION when healthy
```

The reconciliation pass should look for at least:

- observations without a corresponding usable session record;
- recent sessions with observations but no expected summary/consolidation;
- stale-open or prematurely-completed sessions;
- suspicious zero-observation sessions;
- project/agent attribution mismatches;
- consolidation failures;
- fallback-mode capture that was mistaken for durable storage;
- host sessions missing entirely from AgentMemory where an independent host index makes comparison possible.

Use shell/API filtering first. Model reasoning is reserved for ambiguous classification or interpretation.

# Independent gap detection

AgentMemory cannot discover a session it never observed. Therefore complete gap detection requires an independent lightweight host/session index when the host exposes one.

Prefer comparing metadata only:

```text
host session IDs / project / timestamps
vs
AgentMemory session IDs / project / timestamps
```

Do not duplicate raw transcripts merely for gap detection.

A mismatch such as:

```text
host:   A B C D
memory: A B   D
```

should flag `C` as a candidate capture gap for investigation/backfill.

If a host does not expose stable session metadata, record that limitation instead of inventing coverage.

# Historical recovery / backfill

Use the smallest trustworthy source available.

## Existing live session

If AgentMemory starts after a still-active session, explicitly preserve only important context/lessons as needed, then continue automatic capture from that point forward.

## Closed session with surviving transcript

Where an upstream-supported importer/replay path exists for that host, prefer import → summarize/backfill → consolidate instead of custom parsing.

Probe the installed version and host-specific capability first. Do not assume Claude-Code JSONL import semantics also apply to Codex or other hosts.

## No surviving transcript

Do not reconstruct a fake session history from Git.

Durable evidence such as commits, PRs, Issues, PLANs, or HANDOFFs may generate a derived historical observation/lesson, but provenance must state that the source is durable repository evidence rather than the original conversation/session.

# Memory record semantics

Prefer compact experience records over raw conversation storage as planning context.

Candidate useful record types include:

- runtime failure/limitation observations;
- implementation lessons;
- routing/delegation outcomes;
- recurring workarounds or friction;
- user/project preferences that materially affect execution;
- accepted historical rationale references where canonical state alone does not explain the lesson.

A useful recalled record should carry enough provenance to identify its source/session/task and confidence/status where available.

Do not use memory to establish:

- current repository truth;
- accepted architectural decisions;
- scientific claims;
- unresolved brainstorming as policy;
- machine/path discovery that current runtime/project instructions should resolve.

# Authority and contradiction handling

Authority remains:

```text
current scoped/runtime instructions
→ accepted CURRENT / DECISIONS where applicable
→ live Issue / PLAN / PR / Git / project state
→ targeted historical memory
→ older raw/compacted conversational history
```

If memory conflicts with canonical/live state:

```text
surface conflict
→ canonical/live authority wins for current truth
→ preserve memory only as historical evidence/lesson if still useful
→ mark/deprecate/forget stale memory when supported and justified
```

No silent reconciliation in favor of memory.

# Knowledge promotion

Memory capture and durable promotion are separate operations.

```text
OBSERVATION / MEMORY
→ recurrence/materiality check
→ PROPOSE
→ REVIEW
→ ACCEPT / DEFER / NO CHANGE
→ UPDATE the correct owner
```

Possible accepted destinations:

- CURRENT for accepted current state;
- DECISIONS for durable architectural rationale;
- Issue / PLAN for execution intent;
- Wiki or source corpus only through their own evidence/provenance rules;
- reusable skill/policy candidate only after demonstrated reuse;
- remain memory when it is useful historical experience but not canonical truth.

AgentMemory may help detect recurrence. It must not auto-promote observations into control-plane policy.

# Tool and surface minimization

Do not expose or operationalize AgentMemory's entire tool catalog merely because it exists.

For the initial control-plane experiment, prefer the smallest read-oriented recall/session surface needed to prove value. Candidate capabilities are:

- targeted smart search / recall;
- recent session inspection;
- provenance/verification where it materially improves trust.

Write/delete/action-graph/lease/signal/sentinel/routine capabilities are out of scope unless a separate proven requirement emerges.

Use host/plugin/MCP allowlists where supported to reduce tool-selection noise and accidental authority expansion.

# Execution phases after activation

## Phase A — Local reconnaissance

1. Detect whether AgentMemory is already installed/running locally.
2. Record version, server health, persistent data location, full-server vs fallback mode, connected hosts, exposed tools, hook/event activity, context-injection mode, project/agent scope, and restart persistence.
3. Do not reinstall or rewrite configuration if the existing runtime is healthy enough to probe.

## Phase B — Capture reliability proof

4. Run one fresh bounded Codex session and one fresh bounded OpenCode session where available.
5. Confirm session registration plus observation progression rather than merely tool discovery.
6. Intentionally inspect memory state after several turns/tools and after a normal session/phase boundary.
7. Restart/reconnect the memory service once and confirm expected durable state survives.

## Phase C — Reconciliation proof

8. Exercise or identify at least one representative anomaly class: capture gap, consolidation gap, attribution gap, or degraded/fallback condition. Natural evidence is preferred; do not manufacture destructive failure when a harmless fixture/probe can establish the contract.
9. Demonstrate that a reconciliation pass classifies the anomaly and either safely repairs/backfills it or reports it honestly.
10. If host session metadata is available, compare it against AgentMemory recent sessions to test whole-session gap detection.

## Phase D — Recall value proof

11. Exercise:
   - one useful historical recall case;
   - one no-recall-needed case;
   - one stale/contradicted-memory case where canonical/live state wins;
   - one project-scope isolation case.
12. Compare planning/review quality and token/context/runtime overhead against a no-memory baseline.

## Phase E — Acceptance decision

13. Decide `KEEP`, `DEFER`, or `REMOVE / NO INTEGRATION`.
14. Only if kept, define the minimal ongoing capture/reconciliation cadence and capture/deprecation/forget/promotion semantics from actual runtime evidence.
15. Do not introduce a custom memory agent, database, workflow engine, or repository mirror as part of acceptance.

# Token and runtime efficiency

Prefer retrieval of a small ranked set of observations/lessons rather than session transcript replay.

Use deterministic/local filtering where the memory substrate exposes it; reserve model reasoning for relevance judgment, conflict interpretation, planning, and promotion decisions.

Do not add a second model-driven summarization loop if AgentMemory already provides adequate extraction/ranking/consolidation.

Prefer reconciliation that processes only anomalies/failures. Successful healthy sessions should normally collapse to `NO ACTION` rather than consume model context.

Avoid duplicate embeddings/indexes unless a measured retrieval gap demonstrates the need.

# Validation matrix

| Area | Required evidence |
| --- | --- |
| Existing capability | installed/running AgentMemory state is probed before any installation/change |
| Version | exact installed version recorded |
| Durable server | health/liveness proves real server rather than fallback-only mode |
| Persistence | representative captured state survives service restart/reconnect |
| Capture | fresh host session is registered and observations progress |
| Consolidation | representative captured session reaches expected summary/lesson state or gap is classified |
| Scope | project/agent isolation works as intended |
| Reconciliation | recent-session anomalies can be detected and safe cases repaired/backfilled |
| Missing-session detection | host-vs-memory comparison used where host metadata exists; limitation recorded otherwise |
| Recall | useful targeted historical case improves planning/review or the experiment records no material benefit |
| No-recall path | representative task proceeds correctly without memory retrieval |
| Conflict | stale/contradicted memory loses to canonical/live state |
| Token/runtime cost | bounded recall and reconciliation overhead compared with baseline |
| Removal | disabling AgentMemory leaves core control-plane operation functional |
| Scope discipline | no memory agent, duplicate DB/graph/RAG, canonical mirror, or mandatory raw-history ingestion introduced |

# Validation invariants

- memory never overrides canonical/live state;
- capture success is not inferred solely from hook/plugin presence;
- recall is conditional, selective, scoped, and provenance-aware;
- a no-memory path remains the normal valid outcome;
- memory outages degrade continuity but do not block unrelated work;
- project/global and agent isolation behave as intended;
- contradictions surface explicitly;
- stale/deprecated observations do not silently dominate recall;
- scientific claims still require source evidence;
- promotion is proposal/review/accept based;
- context/token overhead is measured against a baseline representative task;
- no duplicate memory-agent, graph, vector store, workflow engine, or canonical-state mirror is introduced;
- removing/disabling AgentMemory leaves the core control plane functional.

# Stop conditions

Stop with `NO INTEGRATION` or keep the PLAN deferred if:

- #2/#31 + canonical artifacts solve observed continuity adequately;
- Project Memory is sufficient for the actual continuity need;
- targeted memory recall does not materially improve planning/review;
- capture cannot be made observable enough to distinguish healthy durable service from silent fallback/degradation;
- reconciliation cannot safely identify or repair important gaps;
- memory adds more synchronization, stale-context, latency, token, or maintenance ambiguity than value;
- safe project/global or agent scoping cannot be demonstrated;
- the integration pressures the control plane toward a competing agent runtime or duplicate graph/RAG architecture.

# Execution handoff to Codex

When #9 is activated, Codex should start with **runtime reconnaissance**, not implementation.

Required handoff:

```text
repository: taixuann/codex-chatpgt
issue: #9
plan: documentation/plans/PLAN-ARW-PERSISTENT-MEMORY-20260809-001.md
local runtime: resolve actual installed AgentMemory + Codex/OpenCode state
scope: probe → capture proof → reconciliation proof → targeted recall proof
writes: only after evidence shows a missing reusable control-plane artifact
```

Codex must report:

- actual installed version/configuration and host integration state;
- whether AgentMemory was already active before the run;
- exact health/fallback/persistence evidence;
- actual hooks/events observed per host;
- session/observation/consolidation evidence;
- any missing-session or attribution gaps;
- reconciliation/backfill evidence;
- targeted recall examples and token/context overhead;
- deviations, blockers, and unsupported assumptions;
- `KEEP`, `DEFER`, or `REMOVE / NO INTEGRATION` recommendation.

Do not treat README capability claims as local runtime evidence.

# Definition of done

Persistent memory is either:

1. proven useful for a concrete repeated continuity/retrieval gap using the existing or experimentally connected AgentMemory substrate, with observable capture, health/fallback detection, reconciliation/backfill semantics, selective recall, authority boundaries, promotion governance, isolation, persistence, and measurable overhead; or
2. explicitly deferred/rejected with evidence, while Project Memory + canonical orientation remain sufficient.

No new permanent memory architecture is accepted solely by completing this PLAN.
