---
id: PLAN-ARW-SESSION-CONTINUITY-EVOLUTION-OBSERVATION-20260809-001
issue: 31
status: execution-ready
date: 2026-08-09
scope: session orientation, reorientation, and evolution observation
---

# Sustainable session continuity and evolution observation

## Objective

Add the smallest semantic/runtime contract needed so the control plane behaves sustainably across both fresh and long-running logical work sessions:

```text
FRESH SESSION
→ ORIENT
→ EXECUTE
→ REORIENT ON MATERIAL STATE CHANGE
→ VALIDATE / REVIEW
→ EVOLUTION CHECK
→ MINIMAL DURABLE RECONCILIATION
```

This PLAN executes Issue #31. It must improve reliability without creating a session subsystem, new memory platform, autonomous evolution agent, checkpoint artifact family, or duplicate orchestration framework.

## Accepted ownership boundaries

Do not reopen these:

- #2 owns **how** extra repository/context evidence is acquired after insufficiency is detected.
- #8 owns parent-vs-subagent/model/reasoning/parallelism/fallback routing.
- #9 owns persistent memory only if real continuity pain remains.
- #10 is the preferred real-project consumer/pilot.
- #11 owns recurrence/materiality thresholds and promotion governance for self-evolution.
- #15 owns execution mechanics for accepted system changes.
- #24 already owns component quality, skill discovery metadata, AGENTS scoping, agent contracts, and component linking.

#31 owns only:

```text
WHEN TO ORIENT
WHEN TO REORIENT
WHEN TO CHECK FOR EVOLUTION SIGNALS
HOW TO HAND THOSE SIGNALS TO EXISTING OWNERS
```

## External constraints from current official guidance

Use current OpenAI guidance as design constraints, not implementation mandates:

1. Codex builds the scoped `AGENTS.md` instruction chain at the start of a run/session and closer files override broader guidance. Keep guidance small and local.
   - https://developers.openai.com/codex/guides/agents-md
   - https://developers.openai.com/codex/concepts/customization
2. Start with one manager/parent agent and add specialists only when isolation, ownership, tools, policy, or clarity materially improves. Manager-style bounded specialist calls are preferred when the parent should retain synthesis.
   - https://developers.openai.com/api/docs/guides/agents/orchestration
3. Sessions/history are one continuation mechanism, not canonical truth. Resumable state should be preserved deliberately; long history may be compacted rather than replayed indefinitely.
   - https://developers.openai.com/api/docs/guides/agents/running-agents
   - https://openai.github.io/openai-agents-js/guides/sessions/
4. OpenAI context-engineering examples recommend trimming/summarization for long interactions while preserving milestones, decisions, constraints, contradiction checks, and useful tool lessons.
   - https://developers.openai.com/cookbook/examples/agents_sdk/session_memory

Do not import Agents SDK session machinery into this repository solely because those primitives exist.

## Governing distinctions

```text
CHAT THREAD ≠ LOGICAL WORK SESSION
CONVERSATION HISTORY ≠ CANONICAL / LIVE STATE
SESSION CONTINUITY ≠ PERSISTENT MEMORY
EVOLUTION OBSERVATION ≠ EVOLUTION PROMOTION
CHECKPOINT ≠ ARTIFACT
SUBAGENT AVAILABLE ≠ SUBAGENT REQUIRED
```

A logical session is primarily:

```text
objective + scope + accepted/live task state
```

not a browser/chat container.

---

# Phase 0 — Inspect live runtime and current semantics

Before editing:

1. Read:
   - root `AGENTS.md`;
   - scoped `agents/AGENTS.md`, `skills/AGENTS.md`, `workflows/AGENTS.md`;
   - `documentation/OPERATING-WORKFLOW.md`;
   - `documentation/CURRENT.md`;
   - `documentation/DECISIONS.md`;
   - Issue #31 and this PLAN;
   - current `shared-session-closeout` or equivalent skill.
2. Inspect actual Codex session/runtime behavior available locally:
   - when AGENTS are loaded/reloaded;
   - whether session history/compaction/resume is exposed;
   - whether current live Git/GitHub state can diverge from chat assumptions;
   - whether closeout is automatically invoked, discoverable, or only explicit.
3. Do not infer capabilities from documentation alone. Record runtime limitations in PR/Issue evidence, not a new report file.

---

# Phase 1 — Add fresh-session orientation semantics

Update the smallest canonical surface, expected primarily `documentation/OPERATING-WORKFLOW.md`.

For fresh **non-trivial** logical work:

```text
1. identify repository/project and intended scope
2. load/apply scoped instructions
3. resolve minimal accepted state relevant to the request
4. resolve current task from user + Issue/PLAN/PR/project state
5. inspect live external/repository state only when correctness depends on it
6. test context sufficiency
7. invoke #2-style context acquisition only when insufficiency is material
8. route capability/delegation/execution
```

### Required properties

- Progressive disclosure: do not bulk-read all docs/issues/wiki/memory.
- Trivial tasks may skip most orientation steps.
- Do not create `session-bootstrap` as a skill merely to encode this lifecycle.
- Do not duplicate the AGENTS instruction chain into another durable file.
- Current/live state wins over stale conversational assumptions.

### Root AGENTS rule

Add at most one compact repo-wide invariant if needed to guarantee fresh orientation. Do not copy the full procedure from `OPERATING-WORKFLOW.md`.

---

# Phase 2 — Add event-driven reorientation checkpoints

Long-running work must not rely on raw conversation continuity alone.

Define material triggers rather than arbitrary turn counts.

Candidate triggers:

- objective/scope changes materially;
- one work phase completes and another begins;
- Issue/PR/branch/accepted state changes externally;
- a consequential mutation follows extended discussion;
- material validation failure or repeated repair changes assumptions;
- new evidence contradicts earlier reasoning;
- the parent is uncertain which state/artifact is authoritative;
- current chat context contains substantial superseded brainstorming/noise.

At a checkpoint reconstruct only:

```text
objective
accepted/live state
material changes
open constraints/blockers
authoritative artifacts
need for additional context acquisition
```

### Explicit non-requirements

Do not create:

- checkpoint files;
- checkpoint commits;
- checkpoint Issues/comments by default;
- checkpoint subagents;
- fixed `every N turns` rules without real evidence.

A checkpoint is usually an internal orientation action.

---

# Phase 3 — Define history/compaction authority

Clarify priority when continuing long work:

```text
1. system/runtime instructions
2. scoped AGENTS normative rules
3. accepted CURRENT / DECISIONS where relevant
4. live Issue / PLAN / PR / Git / project state
5. recent unresolved conversation context
6. older raw/compacted conversational history
```

If runtime-provided compaction/resume exists, use it rather than building a custom summarization subsystem.

Conversation compaction may preserve continuity but never becomes canonical state.

When summary/history conflicts with live/canonical state:

```text
surface conflict
→ prefer authoritative state
→ reorient
```

Persistent cross-session memory remains #9 and is not required here.

---

# Phase 4 — Integrate delegation preconditions without duplicating #8

Before spawning a bounded worker, the parent should have sufficiently fresh:

- objective;
- scope;
- required capability;
- child context subset;
- expected return contract;
- reason delegation adds value.

Delegation is justified by one or more:

```text
context isolation
independent judgment
meaningful independent parallelism
permission boundary
specialized tool/capability
protecting parent context from noisy repetitive work
```

Do not spawn merely because:

```text
task is long
workflow has multiple stages
specialist exists
skill exists
previous session spawned the same specialist
```

Do not encode model/reasoning/parallelism policy here. That remains #8.

---

# Phase 5 — Add bounded completion evolution check

Before meaningful accepted completion of consequential work, perform a small check for material or recurring friction.

Candidate signals:

```text
context acquisition failure
stale-session/reorientation failure
skill routing ambiguity or missing trigger
AGENTS ambiguity/wrong scope
unnecessary workflow ceremony
missing/weak deterministic validation
recurring workaround/manual repair
agent/delegation boundary failure
missing capability
unused/redundant skill/workflow/agent/validator
```

The normal outcome should often be:

```text
NO ACTION
```

Signal handling:

```text
one-off/local
→ repair locally or leave in existing execution evidence

possible recurring/material
→ preserve minimally as an evolution candidate in the existing owner

mature repeated/material evidence
→ hand to #11

accepted change
→ implement through #15/general change lifecycle
```

### Critical rule

Observation must never directly mutate global policy, AGENTS, skills, workflows, agents, or routing.

---

# Phase 6 — Ensure negative evidence can simplify the system

The evolution check must detect evidence for removal/simplification as well as additions.

Examples:

- a skill has no recurring valid trigger;
- a workflow is never useful despite relevant work;
- governed lifecycle ceremony exceeds risk/consumer value;
- an agent never earns spawn overhead;
- validators duplicate stronger checks;
- guidance repeatedly harms rather than helps routing.

Do not automatically delete. Route material repeated evidence to #11/#15 as appropriate.

---

# Phase 7 — Align session-closeout only where useful

Inspect `shared-session-closeout` (or current equivalent).

If it remains a real recurring capability:

