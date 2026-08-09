---
id: PLAN-ARW-CONTROL-PLANE-QUALITY-HARDENING-20260809-001
issue: 24
status: execution-ready
date: 2026-08-09
scope: control-plane quality hardening
---

# Control-plane quality hardening

## Objective

Make the reconciled control plane reliably discoverable, composable, scoped, and routable at runtime. This is a quality pass over surviving components, not another architecture expansion.

The execution must answer, in order:

```text
SHOULD THIS COMPONENT EXIST?
→ WHAT SHOULD IT BE CALLED?
→ WHEN SHOULD IT LOAD?
→ HOW SHOULD IT EXECUTE?
→ HOW DOES IT HAND OFF TO THE NEXT COMPONENT?
→ HOW IS IT VALIDATED?
```

Do not polish a component before proving it deserves to survive.

## Accepted baseline

Treat these as accepted unless live evidence exposes a bounded contradiction:

- `documentation/OPERATING-WORKFLOW.md` owns the canonical global semantic lifecycle.
- Skills are reusable agent-facing procedures/capabilities.
- Scripts/tools own deterministic operations.
- Agents exist for isolation, permissions, independent judgment, specialized tools, or meaningful autonomy.
- Machine workflows survive only for real machine-consumed lifecycle/state/gate/recovery semantics.
- `AGENTS.md` owns scoped normative behavior, not architecture history.
- Ordinary consequential work uses Issue -> optional PLAN -> coherent branch -> implementation -> validation/review -> PR/CI.
- `ops/changes` is historical/exceptional, not the default execution surface.
- No CHG/audit/proof-only artifact family may be introduced.

## Execution mode

Create one fresh branch from current `main`, for example:

```text
refactor/control-plane-quality-hardening
```

Do not create one branch per skill, per quality dimension, review lens, or validator.

The parent owns final dispositions and architecture consistency. Read-only subagents may be used for parallel inventory or independent review when useful. Do not stop after audit; implement the accepted quality changes, validate, repair bounded failures, open one reviewable PR, and complete the Issue.

---

# Phase 0 — Live orientation and consumer inventory

Before editing:

1. Read `AGENTS.md`, `documentation/OPERATING-WORKFLOW.md`, `CURRENT.md`, `DECISIONS.md`, `CLOUD-BRIEF.md`, Issue #24, and this PLAN.
2. Inventory every active skill from the live `skills/` tree and its frontmatter.
3. Inventory every active agent/profile and the applicable instruction chain.
4. Inventory every retained machine workflow, validator, runtime/CI consumer, and references to workflow IDs.
5. Inventory all references to active skill names before any rename.
6. Identify installed/built-in capabilities that may already own a local skill's behavior.

Do not create a durable inventory report. Temporary analysis stays in execution context; final dispositions belong in the PR/Issue and accepted canonical state only.

---

# Phase 1 — Resolve workflow authority

## Target

```text
OPERATING-WORKFLOW.md
= canonical global semantic lifecycle

Franky workflow
= specialized governed control-plane mutation contract
  used only when its stronger gates/contracts have a named consumer or risk reason
```

Inspect actual consumers of `workflows/franky/franky.yaml` and `lifecycle-contract.yaml` before changing metadata.

Resolve whether `canonical`, `entrypoint`, and `workflow_only` are Franky-family-local or incorrectly imply global authority. Adjust metadata/docs/validator semantics minimally so ordinary work is not forced through Franky.

Revisit `write-change-record` and `local-git-finalize`: a retained specialized Franky path may require them only if a named consumer needs them. They must not reintroduce mandatory `change.yaml` for ordinary work.

Retain safety guarantees that still protect real operations.

Validation:

- global and specialized workflow authority do not conflict;
- retained workflow validators pass;
- ordinary work can follow the global semantic lifecycle without Franky ceremony.

---

# Phase 2 — Capability-existence gate for every active skill

Before naming or description work, classify every active skill:

```text
KEEP
MERGE
RETIRE
DEFER
```

