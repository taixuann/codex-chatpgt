---
id: OPERATING-WORKFLOW-CODEX-CONTROL-PLANE
status: active
updated: 2026-08-09
scope: general
---

# General Operating Workflow

## Purpose

This document is the canonical human-readable description of the general operating workflow used by the control plane.

It defines the default lifecycle for non-trivial work across cloud reasoning, GitHub coordination, local execution, validation, review, and durable state updates.

This is a semantic workflow specification, not a requirement to create a separate file, subagent, skill, or ceremony for every stage.

Project-specific workflows may extend this lifecycle when a real project requires different domain steps, state transitions, or validation gates. They should not duplicate the global workflow when the shared lifecycle is sufficient.

## Core lifecycle

```text
INTAKE
  ↓
RECALL / ORIENT
  ↓
CONTEXT SUFFICIENT?
  ├─ yes → continue
  └─ no  → acquire only material context
  ↓
REASON ↺ REFINE
  ↓
DECIDE / PLAN ↺ CRITIQUE
  ↓
PROMOTE TO WORK UNIT when execution-worthy
  ↓
CAPABILITY ROUTING
  ↓
DELEGATE / EXECUTE
  ↓
VALIDATE ↺ BOUNDED REPAIR
  ↓
INDEPENDENT REVIEW when justified
  ↓
SYNTHESIZE ↺ FINAL REFINE
  ↓
ACCEPT / MERGE
  ↓
BOUNDED EVOLUTION CHECK when completion is meaningful
  ↓
COMMIT DURABLE STATE / KNOWLEDGE
```

The loops are conditional. Stop refining or repairing when no material flaw remains, acceptance criteria are met, further work has negligible expected value, or progress requires unavailable evidence or human judgment.

## Stage semantics

### 1. Intake

Establish the actual objective, scope, constraints, expected outcome, and whether the request is simple or consequential.

Do not create durable execution artifacts for raw ideas that are still being explored.

### 2. Recall / Orient

Determine the smallest authoritative context required for the task.

Prefer progressive disclosure:

```text
CLOUD-BRIEF
  ↓
CURRENT / DECISIONS
  ↓
active Issue / PLAN
  ↓
HANDOFF / PR
  ↓
specific files, diffs, runtime evidence
```

Relevant sources may include canonical state, repository evidence, selected memory, Wiki, RAG/source material, or external research. Do not dump all available history into the active context.

### 3. Context sufficiency decision

Ask whether the current context is sufficient to plan or answer reliably.

If sufficient, continue directly.

If insufficient, acquire only the missing material context. A small lookup may remain in the parent context. Use a bounded explorer such as Argus only when isolation, scale, or parallelism justifies delegation.

For a repeatable local repository packet, use the explicit-allowlist helper
`ops/scripts/acquire_context_packet.py`. It reads UTF-8 regular files, records
deterministic hashes, and emits evidence only; it does not decide sufficiency,
route agents, interpret project content, or write checkpoints.

A capability need does not automatically imply a subagent.

### 3a. Fresh logical-session orientation

For fresh non-trivial work, orient from the smallest authoritative state before
capability routing:

```text
identify repository/project and scope
→ apply scoped AGENTS instructions
→ read relevant CURRENT / DECISIONS
→ resolve the active Issue / PLAN / PR / project task
→ inspect live state only when correctness depends on it
→ test context sufficiency
→ acquire missing context through #2 only when material
→ route capability, delegation, and execution
```

Trivial tasks may collapse these steps. Do not bulk-load all history, create a
`session-bootstrap` skill, or duplicate the instruction chain. Current/live
state takes precedence over stale conversational assumptions.

### 3b. Event-driven reorientation

Long-running logical work reorients only after a material event, such as an
objective/scope change, phase transition, external Issue/PR/branch change,
consequential mutation after extended discussion, material validation failure,
contradictory evidence, authority uncertainty, or noisy superseded context.

At a checkpoint reconstruct only the objective, accepted/live state, material
changes, open constraints, authoritative artifacts, and whether #2 context
acquisition is needed. Selectively invalidate affected assumptions and reload
only their sources. A checkpoint is normally an internal action, not a file,
commit, Issue, fixed turn counter, or global reset.

