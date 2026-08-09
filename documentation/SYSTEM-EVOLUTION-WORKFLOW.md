---
id: SYSTEM-EVOLUTION-WORKFLOW
status: proposed
updated: 2026-08-09
scope: workflow-family
inherits: OPERATING-WORKFLOW-CODEX-CONTROL-PLANE
---

# System Configuration and Self-Evolution Workflow

## Purpose

This document defines the shared workflow family for improving the AI control plane itself: configuration, skills, workflows, agent boundaries, routing, tooling, deployment, validation, and controlled self-evolution.

It extends `documentation/OPERATING-WORKFLOW.md`. It does not replace the general lifecycle and does not grant automatic mutation authority.

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
- repeated operational friction that may justify self-evolution.

Classification is diagnostic, not permission to create a new component.

## Reuse before creation

Before building a new local capability:

1. inspect current built-in/runtime behavior;
2. inspect existing local skills/workflows/scripts;
3. inspect maintained external/official capabilities where useful;
4. compare overlap, provenance, trigger quality, mutation boundary, tests, and maintenance cost;
5. create a new component only when the existing options do not satisfy the required contract.

External skill qualification is tracked separately under the external-skill collection work. Existing/local rationalization remains evidence-driven.

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

## Self-evolution gate

System self-evolution is distinct from one-run answer refinement.

A durable behavioral change should normally follow:

```text
OBSERVE
  ↓
RECURRENCE / MATERIALITY CHECK
  ↓
PROPOSE
  ↓
REVIEW
  ↓
ACCEPT
  ↓
UPDATE
  ↓
VALIDATE IN REAL USE
```

A single observation may justify an urgent bug fix, but it does not automatically justify a new global abstraction or policy.

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
- recurring cross-project behavior → global policy candidate after review;
- project-specific behavior → remain project-local until reuse is demonstrated.

## Relationship to projects

Projects inherit the global operating system. A project may expose evidence for system evolution but should not mutate the global control plane silently.

```text
PROJECT OBSERVATION
  ↓
SYSTEM-EVOLUTION PROPOSAL
  ↓
REVIEW / VALIDATION
  ↓
PROJECT-LOCAL CHANGE first when appropriate
  ↓
GLOBAL PROMOTION only after demonstrated reuse
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
- bounded self-improvement.

Avoid:

- automatic self-modification;
- broad refactors justified only by aesthetics;
- one workflow per persona;
- one skill per minor action;
- model-dependent behavior encoded as permanent architecture without runtime evidence;
- maintaining duplicate external skills locally without a real governance reason.

## Completion condition

A system-evolution change is complete only when the observed/requested problem is addressed with evidence, validation is adequate, consequential review is resolved, durable state is reconciled, and the resulting maintenance burden is justified by demonstrated value.