A skill survives only if it has a recurring/discriminative trigger, a stable reusable procedure worth preserving, useful judgment/boundaries beyond one mechanical command where applicable, and no stronger existing capability already owns the behavior.

Use this decision order:

```text
Does the recurring capability deserve skill packaging?
├─ no → RETIRE or MERGE; preserve useful deterministic tools where justified
└─ yes
   ↓
continue to naming
```

Explicitly challenge these cases:

### `install-project-link`
Keep independently only if project-link operations are recurring outside bootstrap/inheritance. Otherwise merge the procedure/tool into the owning project capability while preserving link safety.

### `external-handoff`
Keep only if cross-runtime/external execution requires a stable transformation, approval, evidence, and rollback procedure beyond an ordinary task contract. Otherwise retire the wrapper and use task-contract + parent reasoning.

### `franky-workflow-organizer`
If the surviving behavior is mostly YAML validation, retire the skill and keep the deterministic validator. Retain/repackage a skill only if real recurring lifecycle-design judgment exists.

Do not improve names/descriptions for a skill that should be removed.

---

# Phase 3 — Naming audit for retained skills

## Convention

Prefer capability-centric names using:

```text
<object>-<operation>
```

Preferred operation vocabulary:

```text
bootstrap
link
handoff
installation
audit
maintenance
validation
migration
promotion
closeout
```

Avoid vague synonyms such as:

```text
manager
organizer
handler
helper
support
controller
coordinator
```

unless they have a real stable distinction.

Persona prefixes such as `franky-` survive only when persona/permission/runtime ownership is materially part of the capability. Role routing and capability routing remain separate:

```text
TASK
→ required capability
→ delegation useful?
→ role/agent if needed
```

For each retained skill assign:

```text
KEEP NAME
RENAME
```

Rename only when routing/ownership gain exceeds reference churn.

## Candidate hypotheses to test

| Current | Candidate / challenge |
| --- | --- |
| `project-bootstrap` | KEEP |
| `external-handoff` | `execution-handoff` if retained |
| `install-project-link` | `project-link` if retained |
| `franky-agent-installer` | `agent-profile-installation` if role-neutral |
| `franky-cron-installer` | `scheduler-installation` if scheduler lifecycle is the abstraction |
| `franky-guidance-manager` | `guidance-maintenance` |
| `franky-maintenance` | `control-plane-audit` if diagnosis is primary; otherwise `control-plane-maintenance` |
| `franky-promotion` | `control-plane-promotion` or DEFER if only future portability/export needs it |
| `franky-source-migration` | `source-migration` if role-neutral |
| `franky-workflow-organizer` | RETIRE/validator-only, or `workflow-design` only if judgment capability survives |
| `shared-session-closeout` | `session-closeout` |

These are hypotheses, not forced outcomes.

Where a rename is accepted, update every reference atomically: preferred skill lists, workflows, CI, docs, tests, installation/deployment references, and any runtime metadata.

---

# Phase 4 — Description and SKILL.md hardening

Only retained skills reach this phase.

## Frontmatter description contract

Treat `description` as routing metadata. It should compactly communicate:

```text
ACTION
+ TASK / OBJECT TYPE
+ WHEN TO USE
+ IMPORTANT BOUNDARY / WHEN NOT TO USE when overlap risk exists
```

Avoid broad verbs (`manage`, `support`, `improve`, `handle`) without discriminative conditions.

For overlapping skills, add a concise negative boundary where useful.

## Body contract

Each retained skill should expose enough of:

- purpose;
- positive trigger/use condition;
- required context/inputs;
- reusable procedure;
- expected output/result;
- deterministic helper usage;
- mutation/safety boundary;
- stop/escalation condition;
- validation expectation;
- ownership/non-goals where neighbors overlap.

Do not force identical headings or schema-like frontmatter. Optimize clarity and progressive disclosure.

Move optional provider/runtime-specific material into `references/` only when it is useful but not needed on every invocation. Keep capability-specific deterministic helpers with the skill unless there is a real independent global consumer.

---

# Phase 5 — Nearest-neighbor and contrastive routing evaluation