For continuation, use this authority order:

```text
runtime instructions → scoped AGENTS → accepted CURRENT / DECISIONS
→ live Issue / PLAN / PR / Git / project state
→ recent unresolved conversation → older history/compaction
```

Conceptual context health may be `HEALTHY`, `NOISY`, `STALE`, or `CONFLICTED`.
These are reasoning labels, not serialized runtime state. On conflict, surface
it, prefer authoritative state, and reorient selectively.

### 4. Reason ↺ Refine

Construct the strongest current interpretation or solution, then inspect it for material flaws such as:

- incorrect assumptions;
- missing constraints;
- contradictions;
- unsupported conclusions;
- scope drift;
- unnecessary complexity;
- missing failure modes;
- weak validation.

Refine only when the critique would materially change the result.

### 5. Decide / Plan ↺ Critique

Separate durable decisions from implementation design.

- Accepted long-lived architecture decisions belong in `DECISIONS.md`.
- Current accepted truth belongs in `CURRENT.md`.
- An Issue defines what must become true.
- A PLAN defines how the current Issue should be implemented using current evidence.

Critique consequential plans for scope completeness, dependency order, unnecessary components, hidden coupling, validation gaps, rollback/recovery, and stronger simpler alternatives.

### 6. Promote to work unit

Promote work from discussion into GitHub only when execution intent is stable enough to track.

The default artifact chain is:

```text
Chat / reasoning
  ↓
Decision when needed
  ↓
GitHub Issue
  ↓
PLAN near execution time
```

Do not create Issues for unresolved brainstorming. Do not create detailed future PLANs long before their dependencies provide real evidence.

### 7. Capability routing

Route in this order:

```text
TASK
  ↓
required capability
  ↓
is delegation useful?
  ↓
role / agent
  ↓
model + reasoning effort
```

Definitions:

- **Capability**: what behavior is needed.
- **Skill**: a stable reusable procedure implementing a capability when such a procedure earns reusable packaging.
- **Agent / role**: execution topology, permission boundary, context isolation, autonomy, or independent judgment.
- **Model / reasoning effort**: runtime resources selected after task risk, ambiguity, validation strength, and cost are known.

Do not choose an agent first and then force the task into that agent's available skills.

There are two distinct entry modes:

- An explicit named-agent request such as `@franky` selects that semantic agent
  first, then runs its own admission, permission, and authority checks. The
  request cannot force an out-of-scope task through the selected agent.
- Without a named agent, retain capability-first routing and decide whether
  delegation is useful only after the required capability is understood.

For consequential Franky control-plane work, the parent may materialize the
bounded `franky.task.v1` contract. Franky composes the minimum local capability
path and returns `franky.result.v1` acceptance-ready evidence. The result may
carry a thin ordered evidence envelope from request through closure, but it is
not an executable workflow engine. This is an invocation boundary, not a
universal router; the parent/reviewer retains final acceptance and durable-state
promotion.

### 8. Skill invocation

Use skills only when their declared purpose matches the task.

Supported invocation modes are conceptually:

1. **Automatic discovery** — the runtime/model selects a skill from a discriminative description.
2. **Required capability** — governed work explicitly requires a capability and resolves it to an approved skill/procedure.
3. **Explicit invocation** — the user/operator selects a particular skill for testing or deterministic routing where the harness supports it.

Skills are capability-centric and may be used by the parent or by different bounded workers. Do not treat skills as permanently owned by one persona unless a real permission/tool boundary requires it.

### 8a. Component linking contract

Make the composition path explicit without introducing a universal registry or
interface schema:

```text
TASK / ISSUE
  ↓ objective + scope + constraints
REQUIRED CAPABILITY
  ↓ candidate skill/procedure
DELEGATION DECISION
  ↓ parent or bounded agent
DETERMINISTIC TOOL when needed
  ↓ result
VALIDATION / INDEPENDENT REVIEW when justified
  ↓ acceptance
DURABLE DESTINATION
```

The reusable contracts are semantic review vocabulary:

- **Skill:** trigger → inputs/context → procedure → output → side effects → stop conditions → validation.
- **Agent:** use condition → authority → task contract → allowed scope → return contract → escalation.
- **Workflow:** entry → state/transitions → gates → failure/recovery → exit → consumer.
- **Tool/script:** input → deterministic operation → output → error conditions.

