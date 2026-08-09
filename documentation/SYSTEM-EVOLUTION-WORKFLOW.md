---
id: SYSTEM-EVOLUTION-WORKFLOW
status: proposed
updated: 2026-08-09
scope: workflow-family
inherits: OPERATING-WORKFLOW-CODEX-CONTROL-PLANE
---

# System Configuration and Change Workflow

## Purpose

This document defines the shared workflow family for changing the AI control plane itself: configuration, skills, workflows, agent boundaries, routing, tooling, deployment, validation, and maintenance.

It extends `documentation/OPERATING-WORKFLOW.md`. It does not replace the general lifecycle and does not grant automatic mutation authority.

Controlled self-evolution is a downstream governance concern: this workflow explains **how an accepted system change is handled**, while Issue #11 owns **when repeated evidence is sufficient to propose and promote durable systemic evolution**.

## Entry modes

### Reactive

Use when real work exposes a failure, recurring friction, inconsistency, stale configuration, weak validation, routing error, or unnecessary maintenance burden.

### Proactive

Use when a new capability, integration, tool, or operating improvement is intentionally proposed.

Both modes converge on the same evidence-driven lifecycle.

## Lifecycle

```text
OBSERVE / REQUEST
  ↓
ORIENT TO CURRENT SYSTEM
  ↓
CLASSIFY THE PROBLEM
  ↓
REUSE / RESEARCH EXISTING CAPABILITY
  ↓
PROPOSE THE SMALLEST CHANGE
  ↓
PLAN ↺ CRITIQUE
  ↓
IMPLEMENT / CONFIGURE
  ↓
DETERMINISTIC VALIDATION ↺ BOUNDED REPAIR
  ↓
INDEPENDENT REVIEW WHEN JUSTIFIED
  ↓
ACCEPT / REJECT
  ↓
UPDATE CURRENT / DECISIONS / CAPABILITY SURFACE
  ↓
OBSERVE FUTURE USE
```

## Classification

Classify before changing anything. Typical classes are:

- configuration or instruction problem;
- missing reusable capability;
- skill trigger/procedure problem;
- workflow/state/gate problem;
- agent permission/isolation boundary problem;
- validation/test gap;
- runtime/tool/integration limitation;
- packaging/deployment problem;
- documentation/state drift;
- repeated operational friction that may later become evidence for Issue #11.

Classification is diagnostic, not permission to create a new component.

## Reuse before creation

Before building a new local capability:

1. inspect current built-in/runtime behavior;
2. inspect existing local skills/workflows/scripts;
3. inspect maintained external/official capabilities where useful;
4. compare overlap, provenance, trigger quality, mutation boundary, tests, and maintenance cost;
5. create a new component only when the existing options do not satisfy the required contract.

External skill qualification is tracked under Issue #14. Existing/local rationalization remains evidence-driven under Issue #13.

## Change selection

Prefer the smallest correct change surface:

```text
policy/rule only needed everywhere?      → AGENTS / instructions
stable reusable procedure?               → Skill
stateful lifecycle/gates/resume needed?  → Workflow
objective deterministic operation?       → Script / tool
permission/isolation/autonomy boundary?  → Agent / runtime role
accepted long-lived architecture choice? → DECISIONS
current deployed truth?                  → CURRENT
packaging/distribution concern?          → defer to portability layer
```

Do not introduce a skill, workflow, or agent for architectural symmetry.

## Relationship to controlled self-evolution

This workflow may produce evidence that a recurring pattern deserves broader change, but it does not decide global promotion by itself.

```text
SYSTEM CHANGE OBSERVATION
  ↓
record evidence
  ↓
repeated/material pattern?
  └─ if yes → Issue #11 self-evolution governance
```

Issue #11 owns recurrence/materiality thresholds, proposal-first governance, project-local-first promotion, and acceptance of durable systemic evolution.

A single observation may justify an urgent bounded fix through this workflow, but not a new global abstraction merely because it occurred once.

## Evidence expected

Depending on the change, evidence should include:

- exact current configuration/state;
- reproduced failure or demonstrated unmet need;
- alternatives considered;
- overlap with existing capabilities;
- validation commands/tests/schema checks;
- runtime probe results where behavior is harness-specific;
- migration/rollback path when references or installed surfaces change;
- post-change evidence showing the original problem is improved;
- unresolved limitations.

## Promotion rules

Use explicit promotion destinations:

- accepted architecture decision → `DECISIONS.md`;
- deployed current truth → `CURRENT.md`;
- reusable procedure → Skill after demonstrated reuse;
- deterministic operation → script/tool;
- real lifecycle/state contract → machine-readable workflow only when consumed/enforced;
- project-specific behavior → remain project-local until reuse is demonstrated;
- recurring cross-project behavior → candidate input to Issue #11, not automatic global policy.

## Relationship to projects

Projects inherit the global operating system. A project may expose evidence for system changes but should not mutate the global control plane silently.

```text
PROJECT OBSERVATION
  ↓
BOUNDED PROJECT/SYSTEM CHANGE when needed
  ↓
VALIDATE / REVIEW
  ↓
repeated cross-project pattern?
  └─ if yes → #11 promotion governance
```

## Sustainability rules

Prefer:

- evidence before abstraction;
- reuse before local duplication;
- deterministic validation;
- reversible changes;
- small vertical slices;
- provenance/version tracking for external capabilities;
- capability-first routing;
- bounded changes.

Avoid:

- automatic self-modification;
- broad refactors justified only by aesthetics;
- one workflow per persona;
- one skill per minor action;
- model-dependent behavior encoded as permanent architecture without runtime evidence;
- maintaining duplicate external skills locally without a real governance reason.

## Completion condition

A system change is complete only when the observed/requested problem is addressed with evidence, validation is adequate, consequential review is resolved, durable state is reconciled, and the resulting maintenance burden is justified by demonstrated value.