For each overlapping/high-value retained skill, identify 1-3 nearest routing neighbors during analysis. Do not create a permanent neighbor registry.

Use pairwise contrast to improve descriptions and boundaries.

Examples:

```text
project-bootstrap ↔ guidance-maintenance
project-bootstrap ↔ project-link (if retained)
control-plane-audit/maintenance ↔ workflow validator/tool
```

Create a small evaluation set with these classes:

1. positive trigger;
2. negative trigger;
3. nearest-neighbor contrast;
4. `expected: none` ordinary task;
5. ambiguous case where inspection/clarification is better than loading multiple skills.

Prefer contrastive pairs, e.g.:

```text
A: Set up a new research project with README, metadata and analysis folders
   → project-bootstrap

B: Update AGENTS.md so analysis scripts always preserve raw data
   → guidance-maintenance
```

```text
A: Link this existing project into the Codex workspace
   → project-link if retained

B: Create the project structure
   → project-bootstrap
```

```text
A: Audit stale skill/workflow references across the control plane
   → control-plane-audit/maintenance

B: Validate this workflow YAML
   → deterministic workflow validator unless workflow-design judgment is actually required
```

## Static vs behavioral evidence

Never conflate:

```text
STATIC QUALITY CHECK
= metadata/fixture syntax/obvious overlap checks

BEHAVIORAL ROUTING EVAL
= actual Codex skill discovery/selection
```

Probe the real runtime. If behavioral skill selection cannot be observed reliably, state that limitation and retain only the smallest useful static/contrastive fixture. Do not pretend a metadata lint proves LLM routing.

#24 does not own model choice, reasoning effort, parent-vs-subagent policy, parallelism, or fallback experiments. Those remain #8.

Do not build a router, vector index, telemetry platform, benchmark service, or routing database.

---

# Phase 6 — Scope AGENTS.md by semantic authority

Audit every paragraph in the active instruction chain.

For root `AGENTS.md`, require both:

1. the rule applies broadly across the repository; and
2. the rule materially changes agent behavior.

If it merely explains architecture, move/link it to documentation. If it governs one subtree, move it to the nearest scoped owner when that materially improves context efficiency.

Candidate scoped surfaces, only if justified:

```text
agents/AGENTS.md
skills/AGENTS.md
workflows/AGENTS.md
ops/AGENTS.md only if enough unique rules exist
```

Likely responsibilities:

- root: authority, repo-wide invariants, orientation path, broad parent/subagent boundaries, global mutation/Git safety, durable-state rules;
- `agents/AGENTS.md`: profile/role/delegation rules;
- `skills/AGENTS.md`: skill existence/naming/discovery/locality/quality rules;
- `workflows/AGENTS.md`: workflow admission, consumer/state/gate and validator rules;
- `ops/AGENTS.md`: only genuinely shared deterministic machinery rules.

Do not optimize to a hard line count. Optimize semantic density and progressive disclosure. Do not duplicate the full `OPERATING-WORKFLOW.md` lifecycle into AGENTS files.

---

# Phase 7 — Harden agent contracts

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

Every retained agent must justify itself through at least one real property:

- permission boundary;
- context isolation;
- independent judgment;
- specialized tool access;
- meaningful autonomy boundary.

Do not create new agents unless a real unresolved isolation/permission requirement makes parent/skill execution insufficient.

Keep role identity independent of skill/capability and model/reasoning policy.

---

# Phase 8 — Clarify component linking semantics

Update the smallest canonical semantic surface needed to make this path obvious:

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

Use these as **review vocabulary only**, not mandatory serialized fields:

### Skill
`trigger -> inputs/context -> procedure -> output/result -> side effects -> stop conditions -> validation`

### Agent
`entry/use condition -> authority -> task contract -> allowed tools/scope -> return contract -> escalation`

### Workflow
`entry condition -> state -> transitions -> gates -> failure/recovery -> exit condition -> consumer`

### Tool/script
`input -> deterministic operation -> output -> error conditions`

