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

# Current design decision

The preferred experimental substrate is **AgentMemory**, not a new in-house memory service.

This is a candidate selection, not an accepted runtime dependency.

Why it is the current best fit:

- it is explicitly built for persistent memory across coding-agent sessions;
- it already supports Codex CLI and OpenCode through native hooks/plugins plus MCP;
- it supports scoped lessons/observations and selective context injection rather than requiring raw-history replay;
- one shared memory service can support multiple harnesses without copying memory into this control-plane repository;
- it can be evaluated behind an existing runtime boundary and removed if the value is not demonstrated.

Alternatives reviewed:

- **Mem0**: strong general memory layer and useful benchmark work, but its open-source MCP server is archived and its broader product direction is less directly aligned with the local multi-harness coding-agent workflow.
- **Letta / Letta Code**: sophisticated stateful-agent and memory-first harness, but adopting it would introduce a competing agent runtime and self-modifying context model rather than a bounded memory substrate.
- **Graphiti**: strong temporal context-graph retrieval with provenance and bi-temporal facts, but it introduces graph infrastructure that is not justified by the present continuity problem and would violate the current no-duplicate-memory-graph discipline.
- **LangGraph Memory Service**: conceptually relevant, but the example repository is archived and should not become a new dependency.

Do not create a custom vector database, graph database, memory agent, or memory workflow merely because these projects demonstrate those patterns.

# Activation gate

Do not activate persistent memory merely because AgentMemory exists or because Project Memory is imperfect.

Activation requires evidence after #2 and #31/session-orientation semantics are exercised:

1. at least one **repeated** continuity failure, or a measurable targeted-retrieval gap, survives normal orientation from scoped instructions + accepted/live canonical state;
2. the missing context is genuinely historical/experiential rather than current repository truth or scientific source evidence;
3. targeted retrieval is likely to change planning/review quality enough to justify runtime and synchronization cost.

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

Memory should therefore be **on-demand retrieval**, not a mandatory session bootstrap dump.

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

Do not let AgentMemory auto-promote observations into control-plane policy.

# Execution phases after activation

1. Collect and classify concrete continuity/retrieval failures.
2. Confirm that canonical state, Project Memory, Git history, Issue/PLAN links, Wiki/RAG, or normal #2 acquisition do not already solve them.
3. Install/connect AgentMemory only in the local runtime boundary required for the experiment; do not vendor it into this repository.
4. Probe the actually installed AgentMemory/Codex/OpenCode integration surface rather than assuming README claims map exactly to the local runtime.
5. Define the smallest selective recall query/input and compact return shape needed by the parent.
6. Exercise at least:
   - one useful historical recall case;
   - one no-recall-needed case;
   - one stale/contradicted-memory case;
   - one project-scope isolation case.
7. Compare planning/review quality and context/token overhead against the no-memory baseline.
8. Decide `KEEP`, `DEFER`, or `REMOVE / NO INTEGRATION`.
9. Only if kept, define capture/deprecation/forget and explicit promotion semantics from actual runtime evidence.

# Token and runtime efficiency

Prefer retrieval of a small ranked set of observations/lessons rather than session transcript replay.

Use deterministic/local filtering where the memory substrate exposes it; reserve model reasoning for relevance judgment, conflict interpretation, planning, and promotion decisions.

Do not add a second model-driven summarization loop if AgentMemory already provides adequate extraction/ranking. Avoid duplicate embeddings/indexes unless a measured retrieval gap demonstrates the need.

# Validation

- memory never overrides canonical/live state;
- recall is conditional, selective, scoped, and provenance-aware;
- a no-memory path remains the normal valid outcome;
- project/global isolation behaves as intended;
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
- memory adds more synchronization, stale-context, latency, token, or maintenance ambiguity than value;
- safe project/global scoping cannot be demonstrated;
- the integration pressures the control plane toward a competing agent runtime or duplicate graph/RAG architecture.

# Definition of done

Persistent memory is either:

1. proven useful for a concrete repeated continuity/retrieval gap using AgentMemory as a bounded experimental substrate, with selective recall, authority boundaries, promotion governance, isolation, and measurable overhead; or
2. explicitly deferred/rejected with evidence, while Project Memory + canonical orientation remain sufficient.

No new permanent memory architecture is accepted solely by completing this PLAN.
