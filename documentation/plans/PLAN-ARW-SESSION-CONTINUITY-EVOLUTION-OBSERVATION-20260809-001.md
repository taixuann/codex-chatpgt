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

### Selective invalidation rule

Reorientation must be **selective**, not a global reset.

When a material event occurs:

```text
identify which assumptions/state may now be invalid
→ invalidate only those assumptions
→ reload only affected authoritative sources
→ continue from the refreshed state
```

Examples:

```text
PR merged
→ refresh related Issue/PLAN/branch/current files
→ do not reload unrelated Wiki or memory

new scientific evidence contradicts one mechanism assumption
→ refresh that evidence/claim context
→ do not reconstruct the entire project
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

# Phase 3 — Define history/compaction authority and context health

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

Use the following **conceptual context-health vocabulary only when useful**:

```text
HEALTHY
= current context is sufficient and consistent

NOISY
= too much superseded or irrelevant discussion obscures current work

STALE
= live/canonical state has changed since the relevant reasoning

CONFLICTED
= conversation/summary and authoritative state disagree materially
```

Response semantics:

```text
HEALTHY → continue
NOISY → compact or reorient to minimal state
STALE → selectively reload affected live/canonical state
CONFLICTED → surface conflict, authoritative state wins, then reorient
```

Do not serialize these states, track them in a database, or require token-percentage telemetry.

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

A child context should receive the smallest bounded packet needed for the task rather than an undifferentiated conversation dump.

---

# Phase 5 — Classify failures before choosing the loop

Do not treat every failure as an implementation bug.

Classify a material failure into the smallest useful class:

```text
A. IMPLEMENTATION / EXECUTION FAILURE
   tool, code, test, or bounded operation failed while assumptions remain valid
   → diagnose → bounded repair → revalidate

B. CONTEXT / STATE FAILURE
   missing evidence, stale state, wrong assumption, or authoritative state changed
   → reorient/selectively refresh → return to work

C. ARCHITECTURE / CONTRACT FAILURE
   accepted scope/contract cannot be executed safely or consistently
   → stop and escalate with evidence
```

Do not repair code merely to compensate for stale context. Do not reorient globally when one deterministic implementation check failed. Do not silently redesign architecture to escape an accepted contract.

Repeated repair failure should trigger reclassification rather than unlimited retries.

---

# Phase 6 — Separate acceptance from learning at completion

Before meaningful accepted completion of consequential work, use two distinct checks:

```text
A. ACCEPTANCE CHECK
→ objective met?
→ acceptance criteria satisfied?
→ deterministic validation sufficient?
→ material uncertainty unresolved?
→ independent review justified?

B. LEARNING / EVOLUTION CHECK
→ did execution reveal reusable recurring/material friction or redundancy?
```

Do not redesign architecture as a substitute for finishing or repairing the current task.

The normal learning outcome should often be:

```text
NO ACTION
```

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

### Observation accumulation semantics

Do not equate one observation with an evolution proposal.

Conceptually:

```text
OBSERVE
→ ACCUMULATE EVIDENCE IN EXISTING OWNERS WHEN USEFUL
→ RECURRENCE / MATERIALITY THRESHOLD
→ #11 PROPOSAL GOVERNANCE
```

This is not a numeric `three strikes` rule. A repeated low-impact pattern may need multiple occurrences; one exceptional high-impact failure may be material enough for #11.

#31 does not own the threshold itself. #11 does.

Signal handling:

```text
one-off/local
→ repair locally or leave in existing execution evidence

weak cross-session signal with no suitable durable owner
→ do not invent a new log; if loss becomes a real problem, that is evidence for #9

possible recurring/material pattern
→ preserve minimally in the existing Issue/PR/project owner

mature repeated/material evidence
→ hand to #11

