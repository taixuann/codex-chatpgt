---
id: PLAN-ARW-ARCHITECTURE-RECONCILIATION-20260809-001
issue: 22
status: reconciled
repository: taixuann/codex-chatpgt
created: 2026-08-09
---

# Objective

Reconcile the control-plane semantic architecture against real execution evidence from Issue #19 / PR #20 so later skill/workflow rationalization (#13) and repository cleanup (#21) can execute against one stable target.

This PLAN is intentionally bounded. It does not authorize a mass cleanup of all legacy skills, workflows, or `ops/changes` records.

## Current-state supersession note — 2026-08-10

This is the historical Issue #22 semantic baseline. Its Phase-3 inventory
predates the creator-gated #35 reconciliation and must not be read as the
current workflow catalog. D-009 and
`PLAN-ARW-SYSTEM-SKILLS-V2-20260810-001.md` supersede the historical `KEEP`
rows: all seventeen unconsumed `workflows/franky/**` YAMLs are now retired,
and only `workflows/AGENTS.md` remained as admission policy at the time of this
2026-08-09 plan; this is historical evidence, not current policy. The semantic
Agent/Skill/Script/Workflow model below remains valid as a design record.

# Starting State

The repository currently contains two partially conflicting architecture generations.

The newer canonical human-readable model in `documentation/OPERATING-WORKFLOW.md` says:

- capability need comes before agent/skill selection;
- skills package stable reusable procedures;
- deterministic work belongs in scripts/tools;
- agents exist for isolation/permissions/judgment;
- machine-readable workflows are justified only when state, gates, resume/recovery, deterministic routing, or machine consumption provide real runtime value;
- Issue -> optional PLAN -> implementation -> PR/CI is the preferred execution/evidence chain.

The older Franky runtime surface still includes:

- `WF-FRANKY-CANONICAL` with 9 lifecycle steps and 18 nested pipelines;
- mandatory audit/preview/approval/change-record/local-git-finalize semantics;
- `change.yaml`, workflow-run envelopes, change IDs, exact-preview digests, and other legacy evidence requirements;
- workflow factory/organizer capabilities that can manufacture additional workflow packages;
- goal/session packages and closeout behavior tied to `ops/changes` or AI Labs goal-package artifacts.

Issue #19 / PR #20 supplied the first strong real implementation evidence:

- a useful deterministic file-first bootstrap primitive exists;
- no workflow family is required for that behavior;
- CHG/audit/proof-only artifacts were unnecessary for the implementation;
- the remaining architecture question is whether the agent-facing reusable procedure should be packaged as a `project-bootstrap` skill around the deterministic materializer.

# External Design Constraints

Use external guidance only as design evidence, not as a substitute for runtime proof.

Key principles:

1. OpenAI skill guidance: a skill should package a repeatable task concisely; `SKILL.md` is required and scripts/references/assets are bundled only when they directly support the task.
2. OpenAI skill-creator guidance: avoid extraneous README/quick-reference/changelog-style files inside skills; use progressive disclosure and colocate deterministic helpers with the capability.
3. OpenAI Agents SDK: prefer a small primitive set and choose LLM-led or code-led orchestration according to the task instead of assuming a custom workflow DSL.
4. OpenAI Codex usage guidance: use well-scoped Issue-like prompts and persistent `AGENTS.md` context.
5. Google engineering practice: keep changes small/self-contained and reject speculative generalization/over-engineering.
6. ADR/MADR: record durable architecture decisions leanly and explicitly rather than letting current-state files become historical essays.

# Accepted Semantic Target

Unless runtime evidence contradicts it, reconcile toward:

```text
Agent
= runtime isolation / permission / context / independent judgment boundary

Skill
= reusable agent-facing procedure/capability with discriminative trigger

Script / Tool
= deterministic operation

Workflow
= machine-consumed lifecycle where state/order/gates/resume/failure transitions add real value

AGENTS.md
= normative scoped operating rules

Issue
= what must become true

PLAN
= consequential implementation design; optional for small changes

PR + CI
= actual changes + validation/review evidence

CURRENT
= accepted current snapshot

Decision record
= accepted durable rationale
```

Default execution:

```text
TASK
-> ORIENT
-> reason / select capability
-> parent or bounded subagent when useful
-> skill/procedure when relevant
-> deterministic tool when appropriate
-> validate / bounded repair
-> independent review only when useful
-> PR / acceptance
```

A conceptual stage does not earn a new file, skill, workflow, agent, or branch by itself.

# Execution Strategy

## Phase 0 — Resolve #19 packaging boundary

Do not merge a bare implementation pattern into architecture by accident.

Inspect PR #20 and decide whether the reusable bootstrap procedure has a stable trigger and procedure independent from the deterministic materializer.

Preferred target to prove:

```text
skills/control-plane/project-bootstrap/
├── SKILL.md
├── scripts/
│   └── bootstrap_file_project.py
└── tests/ or equivalent colocated test surface
```

`SKILL.md` should own:

1. classify new vs existing project;
2. inspect relevant project state and instructions;
3. derive required artifact/module surface;
4. reuse existing capabilities before local creation;
5. derive/validate an artifact map;
6. invoke deterministic materialization;
7. validate produced structure and project/knowledge boundaries;
8. stop/escalate when architecture or destructive scope is unclear.

The script should own only deterministic artifact-map validation/materialization and safety checks.

Do not create a workflow or second `file-workbench` skill without new evidence.

If the script remains under `ops/scripts/`, identify at least one independent global consumer outside project bootstrap that justifies global ownership.

## Phase 1 — Confirm architecture responsibility matrix

Read and reconcile:

- `AGENTS.md`;
- `documentation/architecture/workflow/operation.md`;
- `documentation/CURRENT.md`;
- `documentation/architecture/decisions.md`;
- `documentation/architecture/workflow/evolution.md`;
- `documentation/archive/20260901/GOAL-PLAN-GRAPH.md`;
- `documentation/architecture/knowledge/research.md`;
- `agents/AGENTS.md`;
- active runtime configuration relevant to skill/workflow discovery.

Update the smallest canonical surfaces required so all documents agree on agent / skill / script / workflow / Issue / PLAN / PR responsibilities.

Do not migrate `DECISIONS.md` to individual ADR files in this phase; #21 owns later physical migration if still justified.

## Phase 2 — Inventory and confirm all skill dispositions

Inspect every current skill, its scripts/references/templates, actual consumers, and recent runtime evidence.

Use exactly one disposition:

- KEEP
- GENERALIZE
- MERGE
- REPLACE
- RETIRE
- DEFER

Initial hypotheses to verify:

### Generalize / keep core procedure

- `franky-agent-installer`
  - retain adapter validator/template behavior;
  - remove unnecessary Franky naming and stale fixed-model assumptions.

- `franky-cron-installer`
  - retain only if scheduler-specific mutation/approval semantics remain real;
  - generalize to scheduler management.

- `franky-guidance-manager`
  - retain scoped instruction-chain/AGENTS maintenance;
  - generalize naming.

- `franky-source-migration`
  - substantial procedure + deterministic scripts/references;
  - preserve/generalize, likely DEFER execution until #12 portability work.

- `shared-session-closeout`
  - preserve only if closeout/resume behavior remains repeatedly useful;
  - remove goal-package / CHG / Trekker assumptions not required by the current operating model.

### Generalize / merge

- `franky-external-handoff`
  - generalize to role-neutral execution handoff or merge into operating guidance if a skill adds negligible procedure value.

- `franky-project-linker`
  - merge link behavior into project-bootstrap / #10 inheritance where appropriate;
  - retain deterministic link-audit helper if independently useful.

