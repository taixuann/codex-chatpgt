---
id: PLAN-ARW-CONTROL-PLANE-QUALITY-HARDENING-20260809-001
issue: 24
status: execution-ready
date: 2026-08-09
scope: control-plane quality hardening
---

# Control-plane quality hardening

## Objective

Improve the quality of the surviving control-plane architecture after the #19/#22/#13/#21 reconciliation so runtime routing, skill discovery, scoped instructions, agent boundaries, workflow authority, and component handoffs are reliable rather than merely structurally clean.

This PLAN executes Issue #24. It is a quality pass over existing components, not another architecture expansion.

## Accepted baseline

Treat the following as accepted unless live evidence exposes a bounded contradiction:

- `documentation/OPERATING-WORKFLOW.md` owns the canonical general semantic lifecycle.
- Skills are reusable agent-facing procedures/capabilities.
- Scripts/tools own deterministic operations.
- Agents exist for runtime isolation, permission boundaries, independent judgment, specialized tool access, or meaningful autonomy.
- Machine-readable workflows survive only when a real machine consumer and lifecycle/state/gate value justify them.
- Root and nested `AGENTS.md` files are scoped normative instructions, not general architecture documentation.
- Ordinary consequential work uses Issue -> optional PLAN -> coherent implementation branch -> validation/review -> PR/CI.
- `ops/changes` is historical/exceptional, not a default execution artifact surface.
- No new CHG/audit/proof-only artifact family is permitted in this execution.

## Current quality risks to resolve

1. `workflows/franky/franky.yaml` still declares `canonical: true`, `entrypoint: true`, and `workflow_only`, which can conflict with the accepted global semantic workflow.
2. Active skill names and descriptions have uneven routing quality. Some are capability-centric and discriminative; some remain persona-prefixed or broad.
3. Skill bodies vary in how explicitly they expose trigger, input/context, procedure, output, stop conditions, validation, and ownership boundaries.
4. Root `AGENTS.md` contains several concerns that may be more appropriately scoped to `agents/`, `skills/`, `workflows/`, or canonical documentation.
5. Agent contracts are not uniformly expressed as bounded runtime interfaces.
6. Current validation is strong on syntax/contracts but weak on skill-routing discrimination and component-linking behavior.

## Execution mode

Use one fresh coherent branch from current `main`, for example:

```text
refactor/control-plane-quality-hardening
```

Do not create one branch per skill, one branch per quality dimension, or proof/review branches.

The parent agent owns final dispositions and architecture consistency. Use bounded read-only subagents for parallel inventory/review only when that materially reduces context or improves independence.

## Phase 0 — Orient and inventory current live surface

Before editing:

1. Read:
   - `AGENTS.md`;
   - `documentation/OPERATING-WORKFLOW.md`;
   - `documentation/CURRENT.md`;
   - `documentation/DECISIONS.md`;
   - `documentation/CLOUD-BRIEF.md`;
   - Issue #24;
   - this PLAN.
2. Inventory every active skill on `main` by actual directory and `SKILL.md` frontmatter.
3. Inventory every active agent/profile and applicable `agents/AGENTS.md`.
4. Inventory every retained machine-readable workflow and actual validator/runtime consumer.
5. Inventory the active AGENTS instruction chain and note which rules apply globally versus to one subtree.
6. Record the current references to any skill or workflow name before rename decisions.

Do not create a separate durable inventory report. Keep temporary analysis in the active execution context and summarize accepted dispositions in the PR/Issue unless a machine-consumed fixture is explicitly justified below.

## Phase 1 — Resolve workflow authority

### Target

Make authority unambiguous:

```text
OPERATING-WORKFLOW.md
= canonical global semantic lifecycle

Franky workflow
= specialized governed control-plane mutation contract
  invoked only when its explicit stronger lifecycle is required
```

### Required actions

1. Inspect actual consumers of `workflows/franky/franky.yaml` and `lifecycle-contract.yaml`.
2. Determine whether `canonical`, `entrypoint`, and `workflow_only` refer only to Franky's specialized workflow family or incorrectly imply global control-plane authority.
3. Adjust metadata, naming, documentation, or validator semantics minimally so ordinary work is not required to route through Franky.
4. Keep stronger Franky approval/audit semantics only where a named operation or consumer justifies them.
5. Revisit mandatory `write-change-record` / `local-git-finalize` stages. They must not force `change.yaml` for ordinary work after #21 unless a specialized Franky consumer genuinely requires that record.
6. Do not remove safety guarantees merely to simplify syntax.

### Validation

- canonical documentation and workflow metadata do not contradict each other;
- workflow validators still pass for any retained machine contract;
- no ordinary task is semantically forced through Franky when the general lifecycle is sufficient.

## Phase 2 — Audit skill names

Treat skill names as part of discovery/routing quality.

For every active skill assign one of:

```text
KEEP NAME
RENAME
MERGE
RETIRE
DEFER
```