accepted change
→ implement through #15/general change lifecycle
```

### Critical rule

Observation must never directly mutate global policy, AGENTS, skills, workflows, agents, or routing.

---

# Phase 7 — Ensure negative evidence can simplify the system

The evolution check must detect evidence for removal/simplification as well as additions.

Every mature candidate should allow at least these dispositions conceptually:

```text
NO CHANGE
LOCAL FIX
GENERALIZE / PROMOTE
SIMPLIFY / RETIRE
```

Examples:

- a skill has no recurring valid trigger;
- a workflow is never useful despite relevant work;
- governed lifecycle ceremony exceeds risk/consumer value;
- an agent never earns spawn overhead;
- validators duplicate stronger checks;
- guidance repeatedly harms rather than helps routing.

Do not automatically delete. Route material repeated evidence to #11/#15 as appropriate.

Self-evolution must be capable of self-simplification, not only self-growth.

---

# Phase 8 — Admit evaluator/improvement loops only when earned

Do not make `generate → critique → regenerate` a universal lifecycle stage.

A scored/evaluator improvement loop is justified only when all are true enough to matter:

```text
1. the task is difficult/consequential enough to justify iteration;
2. there is a meaningful measurable or reviewable quality criterion;
3. another iteration can plausibly improve the candidate;
4. the expected quality gain exceeds coordination/cost overhead;
5. there is a stop condition such as acceptance threshold, resolved findings, or diminishing returns.
```

Good evidence surfaces include deterministic tests, benchmark scores, explicit rubrics, scientific consistency criteria, or material independent-review findings.

If admitted:

```text
candidate
→ evaluate
→ targeted repair/improvement
→ re-evaluate
→ stop on threshold / resolved findings / diminishing return
```

Do not use vague self-reflection loops that iterate until the output merely feels better.

Model/reasoning/evaluator routing remains #8 where runtime policy is involved.

---

# Phase 9 — Align session-closeout only where useful

Inspect `shared-session-closeout` (or current equivalent).

If it remains a real recurring capability:

- add the bounded evolution check to consequential closeout;
- ensure it can return `NO ACTION`;
- preserve acceptance-before-learning ordering;
- keep ordinary chat endings out of scope;
- prefer Issue/PLAN/PR/CI reconciliation over legacy goal/change wrappers for ordinary repository work;
- do not make closeout the only place the global evolution observation rule exists.

If closeout is not reliably auto-discovered/invoked, the global operating semantics must still guarantee the check at meaningful completion.

Do not create another session skill.

---

# Phase 10 — Add only honest validation

Prefer semantic/fixture validation only where behavior can be tested honestly.

Potential tests:

1. fresh-session orientation examples:
   - trivial task → minimal/no bootstrap;
   - non-trivial repo task → scoped instructions + relevant state;
   - insufficient context → handoff to #2 context acquisition.
2. selective invalidation/checkpoint examples:
   - external PR merge changes related state → refresh affected sources only;
   - unchanged state → continue without ceremony;
   - unrelated external change → do not globally reload.
3. context health/authority conflict:
   - stale conversational assumption conflicts with live GitHub → `CONFLICTED`, live state wins;
   - noisy but not stale history → compact/reorient without pretending summary is canonical.
4. failure classification:
   - deterministic code failure with valid assumptions → bounded repair;
   - missing/moved authoritative file → context/state refresh;
   - accepted contract contradiction → escalate.
5. evolution check:
   - no recurring/material friction → `NO ACTION`;
   - repeated routing ambiguity → candidate to #11, not direct mutation;
   - redundant ceremony → simplification candidate.
6. evaluator-loop admission:
   - ordinary low-risk task → no evaluator loop;
   - difficult task with measurable criterion → bounded evaluate/improve loop allowed.

Do not claim static fixtures prove behavioral runtime behavior.

If a deterministic validator adds no real guarantee, do not create it.

---

# Phase 11 — Independent review for overengineering and missing guarantees

Review must explicitly look for both failure modes:

## Too little

- orientation remains optional prose that may not execute;
- long sessions have no material refresh trigger;
- state invalidation is global/ambiguous rather than selective;
- failure classes are not distinguished and repairs can mask stale context;
- evolution check exists only inside a skill that may never load;
- observations have no handoff/accumulation path to #11;
- state authority remains ambiguous;
- learning/evolution begins before current-task acceptance is settled.

## Too much

- session manager/database introduced;
- mandatory summary/checkpoint artifacts;
- fixed turn counters without evidence;
- context-health states serialized into a new state machine/database;
- auto-created Issues from friction;
- autonomous mutation/evolution agent;
- universal evaluator/self-reflection loop;
- duplicated routing policy from #8;
- memory implementation from #9;
- new workflow engine.

Repair only material findings.

---

# Required durable updates

Expected minimal accepted-state changes:

- `documentation/OPERATING-WORKFLOW.md` for session/reorientation/failure/evolution semantics;
- root/scoped `AGENTS.md` only if one concise normative invariant is required;
- `shared-session-closeout` only if its actual trigger/use justifies alignment;
- `CURRENT.md` and `DECISIONS.md` only for accepted deployed semantics;
- #2/#8/#10/#11/#15 comments for ownership/cross-linking.

Do not create:

- session registry;
- session schema;
- checkpoint schema;
- context-health registry;
- evolution log;
- observation database;
- session workflow;
- evolution workflow;
- evaluator workflow by default;
- new agent;
- new skill unless unexpected real runtime evidence proves a distinct recurring contract.

---

# Acceptance mapping

Issue #31 is complete only when:

- AC-01: fresh non-trivial sessions have a minimal orientation contract;
- AC-02: context sufficiency can hand to #2 without duplicating #2;
- AC-03: long work has event-driven reorientation triggers;
- AC-04: reorientation selectively invalidates/reloads affected state rather than resetting globally;
- AC-05: live/canonical state overrides stale conversation assumptions and context can be recognized conceptually as healthy/noisy/stale/conflicted without a new store;
- AC-06: compaction/history remains continuity context, not authority;
- AC-07: delegation occurs only after sufficiently fresh orientation and #8 ownership is preserved;
- AC-08: failures distinguish implementation repair, context/state refresh, and architecture/contract escalation;
- AC-09: completion separates acceptance from learning/evolution;
- AC-10: consequential completion runs a bounded evolution check that may return `NO ACTION`;
- AC-11: observations accumulate only through existing evidence surfaces and mature candidates hand off to #11 rather than auto-promoting;
- AC-12: simplification/removal evidence is first-class;
- AC-13: evaluator/improvement loops are conditional on measurable value and have explicit stop conditions;
- AC-14: no mandatory checkpoint/evolution/context-health artifact family is added;
- AC-15: no session/memory/evolution/evaluator platform is built;
- AC-16: #10 can consume the lifecycle without project-local duplication.

---

# Execution discipline

Use one coherent implementation branch from current `main`.

Do not create one branch per session concern or one PR per semantic rule.

Use subagents only for bounded read-only runtime inspection or independent review when isolation is materially useful.

The parent owns synthesis and final acceptance.

Think of the runtime as one lifecycle with four event hooks, not a collection of independent perpetual loops:

```text
START HOOK
→ ORIENT

STATE-CHANGE HOOK
→ SELECTIVE REORIENT if needed

FAILURE HOOK
→ CLASSIFY → REPAIR / REORIENT / ESCALATE

COMPLETION HOOK
→ ACCEPTANCE → OPTIONAL REVIEW → EVOLUTION OBSERVATION
```

---

# Stop / escalation

Stop only if:

1. actual Codex session/AGENTS runtime behavior materially contradicts the assumed semantics;
2. reliable implementation requires runtime/platform controls not exposed locally;
3. a requested change would require implementing #8, #9, #11, or #15 rather than merely interfacing with them;
4. a closeout/session capability is externally consumed in a way that would be broken by the minimal semantic change;
5. evidence shows a real distinct persistent state machine is required, in which case report it rather than silently creating one.

Do not stop for ordinary documentation, scoped guidance, closeout alignment, or bounded fixtures inside this PLAN.

---

# Definition of done

The system is sustainable at the session layer when it can start fresh from the right minimal state, selectively refresh itself when the live task meaningfully changes, keep long-history context subordinate to authoritative state, distinguish implementation failures from stale-context and architecture failures, make delegation decisions from fresh context, finish the current task before attempting broader learning, and reliably notice/accumulate material friction or redundancy without automatically growing or mutating the control plane.