- add the bounded evolution check to consequential closeout;
- ensure it can return `NO ACTION`;
- keep ordinary chat endings out of scope;
- prefer Issue/PLAN/PR/CI reconciliation over legacy goal/change wrappers for ordinary repository work;
- do not make closeout the only place the global evolution observation rule exists.

If closeout is not reliably auto-discovered/invoked, the global operating semantics must still guarantee the check at meaningful completion.

Do not create another session skill.

---

# Phase 8 — Add only honest validation

Prefer semantic/fixture validation only where behavior can be tested honestly.

Potential tests:

1. fresh-session orientation examples:
   - trivial task → minimal/no bootstrap;
   - non-trivial repo task → scoped instructions + relevant state;
   - insufficient context → handoff to #2 context acquisition.
2. checkpoint examples:
   - external PR merge changes state → reorient;
   - unchanged state → continue without ceremony.
3. authority conflict:
   - stale conversational assumption conflicts with live GitHub → live state wins.
4. evolution check:
   - no recurring/material friction → `NO ACTION`;
   - repeated routing ambiguity → candidate to #11, not direct mutation;
   - redundant ceremony → simplification candidate.

Do not claim static fixtures prove behavioral runtime behavior.

If a deterministic validator adds no real guarantee, do not create it.

---

# Phase 9 — Independent review for overengineering and missing guarantees

Review must explicitly look for both failure modes:

## Too little

- orientation remains optional prose that may not execute;
- long sessions have no material refresh trigger;
- evolution check exists only inside a skill that may never load;
- observations have no handoff to #11/#15;
- state authority remains ambiguous.

## Too much

- session manager/database introduced;
- mandatory summary/checkpoint artifacts;
- fixed turn counters without evidence;
- auto-created Issues from friction;
- autonomous mutation/evolution agent;
- duplicated routing policy from #8;
- memory implementation from #9;
- new workflow engine.

Repair only material findings.

---

# Required durable updates

Expected minimal accepted-state changes:

- `documentation/OPERATING-WORKFLOW.md` for session/reorientation/evolution semantics;
- root/scoped `AGENTS.md` only if one concise normative invariant is required;
- `shared-session-closeout` only if its actual trigger/use justifies alignment;
- `CURRENT.md` and `DECISIONS.md` only for accepted deployed semantics;
- #2/#8/#10/#11/#15 comments for ownership/cross-linking.

Do not create:

- session registry;
- session schema;
- checkpoint schema;
- evolution log;
- observation database;
- session workflow;
- evolution workflow;
- new agent;
- new skill unless unexpected real runtime evidence proves a distinct recurring contract.

---

# Acceptance mapping

Issue #31 is complete only when:

- AC-01: fresh non-trivial sessions have a minimal orientation contract;
- AC-02: context sufficiency can hand to #2 without duplicating #2;
- AC-03: long work has event-driven reorientation triggers;
- AC-04: live/canonical state overrides stale conversation assumptions;
- AC-05: compaction/history remains continuity context, not authority;
- AC-06: delegation occurs only after sufficiently fresh orientation and #8 ownership is preserved;
- AC-07: consequential completion runs a bounded evolution check that may return `NO ACTION`;
- AC-08: observations never mutate global architecture directly and hand off to #11/#15 appropriately;
- AC-09: simplification/removal evidence is first-class;
- AC-10: no mandatory checkpoint/evolution artifact family is added;
- AC-11: no session/memory/evolution platform is built;
- AC-12: #10 can consume the lifecycle without project-local duplication.

---

# Execution discipline

Use one coherent implementation branch from current `main`.

Do not create one branch per session concern or one PR per semantic rule.

Use subagents only for bounded read-only runtime inspection or independent review when isolation is materially useful.

The parent owns synthesis and final acceptance.

---

# Stop / escalation

Stop only if:

1. actual Codex session/AGENTS runtime behavior materially contradicts the assumed semantics;
2. reliable implementation requires runtime/platform controls not exposed locally;
3. a requested change would require implementing #8, #9, #11, or #15 rather than merely interfacing with them;
4. a closeout/session capability is externally consumed in a way that would be broken by the minimal semantic change;
5. evidence shows a real distinct state machine is required, in which case report it rather than silently creating one.

Do not stop for ordinary documentation, scoped guidance, closeout alignment, or bounded fixtures inside this PLAN.

---

# Definition of done

The system is sustainable at the session layer when it can start fresh from the right minimal state, refresh itself when the live task meaningfully changes, keep long-history context subordinate to authoritative state, make delegation decisions from fresh context, and reliably notice material friction or redundancy before completion without automatically growing or mutating the control plane.