### Name-quality criteria

Score/judge:

- capability-centric when role-neutral;
- concrete and discriminative;
- stable across temporary implementations;
- not broader than the procedure;
- distinct from neighboring skills;
- persona prefix only when persona/permission ownership is materially part of the capability;
- low reference churn relative to routing gain.

### Important rule

Do not systematically strip `franky-` from every surviving skill. Keep it when the capability is genuinely Franky/control-plane-role specific. Rename only when the procedure is reusable independently of Franky and the new name improves discovery/ownership.

### Expected candidates to challenge

At minimum inspect:

- `external-handoff`;
- `project-bootstrap`;
- `install-project-link`;
- `franky-agent-installer`;
- `franky-cron-installer`;
- `franky-guidance-manager`;
- `franky-maintenance`;
- `franky-promotion`;
- `franky-source-migration`;
- `franky-workflow-organizer`;
- `shared-session-closeout`;

Do not assume this list is exhaustive; use the live tree.

## Phase 3 — Harden skill descriptions and bodies

### Frontmatter description contract

Every active skill description should compactly communicate:

```text
ACTION
+ TASK/OBJECT TYPE
+ WHEN TO USE
+ IMPORTANT BOUNDARY / WHEN NOT TO USE when overlap risk exists
```

Descriptions are routing metadata, not miniature documentation essays.

Challenge vague wording such as `manage`, `support`, `maintain`, `handle`, or `improve` when it lacks discriminative task conditions.

### Body contract

For each retained skill, make sure the skill exposes enough of:

- purpose;
- positive trigger/use condition;
- required input/context;
- reusable procedure;
- expected output/result;
- deterministic tool/script invocation where applicable;
- mutation/safety boundaries;
- stop/escalation conditions;
- validation expectation;
- ownership/non-goals when neighboring capabilities overlap.

Do not force identical headings/templates if the content is naturally concise. Optimize for clarity and progressive disclosure, not template compliance.

### Locality

If a deterministic helper is owned by one skill, keep it with that skill unless a real independent global consumer justifies `ops/scripts/` ownership.

## Phase 4 — Add the smallest useful skill-routing eval

### Purpose

Test whether metadata actually distinguishes capabilities.

### Minimum case classes

For overlapping/high-value skills include representative:

1. positive trigger;
2. negative trigger;
3. neighboring-skill discrimination;
4. ambiguous prompt where the correct behavior is inspect/clarify rather than activate many skills.

### Example semantic cases

```text
Set up a new scientific IV project
→ project-bootstrap

Create or tighten persistent instructions for this subtree
→ guidance-management capability

Audit stale cross-component control-plane references
→ control-plane maintenance capability

Fix an ordinary Python function
→ none of the control-plane maintenance/bootstrap skills
```

### Packaging decision

First probe what the actual Codex runtime exposes for skill discovery/selection observation.

- If selection can be exercised/observed reliably, create one small runnable routing-eval fixture/script/test surface.
- If not, retain one minimal machine-readable or testable case fixture only if it still provides deterministic description-overlap checks; otherwise keep cases in the Issue/PR acceptance evidence and record the runtime limitation.

Do not build a router, vector database, telemetry service, or benchmark framework.

## Phase 5 — Scope AGENTS.md correctly

Audit each paragraph/rule using:

> Does this rule apply to nearly every task under this directory scope?

### Root target

Root `AGENTS.md` should focus on:

- repository authority and canonical references;
- global invariants;
- orientation path;
- broad parent/subagent authority boundaries;
- global mutation/Git/GitHub safety;
- durable-state rules that truly apply repo-wide.

Do not duplicate the full lifecycle from `OPERATING-WORKFLOW.md`.

### Scoped candidates

Use existing or add only justified scoped files:

```text
agents/AGENTS.md
skills/AGENTS.md
workflows/AGENTS.md
ops/AGENTS.md only if needed
```

Potential ownership:

- `agents/AGENTS.md`: profile/role/delegation boundaries;
- `skills/AGENTS.md`: skill naming, discovery, authoring, locality, and quality rules;
- `workflows/AGENTS.md`: workflow admission, consumer/state/gate requirements, validation;
- `ops/AGENTS.md`: only shared deterministic machinery rules if enough unique guidance exists.

Avoid creating nested AGENTS files containing only a few duplicated sentences.

## Phase 6 — Harden agent contracts

For every active agent/profile answer:

```text
WHY AGENT?
WHEN TO USE?
AUTHORITY?
INPUT / TASK CONTRACT?
TOOLS / WRITE SCOPE?
LOCAL AUTONOMY?
RETURN CONTRACT?
WHEN NOT TO USE?
ESCALATION?
```

An agent must justify itself through at least one real property:

- permission boundary;
- context isolation;
- independent judgment;
- specialized tool access;
- meaningful autonomy boundary.