Do not create `component-interface.schema.yaml`, a universal registry/database, or mandatory new frontmatter taxonomy. A schema is allowed only in a later Issue if repeated real execution proves file-first metadata insufficient.

---

# Phase 9 — Independent quality review and bounded repair

Use the 0-2 review rubric:

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

The rubric supports judgment only. Do not create a permanent scorecard artifact.

Review the system as a whole for:

- discoverability;
- composability;
- locality;
- authority clarity;
- observability/debuggability;
- deterministic validation;
- evolvability;
- context efficiency/progressive disclosure.

Use an independent reviewer when useful. Repair material findings inside #24 scope, then revalidate.

---

# Required validation

Run all relevant current validation plus any minimal new quality checks introduced by this pass:

- retained skill validators and affected skill-specific tests;
- workflow contract validation for retained workflows;
- agent/profile validation;
- task-contract/schema checks where applicable;
- routing fixture/static checks if added;
- actual behavioral routing probes where observable;
- Git allowlist;
- `git diff --check`;
- hosted `Control-plane validation` CI.

For every rename, verify all references and installed/deployment hints. No stale old name may remain except intentional historical prose.

---

# Durable-state updates

Update only accepted truth:

- `CURRENT.md` for deployed state;
- `DECISIONS.md` only for durable architectural choices that require rationale;
- `OPERATING-WORKFLOW.md` for canonical workflow/linking semantics;
- scoped `AGENTS.md` only for normative behavior.

Do not create separate quality reports, routing reports, CHG folders, audit records, result files, or component scorecards.

---

# Explicit non-goals

Do not implement:

- #8 model/reasoning/delegation router;
- #9 memory;
- #16 research infrastructure;
- #12 portability/plugin architecture;
- a new workflow engine;
- a capability/component registry;
- a universal interface schema;
- one skill per project/file format;
- new personas for conceptual stages;
- broad project migration.

---

# Acceptance mapping

Issue #24 is complete only when:

- AC-01: global vs specialized Franky workflow authority is unambiguous;
- AC-02: every active skill has a capability-existence disposition before polish;
- AC-03: every retained skill has a deliberate KEEP NAME/RENAME decision;
- AC-04: retained descriptions are discriminative and nearest-neighbor conflicts are reduced;
- AC-05: retained skill bodies expose stable procedure/boundary/tool/validation semantics;
- AC-06: a minimal contrastive routing eval exists and static vs behavioral evidence is clearly distinguished;
- AC-07: root/nested AGENTS scopes are lean, non-duplicative, and semantically local;
- AC-08: every retained agent has an agent-specific justification and bounded return contract;
- AC-09: task -> capability -> skill/agent/tool -> validation/review -> durable state is obvious from canonical semantics;
- AC-10: relevant deterministic validation and hosted CI pass;
- AC-11: no new quality bureaucracy, router, workflow engine, universal schema, or registry is introduced.

---

# Stop / escalation

Stop only if:

1. a rename would break an external/runtime consumer that cannot be safely migrated;
2. skill-discovery behavior cannot be observed and no honest bounded test can approximate the required evidence;
3. Franky workflow metadata is consumed by an external runtime whose semantics conflict with the intended specialized scope;
4. AGENTS precedence/runtime behavior differs materially from repository assumptions and cannot be verified;
5. required work expands into #8/#9/#12/#16 or another separately owned architecture concern;
6. deletion/merge would destroy unique provenance or behavior not recoverable from Git/GitHub.

Do not stop for ordinary naming, description, reference migration, scoped-instruction, merge/retire, or validator changes inside #24.

---

# Final report

The PR/Issue final report should contain only:

1. workflow authority outcome;
2. final active skill surface;
3. retired/merged skills and preserved deterministic tools;
4. final names and rename rationale;
5. description/neighbor-routing improvements;
6. static and behavioral routing-eval results/limitations;
7. final AGENTS scope map;
8. agent-contract changes;
9. component-linking clarification;
10. tests/validators/CI results;
11. deferred issues outside #24.

No separate result artifact is required.