- `franky-maintenance`
  - preserve deterministic audit/validators;
  - remove mandatory audit-record / `ops/changes` writing from ordinary maintenance;
  - avoid a giant catch-all skill after cleanup.

- `franky-promotion`
  - preserve only if Codex -> AI Labs export/promotion remains a real operational destination;
  - otherwise defer to #12 portability/distribution semantics.

### Replace / retire candidates

- `franky-github-review`
  - replace with installed `gh-address-comments` unless unique governance is proven.

- `franky-skill-installer`
  - replace with installed `skill-installer` / `skill-creator`; retain only unique local validation if necessary.

- `franky-goal-session`
  - retire/replace legacy GOAL/TASKS/walkthrough/revision/PROMOTION package semantics with Issue/PLAN/PR model unless a distinct remaining use case is proven.

- `franky-workflow-factory`
  - retire unless a real need for generating machine-consumed stateful workflows survives the workflow audit.

- `franky-workflow-organizer`
  - likely retire as agent-facing skill; preserve deterministic workflow validators only if retained workflows still need them.

For each skill record:

- trigger/purpose;
- real consumers;
- unique procedure;
- deterministic assets;
- overlap/replacement;
- current evidence;
- target disposition;
- follow-up owner (#13, #12, #10, etc.).

Do not rename/delete all skills in this architecture PR.

## Phase 3 — Inventory machine-readable workflows

Inspect the actual workflow tree and validators, including:

- `workflows/franky/franky.yaml`;
- `workflows/franky/lifecycle-contract.yaml`;
- nested `franky-install/` and `franky-maintenance/` pipelines;
- `general-workflow-factory/` pipelines;
- legacy root `install.yaml` / `maintenance.yaml`;
- `workflows/shared/session-closeout.yaml`;
- scripts that validate/route workflow runs;
- any actual runtime code that consumes workflow IDs, versions, run envelopes, gates, or current-step state.

For each workflow/pipeline answer:

1. Who/what consumes it at runtime?
2. Is execution state persistent?
3. Does ordering matter beyond an ordinary skill procedure?
4. Is an approval gate enforced by runtime tooling?
5. Is resume/recovery state used?
6. Does `on_failure` drive real behavior?
7. Could Issue/skill/script/PR semantics provide the same guarantees more simply?

Expected hypotheses to challenge:

- `WF-FRANKY-CANONICAL` is legacy compatibility architecture rather than a required default runtime engine;
- `write-change-record` and `local-git-finalize` are likely obsolete as mandatory workflow stages;
- legacy root `install.yaml` / `maintenance.yaml` should retire when consumers are absent;
- `session-closeout.yaml` likely duplicates the session-closeout skill unless a machine consumer needs the state contract;
- workflow factory/organizer machinery should shrink sharply if few machine workflows survive.

The bounded cleanup removed only the audited proposal-only and duplicate files.
The canonical Franky entrypoint and nested install/maintenance pipelines stay
intact and continue to pass contract validation.

### Confirmed inventory (2026-08-09)

| Surface | Repository consumer | Persistent state / enforced gate | Disposition |
| --- | --- | --- | --- |
| `workflows/franky/franky.yaml` + `lifecycle-contract.yaml` | Nested paths and the hosted layout/contract validators | State, approvals, and recovery are declared in YAML; no local dispatcher or resume store was found | KEEP as compatibility contract; #13 may simplify after runtime evidence |
| `workflows/franky/franky-install/*` | Branches from the canonical Franky entrypoint and install skills | Ordering is declarative; no executable engine was found | KEEP pending #13 consumer review |
| `workflows/franky/franky-maintenance/*` | Branches from the canonical Franky entrypoint and maintenance skills | Declarative gates; no executable engine was found | KEEP pending #13 consumer review |
| `workflows/franky/general-workflow-factory/*` | No machine consumer; proposal-only factory skill | No runtime consumer or resume store was found | RETIRED in #13 cleanup |
| `workflows/feynman/*` | Feynman skill procedures and project-scoped documentation | Domain ordering is documented; no generic dispatcher was found | KEEP as project/domain extensions |
| `workflows/shared/session-closeout.yaml` | No runtime consumer; duplicated the shared skill | No state or enforcement consumer was found | RETIRED in #13 cleanup |
| legacy root `workflows/franky/install.yaml` / `maintenance.yaml` | No references outside their own files and canonical docs | No state or enforcement consumer found | RETIRED in #13 cleanup |

The audit used repository reference searches and validator entrypoints. It did
not infer host runtime behavior from YAML: no executable workflow dispatcher,
resume store, or approval enforcer is present in this checkout. Consequently,
the current files remain compatibility contracts until a real consumer is
observed.

## Phase 4 — Reclassify architecture documents

### Keep / update

- `architecture/workflow/operation.md`: canonical human-readable operating semantics.
- `CURRENT.md`: current accepted snapshot only.
- `architecture/cloud-brief.md`: compact orientation only.

### Reclassify / simplify

- `architecture/workflow/evolution.md`
  - preserve system-change lifecycle semantics;
  - treat as an operating extension/concept unless a machine lifecycle is actually implemented.

- `archive/20260901/GOAL-PLAN-GRAPH.md`
  - preserve lightweight Issue/PLAN/PR relationships;
  - remove pressure toward custom goal packages/registries/graph infrastructure not earned by real use.

- `architecture/knowledge/research.md`
  - preserve objective -> evidence -> understanding -> claims -> hypothesis/test -> result -> promotion semantics;
  - treat as scientific/domain lifecycle semantics, not automatic machine workflow packaging.

No file move is required merely because a better future folder taxonomy exists. #21 owns structural relocation after semantics stabilize.

## Phase 5 — Prepare exact #13 / #21 execution handoff

Update Issue #13 with the confirmed skill/workflow disposition matrix and split implementation into small independently reviewable cleanup groups.

Recommended #13 PR groups, subject to audit evidence:

1. retire/replace thin wrappers and legacy goal/workflow-generation skills;
2. generalize retained agent/scheduler/guidance/maintenance capabilities;
3. reconcile deferred source-migration/promotion boundaries without implementing portability prematurely;
4. remove workflow validators/factory machinery only after retained workflow consumers are known.

Update Issue #21 with only the physical consequences that remain after #13:

- `ops/changes` disposition;
- script locality;
- documentation tree / decision-record migration;
- obsolete validators and artifact wrappers;
- branch/artifact rules.

## Reconciliation result

PR #20 is now merged into `main` as commit `a87a948`; Issue #19 is closed. The
agent-facing bootstrap procedure is therefore confirmed as one reusable
`skills/control-plane/project-bootstrap/` skill colocated with its deterministic helper and
tests. No `file-workbench` skill or project workflow was created.

The fourteen Franky/shared capabilities named in the original hypotheses are
recorded in the companion #13 plan with an evidence-backed disposition matrix.
The bounded #13/#21 physical cleanup is now applied on the rationalization
branch; historical change records remain immutable provenance.

The canonical task-contract schema now has a deterministic validator at
`ops/scripts/validate_task_contract.py`, a checked-in example under
`ops/schemas/examples/`, and a focused two-case unit test. Hosted control-plane
CI runs that validator alongside the existing skill, agent, workflow, and
bootstrap checks.

# Expected Changed Components

The architecture reconciliation PR should remain mostly within:

- `documentation/OPERATING-WORKFLOW.md`;
- selected proposed architecture docs named above;
- `AGENTS.md` / `agents/AGENTS.md` only if responsibility semantics are currently contradictory;
- #19 project-bootstrap packaging surface if not already corrected before activation;
- minimal metadata/comments needed to mark legacy workflow status clearly.

Do not perform broad folder renames or mass deletions in this PR.

# Validation Plan

Run at minimum:

- all skill interface/frontmatter validation affected by changed skill metadata;
- project-bootstrap focused tests if packaging changes;
- maintenance tests;
- workflow-factory / workflow-organizer tests while those validators remain tracked;
- workflow validation on retained canonical workflow surfaces;
- agent/config validators for any changed agent references;
- Git allowlist / canonical-layout validation;
- `git diff --check`;
- hosted control-plane CI.

Also perform qualitative validation:

- every retained abstraction has a named consumer/responsibility;
- architecture docs do not disagree on packaging rules;
- no new CHG/audit/proof-only artifact appears;
- no new workflow/agent exists by symmetry;
- diff is small enough for a reviewer to understand without reading unrelated cleanup.

# Acceptance Mapping

| Issue #22 AC | PLAN evidence |
| --- | --- |
| AC-01 | canonical responsibility matrix in updated operating docs |
| AC-02 | #19 project-bootstrap procedure/tool locality decision |
| AC-03 | complete 14-skill disposition matrix |
| AC-04 | workflow consumer/state/gate inventory |
| AC-05 | reconciled operating/system-change/Goal-Plan/research semantics |
| AC-06 | diff review confirms no symmetry-created components |
| AC-07 | one focused architecture PR; broad cleanup stays #13/#21 |
| AC-08 | deterministic validators/tests/CI |
| AC-09 | #13 updated with executable cleanup groups |
| AC-10 | #21 updated with resulting physical cleanup consequences |

# Failure Modes

- PR #20 packaging is still moving: stop architecture branch work and resolve #19 first.
- A workflow has a real machine consumer not visible from docs: preserve it and document the consumer before changing semantics.
- A thin-looking skill owns a real permission/safety boundary: generalize/keep it rather than merging it for aesthetics.
- A proposed rename causes large cross-reference churn: record the target disposition and defer physical rename to #13.
- Architecture docs can be reconciled without changing runtime files: prefer the smaller diff.
- Validation relies on legacy machinery marked for later retirement: keep validation green now and hand explicit removal work to #13/#21 rather than breaking the architecture PR.

# Review Focus

1. Is the architecture describing the system that actually executed #19 rather than the system imagined before #19?
2. Does every retained abstraction have a distinct consumer, authority, or lifecycle?
3. Are skill descriptions discriminative enough for discovery without persona coupling?
4. Are deterministic scripts colocated with their actual capability owner?
5. Are machine workflows retained only for real state/gate/runtime value?
6. Did the PR make #13/#21 easier to execute rather than create another governance layer?
7. Could any new/changed file be removed without losing a distinct responsibility?

# Stop / Escalation Conditions

Stop and return to the maintainer rather than widening scope when:

- resolving a skill requires changing canonical agent roles;
- workflow removal would require unproven runtime behavior changes;
- the PR grows into broad physical cleanup;
- a decision depends on #8 model-routing or #12 portability evidence not yet available;
- #19 packaging remains unaccepted;
- a proposed simplification would remove a validated safety/permission guarantee without replacement.

# Definition of Done

The architecture-reconciliation slice is complete when:

- one canonical responsibility model explains current operation;
- #19 has the correct skill/tool boundary;
- all existing skills/workflows have confirmed dispositions;
- semantic docs no longer imply contradictory workflow/package architectures;
- deterministic validation remains green;
- #13 and #21 are execution-ready with bounded follow-up scopes;
- no broad cleanup or replacement framework was smuggled into the architecture PR.

## Superseding execution note

The architecture slice was completed on `main` at `b5155da`. The subsequent
bounded #13/#21 rationalization branch applies the disposition matrix: generic
handoff/link skills are tracked, duplicate wrapper skills and proposal-only
workflow families are removed, and the retained canonical workflow validators
remain green. This plan remains the semantic record; the cleanup plan owns the
physical changes.
