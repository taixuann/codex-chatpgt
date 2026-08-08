---
id: PLAN-ARW-CONTEXT-STRENGTHENING-20260808-001
title: Context Strengthening v1 Vertical Slice
status: proposed
date: 2026-08-08
issue: 2
scope: global-capability-vertical-slice
---

# Objective

Prove the current global agent/skill/task-contract architecture through one thin end-to-end path before expanding memory, research integrations, or broader orchestration.

Target path:

`main orchestration -> task contract -> Argus -> repository-exploration -> context-strengthening -> compact context packet -> parent planning`

# Confirmed decisions

- Keep the current top-level architecture simple.
- Do not add new agents for this slice.
- Argus is the bounded read-only explorer adapter.
- Skills remain capability-centric and reusable across roles.
- Main retains architecture, planning, and final synthesis authority.
- Workflows express lifecycle/conditions rather than persona-specific scripts.
- Do not integrate AgentMemory, Wiki/RAG, or OpenScience in v1.

# Scope

## In scope

1. Add `repository-exploration` skill.
2. Add `context-strengthening` skill.
3. Create a representative task-contract instance for a bounded Argus exploration task.
4. Connect conditional delegation semantics to the existing main operating kernel without creating a persona-specific workflow.
5. Define and validate a compact context packet.
6. Add deterministic validation where practical.
7. Record actual local runtime behavior and deviations.

## Out of scope

- AgentMemory integration.
- Wiki/RAG implementation.
- OpenScience integration.
- New agents or recursive delegation.
- Full model-routing redesign.
- Broad Franky cleanup or renaming.
- Large folder restructuring.
- Generalization into a larger orchestration framework.

# Capability contracts

## repository-exploration

Purpose: retrieve exact internal repository evidence needed by a bounded task.

Must define:

- trigger conditions;
- allowed scope;
- applicable-instruction discovery;
- file/dependency search procedure;
- evidence formatting;
- stop conditions;
- read-only boundary;
- return contract.

## context-strengthening

Purpose: improve planning/review context by selecting and combining only material internal context.

For v1, use only sources that actually exist in this control-plane implementation:

- canonical state;
- repository evidence.

Return shape:

```yaml
canonical: []
repository_evidence: []
conflicts: []
uncertainties: []
```

Do not add speculative memory/wiki/RAG integration fields merely for future architecture symmetry.

# Delegation rules

Delegate to the explorer role only when:

- material internal context is missing;
- the exploration task is independently executable;
- isolated context reduces parent-context noise or cost;
- delegation is expected to add more value than its overhead.

Otherwise the parent should inspect the required context directly.

Argus may choose local search/inspection order inside the bounded task but must not:

- modify files;
- widen scope;
- redesign the parent plan;
- create new global rules;
- recursively delegate.

# Representative task contract

The implementation should include one small representative contract following the existing schema and containing:

- objective;
- include/exclude scope;
- relevant canonical context;
- explorer role hint where useful;
- required capability: repository exploration;
- expected evidence output;
- validation;
- stop conditions.

Do not embed the full parent conversation.

# Validation

Validate at minimum:

1. new skill structure/interfaces;
2. representative task contract against the existing schema;
3. read-only Argus boundary;
4. context-packet shape;
5. existing repository validation/tests remain passing;
6. actual runtime execution where the installed Codex surface allows it.

Record runtime limitations rather than papering over unsupported behavior.

# Review gate

Before acceptance, review the implementation against:

- GitHub Issue #2;
- this plan;
- `documentation/CURRENT.md`;
- `documentation/DECISIONS.md`;
- the actual diff;
- validation evidence.

Ask specifically:

1. Was delegation actually useful?
2. Did the task contract reduce ambiguity?
3. Did capability routing remain natural?
4. Did the context packet improve planning without dumping irrelevant history?
5. Is the resulting system still easy to understand and debug?

# Expected output

- working `repository-exploration` capability;
- working `context-strengthening` capability;
- one representative bounded task contract;
- deterministic validation additions where justified;
- runtime validation notes;
- minimal CURRENT/CLOUD-BRIEF updates only if accepted state changes.

# Definition of done

This slice is done only when it works end-to-end well enough to inform whether the pattern should be reused. Do not promote it into a broader framework based solely on the design looking clean on paper.