Use the smallest contract that makes a handoff, validation, or recovery
observable. Do not serialize these fields merely for symmetry.

### 9. Delegate / Execute

The parent/main agent retains overall reasoning, architecture, planning, decomposition, conflict resolution, synthesis, and final decision authority.

Delegate only when work benefits from:

- meaningful parallelism;
- context isolation;
- independent judgment;
- specialized external capability.

Subagents may plan locally inside a bounded task contract but must not silently widen scope, replace the parent plan, create global policy, or recursively delegate by default.

### 10. Validate ↺ Bounded repair

Prefer deterministic validation wherever possible:

- tests;
- schema validation;
- lint/type checks;
- file/output existence;
- numerical tolerances;
- reproducibility checks;
- acceptance-criteria-to-evidence mapping.

Use:

```text
execute
  ↓
validate
  ↓ fail
diagnose
  ↓
bounded repair
  ↓
validate again
```

Escalate rather than retry indefinitely when failures repeat, evidence conflicts, architecture/scope must change, or repair would become speculative.

### 10a. Failure classification

Classify a material failure before choosing the next loop:

```text
implementation/execution failure
→ diagnose → bounded repair → revalidate

context/state failure
→ selectively reorient or acquire missing context

architecture/contract failure
→ stop and escalate with evidence
```

Do not repair code to compensate for stale context, globally reorient for a
local deterministic failure, or retry indefinitely. Repeated repair failure is
evidence to reclassify.

### 11. Independent review when justified

Validation asks whether the result works as specified.

Review asks whether the result should be accepted.

Use independent review when deterministic validation is incomplete, architecture or scientific interpretation matters, consequences are high, uncertainty remains, repeated failures occur, or independence materially improves confidence.

Do not invoke independent review mechanically for every low-risk task.

### 12. Pull Request as evidence contract

For repository implementation, the PR presents what actually changed and the evidence supporting acceptance.

A good PR should trace:

```text
Issue intent
  ↓
PLAN design
  ↓
actual changes
  ↓
validation evidence
  ↓
acceptance criteria status
  ↓
deviations / limitations
  ↓
review outcome
```

A passing command or successful worker run is not, by itself, acceptance.

### 12a. Default Git branch lifecycle

For ordinary implementation work, use one temporary work-unit branch from
fresh canonical `main`:

```text
main
  → one Issue/work-unit branch
  → one PR targeting main
  → validation / review where required
  → merge
  → delete the implementation branch
```

Before opening a branch, check whether an existing active branch already owns
the work. Normally only one active implementation branch exists for the
current work unit. Do not branch from another feature or integration branch by
default, and do not create branch-per-agent or branch-per-reviewer variants.
All roles may inspect, review, test, and repair on the same active branch.

Use a stacked branch only when an explicit dependency requires it and the
Issue or PLAN records that dependency. A branch is temporary execution state,
not durable architecture; documentation follow-up, validation, reviewer fixes,
and role handoffs do not independently justify another branch. Retire the
implementation branch after merge and never leave an obsolete integration
branch as the base for future work.

### 13. Synthesize ↺ Final refine

Before completion, compare the result against the original objective and check:

- requirements and acceptance criteria;
- validation sufficiency;
- unresolved failures;
- contradictions;
- unsupported claims;
- scope drift;
- unnecessary maintenance burden.

The parent performs final synthesis and resolves conflicting worker/reviewer outputs.

### 14. Accept / Merge

Merge or explicitly accept only when material acceptance conditions are satisfied or consciously waived with rationale.

Completion of execution does not automatically mean acceptance of architecture or scientific interpretation.

### 15. Commit durable state / knowledge

Keep durable planes distinct:

- `AGENTS.md` = operating rules and boundaries;
- `CURRENT.md` = accepted current truth;
- `DECISIONS.md` = accepted long-lived decisions;
- Issue = intended future state / execution contract;
- PLAN = current implementation design;
- PR = implementation and validation evidence;
- memory = historical observations, failures, patterns, experience;
- Wiki = consolidated reviewed knowledge;
- RAG/source corpus = source evidence;
- Skill = promoted reusable procedure after demonstrated need and review.