Do not create new agents in this phase unless a real unresolved runtime isolation/permission requirement makes ordinary parent/skill execution insufficient.

## Phase 7 — Clarify component linking contract

Update the smallest canonical semantic surface needed to make this path explicit:

```text
TASK / ISSUE
→ objective + scope + constraints
→ required capability
→ candidate skill/procedure
→ delegation useful?
→ parent or bounded agent
→ deterministic tool/script when needed
→ result
→ deterministic validation
→ independent review when justified
→ acceptance
→ durable destination
```

Clarify what each component must expose so the next stage can consume it.

Preferred interface vocabulary:

### Skill

```text
trigger
inputs/context
procedure
output/result
side effects
stop conditions
validation
```

### Agent

```text
entry/use condition
authority
task contract
allowed tools/scope
return contract
escalation
```

### Workflow

```text
entry condition
state
transitions
gates
failure/recovery
exit condition
consumer
```

### Tool/script

```text
input
deterministic operation
output
error conditions
```

Do not create a new universal registry/schema unless repeated implementation evidence shows that the existing file metadata cannot express these contracts reliably.

## Phase 8 — Quality review and bounded repair

Use the following 0-2 component rubric as a review aid:

1. trigger/entry clarity;
2. unique responsibility;
3. input/output contract;
4. deterministic validation;
5. boundary/stop condition;
6. evidence of real reuse.

Interpretation:

```text
10-12 strong
7-9 improve in place
4-6 merge/generalize/repackage candidate
0-3 retire candidate
```

Do not create a permanent scorecard file merely to store numbers. Summarize material final dispositions in the PR and update canonical docs only where the accepted architecture changes.

Also review the whole system for:

- discoverability;
- composability;
- locality;
- authority clarity;
- observability/debuggability;
- deterministic validation;
- evolvability;
- context efficiency/progressive disclosure.

Use an independent reviewer for this final architecture-quality review if the runtime supports it and independence adds value.

Repair material findings inside Issue #24 scope, then revalidate.

## Required validation

Run all relevant existing repository validation plus any minimal new tests introduced by this pass, including at least:

- skill validators/quality checks;
- skill-specific test suites affected by rename/description/procedure changes;
- workflow contract validation for retained workflows;
- agent/profile validation;
- task-contract/schema checks where applicable;
- Git allowlist and `git diff --check`;
- hosted `Control-plane validation` CI.

Where names are changed, verify all references, preferred-skill hints, workflow dependencies, CI paths, docs, tests, and installation/deployment references.

## Durable-state updates

Update only what becomes accepted truth:

- `CURRENT.md` for final deployed state;
- `DECISIONS.md` only for durable architectural choices that need rationale;
- `OPERATING-WORKFLOW.md` for canonical semantic/interface clarifications;
- scoped `AGENTS.md` only for normative instructions.

Do not create separate quality reports, CHG folders, audit records, routing reports, or result files by default.

## Non-goals

Do not implement:

- #8 model/reasoning router;
- #9 persistent memory;
- #16 research workflow infrastructure;
- #12 portability/plugin packaging;
- a new workflow engine;
- a capability registry/database;
- one skill per project/file format;
- new personas for conceptual stages;
- broad project migration.

## Acceptance mapping

Issue #24 is complete when:

- AC-01: global vs specialized workflow authority is unambiguous;
- AC-02: every active skill has a deliberate name disposition;
- AC-03: active descriptions are discriminative enough for routing;
- AC-04: retained skill bodies expose appropriate procedure/boundary/validation semantics;
- AC-05: a minimal routing/discovery eval exists or the runtime limitation is explicitly demonstrated with the smallest alternative evidence;
- AC-06: root/nested AGENTS scopes are lean and non-duplicative;
- AC-07: every active agent has a clear agent-specific justification and return boundary;
- AC-08: component linking is explicit enough to follow without conversation history;
- AC-09: deterministic validation and hosted CI pass;
- AC-10: no new quality bureaucracy or orchestration layer is introduced.

## Stop / escalation

Stop and report only if:

1. a rename would break an external/runtime consumer that cannot be safely migrated;
2. current Codex skill-discovery behavior cannot be observed and no honest bounded test can approximate it;
3. Franky workflow metadata is consumed by an external runtime whose semantics conflict with the intended specialized scope;
4. AGENTS precedence/runtime behavior differs materially from the repository assumptions and cannot be verified locally;
5. a required change would expand into #8/#9/#12/#16 or another separately owned architecture concern.

Do not stop for ordinary naming, description, reference migration, or scoped-instruction decisions inside this PLAN.

## Final report

The PR/Issue final report should contain only:

1. workflow authority outcome;
2. final active skill names and any renames/merges/retirements;
3. description/routing-quality improvements;
4. routing-eval result and runtime limitations;
5. final AGENTS scope map;
6. agent-contract changes;
7. component-linking clarification;
8. tests/validators/CI results;
9. deferred issues outside #24.

No separate result artifact is required.
