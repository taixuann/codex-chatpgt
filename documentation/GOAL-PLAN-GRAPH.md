---
id: GOAL-PLAN-GRAPH-CODEX-CONTROL-PLANE
status: proposed
updated: 2026-08-09
scope: shared-planning-semantics
---

# Goal–Plan Graph Model

## Purpose

This document defines the shared semantic model for connecting durable goals, living plans, bounded tasks, execution evidence, and accepted knowledge across the control plane.

The goal is to prevent planning artifacts from becoming isolated documents that lose their relationship to prior intent, dependencies, later revisions, or downstream outcomes.

This is a lightweight semantic model. It does not require a custom graph database, new orchestration engine, or one file per thought.

## Core principle

> Goals are persistent intent nodes. Plans are living execution paths attached to goals. Tasks form temporary dependency graphs inside plans. Results and knowledge update the goal graph after execution.

The general relationship is:

```text
GOAL GRAPH
   ↓
PLAN
   ↓
TASK / CAPABILITY DAG
   ↓
SKILL / AGENT / TOOL
   ↓
EXECUTION
   ↓
VALIDATE / REVIEW
   ↓
RESULT / KNOWLEDGE
   ↓
UPDATE GOAL GRAPH
```

## Semantic responsibilities

| Concept | Responsibility |
| --- | --- |
| Goal | persistent intent: what outcome should eventually become true |
| Plan | current execution design/path for one goal |
| Task | bounded executable unit inside a plan |
| Capability | behavior required by a task |
| Skill | reusable procedure implementing a capability when justified |
| Agent / role | bounded executor, reviewer, permission or context-isolation boundary |
| Result | execution evidence or produced artifact |
| Decision | accepted durable choice affecting future behavior/design |
| Knowledge | reviewed understanding promoted from evidence |

## Goal graph

Goals may relate to one another without being collapsed into one large plan.

Use the smallest useful relationship set:

- `parent`
- `depends_on`
- `related_to`
- `supersedes`
- `realized_by`
- `produces`
- `derived_from`

Do not add relationship types merely for ontology completeness.

Conceptual example:

```text
GOAL-CP-001 Reliable control plane
│
├── GOAL-CP-002 Context acquisition
│      └── realized_by PLAN-CP-002-A
│
├── GOAL-CP-003 Execution + validation
│      └── depends_on GOAL-CP-002
│
└── GOAL-CP-004 Research workflow
       ├── related_to GOAL-CP-003
       └── realized_by PLAN-CP-004-A
```

## GitHub mapping for v1

For the first implementation, prefer existing GitHub primitives over a new goal database:

```text
GitHub Issue
≈ durable goal / tracked work node

Sub-issue
≈ child/sub-goal when independent durable tracking is justified

Issue dependency
≈ blocked-by / depends-on relationship where GitHub supports it

PLAN file
≈ living implementation design attached to the goal

PR
≈ implementation/evidence path showing what changed
```

Do not create an Issue for every implementation task. Small tasks remain inside the PLAN.

## When a task becomes a goal/sub-goal

Promote a task into a durable goal/sub-goal only when at least one of these is true:

- it has an independent outcome worth tracking;
- it spans multiple sessions;
- it has separate blockers/dependencies;
- it requires independent review/acceptance;
- it may proceed separately from the parent plan;
- it produces a reusable capability or durable state change.

Otherwise keep it inside the PLAN task DAG/checklist.

## Plan relationships

Plans are mutable execution paths and may evolve while the goal remains stable.

Use metadata such as:

```yaml
id: PLAN-CP-002-B
goal: GOAL-CP-002
status: active

depends_on:
  - PLAN-CP-001-A

supersedes:
  - PLAN-CP-002-A

inputs:
  - DEC-007
  - ISSUE-14

outputs:
  - PR-21
```

A plan may be superseded without superseding the underlying goal.

Use `supersedes` on the goal only when the durable intent itself materially changes.

## Plan as living design contract

A PLAN should remain current while implementation proceeds.

When material discoveries change implementation design:

- update the active PLAN or create a clearly superseding revision when preserving the old path is useful;
- record why the prior path changed;
- keep the originating goal stable unless the objective itself changes;
- keep acceptance criteria traceable to the goal/Issue.

Do not create multiple unrelated PLAN files for the same goal without explicit relationships.

## Task DAG inside a plan

Plans may contain an explicit dependency graph where ordering matters.

Example:

```text
Task A
  ↓
Task B ──┐
         ├──> Task D
Task C ──┘
```

Tasks should be small enough to execute and verify in a focused session when practical.

Prefer vertical slices that leave the system in a working/verifiable state over large horizontal batches.

Each material task should state:

- purpose;
- acceptance criteria;
- verification;
- dependencies;
- expected changed components when useful;
- stop/escalation conditions.

## Capability routing from the task graph

Task decomposition precedes skill/agent/model selection:

```text
GOAL
 ↓
PLAN
 ↓
TASK DAG
 ↓
required capability
 ↓
is delegation useful?
 ↓
role / agent
 ↓
model + reasoning effort
```

Do not derive plans from the currently installed skill catalog.

Skills are selected because a task requires their capability, not because the skill exists.

## Idea-to-goal promotion

Raw ideas remain in discussion until sufficiently stable.

Recommended flow:

```text
IDEA
 ↓
REFINE / STRESS-TEST
 ↓
stable enough?
 ├─ no → remain discussion
 └─ yes
      ↓
durable intent?
 ├─ no → decision/note only
 └─ yes → GOAL / GitHub Issue
```

Useful idea-refinement semantics include:

- problem statement;
- success condition;
- key assumptions;
- alternatives;
- recommended direction;
- MVP/minimum proof;
- explicit `Not Doing` scope;
- open questions.

Do not create a durable goal simply because an idea was discussed.

## Research integration

The Research and Knowledge workflow may create new goals from knowledge gaps, hypotheses, or unresolved research decisions.

Conceptual flow:

```text
RESEARCH OBJECTIVE
  ↓
GOAL
  ↓
UNDERSTANDING / CLAIMS
  ↓
GAP
  ↓
SUB-GOAL
  ↓
HYPOTHESIS
  ↓
PLAN
  ↓
EXPERIMENT / ANALYSIS
  ↓
RESULT
  ↓
CLAIM UPDATE
  ↓
NEXT GOAL
```

This connects the execution graph to knowledge without making the Wiki or RAG system the planning source of truth.

## System-evolution integration

Repeated operational friction or validated improvement opportunities may create system goals.

```text
OBSERVATION
 ↓
repeated/material?
 ├─ no → keep as evidence
 └─ yes
      ↓
GOAL-SYS-...
      ↓
PLAN
      ↓
CHANGE
      ↓
VALIDATE / REVIEW
      ↓
DECISION / CURRENT update
```

A single observation does not justify global mutation.

## Project inheritance

Projects should not own isolated planning systems.

A project inherits:

- the general operating workflow;
- shared goal/plan semantics;
- shared capability routing rules;
- shared artifact meanings.

A project adds only:

- project objective/domain;
- active project goals;
- local context and source scope;
- project-specific validation;
- domain comparison dimensions where relevant;
- required outputs;
- lifecycle extension only when materially necessary.

Example project overlay:

```yaml
project:
  id: PROJECT-DEVICE-001
  objective: ...
  active_goals:
    - GOAL-R-012
  domain: materials-device-physics
  validation: ...
  capabilities: ...
  knowledge_sources: ...
  outputs: ...
```

Do not copy global workflows, skills, or agent definitions into every project.

## Goal lifecycle

Use a small lifecycle:

```text
PROPOSED
  ↓
ACTIVE
  ↓
IN_PROGRESS / BLOCKED
  ↓
REVIEW
  ↓
DONE
```

Additional terminal states:

- `DROPPED`
- `SUPERSEDED`

Do not create detailed workflow machinery unless tooling actually needs to enforce these states.

## IDs

Prefer stable semantic identifiers with short domain prefixes, for example:

```text
GOAL-CP-014
PLAN-CP-014-A
PLAN-CP-014-B
DEC-008
CLM-TR-021
HYP-TR-004
```

Timestamps belong in metadata/Git history unless a specific artifact class requires date-based IDs.

## Academic-output relationship

Academic writing consumes reviewed research state; it does not become a second knowledge authority.

```text
PAPER GOAL
 ↓
select reviewed claim set
 ↓
evidence / figures
 ↓
argument structure
 ↓
Typst manuscript
```

A manuscript may reference the goals/claims/results it realizes or presents.

## Sustainability rules

Prefer:

- GitHub relationships + Markdown/front matter first;
- explicit goal/plan relationships;
- one active plan per execution path;
- task DAGs only where dependencies matter;
- durable goals only for meaningful tracked outcomes;
- reuse of existing GitHub/project primitives;
- rendering/graph visualization derived from canonical metadata.

Avoid:

- a custom graph database before demonstrated need;
- a new planning engine before current primitives fail;
- one Issue per tiny task;
- disconnected `PLAN-*.md` files with no parent goal;
- duplicated goal state in several registries;
- automatic promotion of observations into goals;
- plans generated from available skill names instead of actual requirements.

## Initial implementation strategy

Prove this model using existing work before creating more infrastructure.

Use several existing control-plane goals/Issues and one research/project path to test:

1. stable goal identifiers/relationships;
2. active PLAN linkage;
3. dependency/supersession semantics;
4. task DAG where useful;
5. result/PR traceability;
6. project inheritance;
7. knowledge-to-goal feedback for research/system evolution.

Only after those tests should the system decide whether dedicated goal files, automated graph extraction, Obsidian rendering, or additional tooling are justified.