Use explicit promotion:

```text
OBSERVE → PROPOSE → REVIEW → ACCEPT → UPDATE
```

Do not turn a single observation into global policy or silently mutate global instructions, skills, workflows, or routing.

## Completion and logical-session continuity

For consequential work, acceptance precedes learning:

```text
finish implementation
→ change-impact closure
→ deterministic validation
→ independent review when justified
→ acceptance
→ bounded evolution observation
```

The evolution check asks whether execution exposed recurring/material context
failure, routing ambiguity, guidance confusion, unnecessary ceremony, missing
validation, repeated workaround, boundary failure, missing capability, or
redundant component. The normal result is `NO ACTION`. Observations accumulate
in existing Issue/PR/project owners; mature evidence hands to #11, and accepted
system changes follow #15/general change lifecycle. Observation never directly
mutates global policy or creates an Issue, skill, workflow, or agent.

Negative evidence is valid: a skill, workflow, agent, validator, or rule may be
a simplification/retirement candidate. Evaluator loops are admitted only for a
material task with a measurable criterion, plausible gain, justified cost, and
explicit stop condition.

A logical session is `objective + scope + accepted/live task state`, not a chat
container. After acceptance, continue when the objective and context remain
healthy; reorient when state is stale/noisy; recommend a fresh logical session
when the objective materially changes, reconstruction is safer, or independent
review needs fresh judgment. Do not auto-close the chat or force a fixed turn
limit.

## Artifact responsibilities

| Artifact | Responsibility |
| --- | --- |
| `AGENTS.md` | concise runtime policy and boundaries |
| `OPERATING-WORKFLOW.md` | canonical human-readable general lifecycle semantics |
| `CURRENT.md` | what is accepted as true now |
| `DECISIONS.md` | accepted long-lived architecture choices and rationale |
| GitHub Issue | what must become true, with scope and acceptance |
| PLAN | how the current work will be implemented |
| PR | what changed and evidence that it meets acceptance |
| HANDOFF | bounded cloud/local execution provenance when needed |
| Skill | stable reusable procedure |
| Machine-readable workflow | only when actual state/gate/runtime enforcement justifies one |

## General versus project-specific workflow

The general workflow governs the control pattern across projects.

A project should inherit it and add only real differences, for example:

```text
GENERAL
ORIENT → PLAN → EXECUTE → VALIDATE → REVIEW

PROJECT-SPECIFIC EXTENSION
DOMAIN STEP A → DOMAIN STEP B → PROJECT VALIDATION
```

Create a project-specific workflow or lifecycle adapter only when a real project demonstrates materially different states, gates, or ordering. Domain knowledge alone is not enough reason to create a new agent or workflow.

## Machine-readable workflow rule

A YAML or other machine-readable workflow is justified only when it provides runtime value such as:

- enforced state transitions;
- approval gates;
- resume/recovery state;
- deterministic routing or validation;
- machine consumption by tooling.

If a machine-readable workflow merely restates the prose procedure in `SKILL.md` or this document and nothing consumes or enforces it, prefer the simpler source and avoid duplication.

## Sustainability rules

Prefer:

- capability-first routing;
- few sharp skills;
- one thin shared lifecycle;
- project-local specialization;
- deterministic scripts for deterministic work;
- explicit validation and review boundaries;
- evidence-driven promotion;
- progressive disclosure;
- GitHub as the durable cloud/local coordination bus.

Avoid:

- one workflow per persona;
- one agent per domain;
- new skills for architectural symmetry;
- giant always-loaded workflows;
- duplicated state or duplicated procedure text;
- memory as canonical truth or scientific evidence;
- automatic global mutation;
- premature plugin/harness packaging;
- speculative components that have not earned their maintenance cost.

## Build philosophy

For new architecture, use:

```text
PROVE BEHAVIOR
  → OBSERVE
  → EXTRACT STABLE CONTRACT
  → REUSE
  → PACKAGE
```

The goal is not the largest agent system. The goal is the smallest durable operating system that reliably acquires context, executes bounded work, validates results, invokes independent judgment when useful, and records accepted state without creating unnecessary machinery.
