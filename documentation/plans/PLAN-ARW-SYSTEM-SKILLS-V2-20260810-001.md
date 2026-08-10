---
id: PLAN-ARW-SYSTEM-SKILLS-V2-20260810-001
issue: 35
status: conditional-reconciled
scope: system-skills-and-workflow-reconciliation-v2
updated: 2026-08-10
---

# Objective

Reconcile the current `skills/` and `workflows/` surfaces against the accepted multi-harness control-plane architecture and current Agent Skills evidence.

The goal is not minimum file count. The goal is the smallest **active routing surface** that preserves distinct useful procedures, deterministic guarantees, permission boundaries, and evidence quality.

Target principles:

```text
CAPABILITY NEED
-> decide whether a reusable skill is warranted
-> prefer maintained existing capability when it fits
-> otherwise generalize/create the smallest local procedure
-> keep deterministic mechanics in scripts/tools
-> keep machine workflows only for real persisted lifecycle/state/gate consumers
```

# Governing distinctions

Do not collapse these concepts:

```text
AGENT
= isolated runtime/context/permission/independent-judgment boundary

SKILL
= reusable on-demand procedure or domain method

SCRIPT / TOOL
= deterministic operation

WORKFLOW
= persisted lifecycle/state/gates/recovery with a real consumer

POLICY / ISSUE / PLAN
= authority, routing, scope, one-off execution semantics
```

A system capability may be used by the parent directly or by a bounded worker. Skill existence does not imply subagent delegation.

# New evidence since #13

#13 completed a useful first cleanup under the architecture known on 2026-08-09. This PLAN is justified by new evidence rather than aesthetics:

- #8 now defines OpenCode as a bounded secondary executor with explicit session/directory/model/permission boundaries;
- #9 distinguishes AgentMemory historical experience from canonical/live state;
- Wiki routing established an external scientific-evidence capability rather than an autonomous scientific agent OS;
- portability now requires separating canonical semantics from harness adapters;
- current repository inspection still shows Franky/AI-Labs-era assumptions in retained skills and a large Franky workflow tree;
- current Agent Skills ecosystems provide stronger patterns for progressive disclosure, engineering discipline, and behavioral skill testing;
- #38 now owns the production-grade `skill-creator` quality system that must gate future local skill creation/adaptation.

# External evidence to qualify

Use #14 provenance rules. Read actual artifacts before adopting anything.

## Maintained / standard references

1. Agent Skills specification
   - focused `SKILL.md` package;
   - `name` + `description` as discovery surface;
   - progressive disclosure;
   - optional scripts/references/assets.

2. Current Codex/OpenAI plugin guidance and `openai/plugins`
   - focused user goal;
   - explicit trigger/boundary/output;
   - deterministic scripts only where useful;
   - package as plugin only when distribution earns it.

3. `github/awesome-copilot`
   Candidate procedures/patterns:
   - `acquire-codebase-knowledge`;
   - `refactor-plan`;
   - `harness-engineering`;
   - `agentic-eval`;
   - related instruction/documentation skills.

4. `microsoft/agent-skills`
   - use mainly as evidence for acceptance-scenario discipline and skill test harness structure rather than as a generic catalog to install.

## OSS comparison set

Do not install wholesale.

- `raddue/crucible`
  - useful: measured A/B skill evals, iterative quality gates, stagnation detection, disk-mediated context patterns;
  - reject as architecture dependency: too much orchestration for this control plane.

- `adityaarakeri/senior-agent-skills`
  - useful: intentionally small non-overlapping set (`repo-recon`, `plan-first`, `tdd-loop`, `debug-protocol`, `safe-refactor`, `self-review`, `verify-done`, `git-hygiene`);
  - lesson: a small discipline catalog may route better than a large generic skill zoo.

- `SteveVitali/agent-skills`
  - useful: deterministic-before-LLM, evidence-before-claims, fresh-context review, `agent-docs`, documentation freshness, durable state only where long horizon justifies it.

- `bharath31/tripwire`
  - useful: activation coverage, positive/negative prompt scenarios, whole-catalog description conflict detection, model drift checks;
  - limitation: Codex skill activation observation remains more heuristic than Claude-specific instrumentation.

- `zztimur/skill-forge`
  - useful: separate package-integrity evidence from agent-behavior quality, pressure tests, explicit Not-Assessed instead of fake pass.

- `sakhilchawla/skillkit`, `vaibhavtupe/skill-guard`
  - useful: static lint, hardcoded-path/security checks, trigger conflict, scenario tests, regression/benchmark ideas;
  - do not adopt before qualification.

# Target architecture hypothesis

Use two skill families conceptually. Do not necessarily create new nesting folders unless runtime discovery benefits from it.

```text
SYSTEM SKILLS
|
|-- CONTROL-PLANE PROCEDURES
|   `-- maintain/extend the harness itself
|
`-- ENGINEERING DISCIPLINE
    `-- portable execution-quality procedures used inside project work
```

The active core should remain small. On-demand capabilities may exist without being globally exposed if the runtime supports disabling/selective installation.

# Target formation map after #38

This section is a **capability target and formation order**, not approval to create every named skill.

Every item below must pass the #38 creator/admission gate and end in one of:

```text
USE_EXISTING
ADAPT_EXISTING
CREATE_SKILL
SCRIPT_NOT_SKILL
POLICY_NOT_SKILL
REFERENCE_NOT_SKILL
TOOL_NOT_SKILL
DEFER
```

The target names are semantic handles only until admission proves the final package boundary and name.

## Tier 0 — creator/admission gate first

### `skill-creator`

Owner: #38.

This must mature before broad system-skill refactoring because it governs:

- necessity / `DO NOT CREATE A SKILL`;
- upstream/local reuse search;
- trigger and sibling-conflict evidence;
- behavioral utility / with-vs-without baseline where material;
- security/dependency evidence;
- portability honesty;
- regression and simplification pressure.

Do not create the remaining target catalog first and validate it afterward.

## Tier 1 — control-plane core capability hypotheses

Expected capability set to resolve after #38:

1. `skill-creator`
   - canonical meta-procedure for skill creation/adaptation/evaluation;
   - remains one visible capability while evaluators/scanners stay tools/dependencies.

2. `capability-qualification`
   - qualify external skills/plugins/MCPs/adapters/OSS assets;
   - provenance, overlap, safety, trigger/runtime fit, disposition;
   - distinct from creator only if broader non-skill qualification remains a stable recurring procedure.

3. `control-plane-audit`
   - read-first audit of agents/skills/instructions/runtime adapters/workflows/stale refs;
   - no universal mutation authority.

4. `instruction-maintenance`
   - scoped `AGENTS.md`/instruction discovery, inheritance, precedence, locality and drift correction;
   - no architecture-history or model-routing ownership.

5. `runtime-adapter-management`
   - map canonical role/capability semantics to runtime-specific adapter/config/permission deployment;
   - Codex/OpenCode implementation details remain adapters/references, not canonical architecture.

6. `external-handoff`
   - bounded execution/handoff contract between Codex and OpenCode/another runtime/team;
   - non-executing and role-neutral.

7. `project-bootstrap`
   - adaptive project inspection/materialization with deterministic dry-run/apply and raw-data protection.

8. `session-closeout`
   - acceptance state, unresolved work, durable pointers, next action, bounded evolution observation;
   - legacy Trekker/CHG/goal-package paths do not remain core unless independently consumed.

Target expectation: approximately **6-8 active local/core procedures**, not a mandatory count. If two hypotheses collapse cleanly without losing trigger/permission/validation boundaries, prefer the smaller catalog.

## Tier 2 — engineering-discipline capability hypotheses

These are capability gaps to resolve, not a mandate for local authoring. Prefer maintained external skills when they outperform ordinary model behavior and fit the control plane.

1. `repo-recon`
   - lightweight repository orientation before mutation;
   - should complement #2, not generate broad documentation by default.

2. `change-surface`
   - map likely affected code/tests/config/docs/generated/consumer surfaces and support #5 closure.

3. `systematic-debugging`
   - reproduce -> localize/minimize -> hypothesis -> instrument -> fix -> regression evidence.

4. `verification-before-completion`
   - fresh evidence before completion claims;
   - may resolve to #5 policy instead of an installed skill if measured lift is negligible.

5. `safe-refactor`
   - behavior-preserving, small-step refactoring with tests between changes;
   - not architecture redesign.

6. `self-review`
   - author-side pre-PR/diff review;
   - cannot replace #6 independent review when judgment independence matters.

7. `docs-drift`
   - code/docs/instruction freshness and scoped correction;
   - may merge into `instruction-maintenance` or remain a separate engineering skill only if trigger/use cases are sufficiently distinct.

Target expectation: resolve all seven capability families, but admit only the smallest set with measurable routing/outcome value. A realistic result may be **3-5 active or installed engineering-discipline skills**, with the rest represented by policy, tools or on-demand external capabilities.

## Tier 3 — on-demand specialist hypotheses

These should not occupy global discovery surface unless actual usage earns it.

1. `scheduler-management`
   - recurrence/timezone/collision/approval/rollback semantics.

2. `harness-migration`
   - cross-harness inventory, compatibility, collision and migration;
   - gated by #12 and current OpenCode portability evidence.

Target expectation: installed/available on demand, disabled or absent from ordinary discovery where possible.

## External/system-installed capabilities

Do not locally clone capabilities already owned well by maintained plugins/skills.

Current examples to preserve/qualify:

```text
GitHub specialist capabilities
- gh-address-comments
- gh-fix-ci
- yeet/publish workflow

External engineering candidates
- acquire-codebase-knowledge?  -> qualify against repo-recon need
- refactor-plan?               -> qualify against planning/refactor boundary
- agentic-eval?                -> on-demand only if eval value is material

Skill quality tooling
- upstream/installed skill-creator baseline
- agent-skill-eval? / skill-probe? / SkillSpector? / equivalent
  -> tools or optional dependencies, not visible skills by default
```

`?` means candidate, not pre-approved installation.

## Expected steady-state discovery surface

Do not optimize for a precise number, but use this as a routing-pressure sanity check:

```text
local/core active procedures        ~6-8
active engineering disciplines      ~3-5
on-demand specialists               ~0-2 in normal discovery
maintained plugin/runtime skills     separate, no local duplicate
```

Therefore the ordinary active discovery surface should likely remain around **8-12 high-signal capabilities**, even if more optional capabilities are available outside the default path.

If the active catalog grows materially beyond this, require evidence that trigger precision and co-loaded routing remain healthy.

# Formation sequence

Execute the skill system in this order:

```text
#38 harden skill-creator
        |
        v
admit/refactor Tier 1 core procedures
        |
        v
qualify Tier 2 OSS engineering disciplines
        |
        v
resolve Tier 3 on-demand specialists
        |
        v
retire/merge legacy Franky skills + workflows
        |
        v
co-loaded routing + outcome regression
        |
        v
reconcile CURRENT / DECISIONS / roadmap
```

Do not mass-create target names before #38 proves the gate.

# Phase A — current-surface inventory and legacy-coupling audit

Inventory every current skill and every `workflows/franky/**` YAML.

For each skill record:

- current name/path;
- trigger/description;
- procedure and output;
- current consumers;
- scripts/references/assets;
- mutation/permission boundary;
- legacy persona/runtime/model/path coupling;
- overlap with another local/system/external capability;
- actual runtime-use evidence;
- candidate disposition.

Explicitly check for:

- absolute machine paths;
- stale model names/defaults;
- AI-Labs/old registry authority assumptions;
- Franky persona coupling where the procedure is role-neutral;
- CHG/Trekker/goal-package assumptions on ordinary paths;
- broad descriptions that collide with neighboring skills;
- bundled resources referenced by stale paths;
- skills whose deterministic scripts are useful even if the model-visible skill is not.

For workflows, additionally record:

- named runtime consumer;
- persisted state;
- transition/gate/recovery semantics;
- CI/runtime references;
- whether Issue/PLAN + skill/script already covers the behavior.

Do not mutate during this phase except for an independently urgent broken reference if separately approved.

# Phase B — define control-plane procedure dispositions

Resolve these hypotheses with evidence.

## B1 — `instruction-maintenance`

Source hypothesis: generalize `franky-guidance-manager`.

Retain:

- instruction-chain discovery;
- scope/precedence/locality reasoning;
- minimal durable edits;
- guidance validation.

Remove/isolate:

- persona naming;
- architecture-history ownership;
- unrelated runtime routing.

## B2 — `control-plane-audit`

Source hypothesis: extract read-first diagnostic value from `franky-maintenance`.

Must remain primarily diagnostic:

```text
inventory
-> deterministic checks
-> classify findings
-> impacted consumers
-> recommendation
```

Do not retain universal mutation authority. Mutation routes to the owning capability/Issue/PLAN.

## B3 — `capability-qualification`

Create/adapt only if it adds system-level value beyond maintained skill-package evaluators.

Scope may include:

- skill;
- plugin;
- MCP capability;
- runtime adapter;
- OSS agent asset.

Procedure:

```text
provenance
-> actual artifact inspection
-> trigger/contract
-> overlap
-> permission/safety
-> positive/negative tests
-> runtime proof
-> outcome quality
-> KEEP/USE/ADAPT/REJECT/DEFER
```

Use qualified external validators as deterministic/behavioral tools rather than reimplementing them.

## B4 — `external-handoff`

Likely KEEP with narrow correction of any stale bundled-runner claim.

Must remain role-neutral and non-executing.

## B5 — `runtime-adapter-management`

Source hypothesis: generalize `franky-agent-installer`.

Own:

- adapter schema;
- filename/identity consistency;
- scope/collision;
- permission/sandbox boundaries;
- dependency/runtime support;
- deployment path;
- rollback.

Do not own:

- canonical role architecture;
- model-routing policy;
- fixed model defaults;
- OpenCode/Codex-specific semantics except in progressive references/adapters.

## B6 — `project-bootstrap`

Likely KEEP.

Preserve model judgment + deterministic dry-run/apply split and raw-data protection.

## B7 — `session-closeout`

Source hypothesis: simplify `shared-session-closeout`.

Core should cover:

- status;
- acceptance evidence;
- unresolved work;
- durable pointer;
- next action;
- bounded evolution observation.

Optional legacy/integration paths must move behind references or retire if no consumer exists.

## B8 — `scheduler-management`

Generalize only the unique scheduler safety procedure from `franky-cron-installer`.

Prefer on-demand/disabled-by-default unless actual frequency justifies core exposure.

## B9 — `harness-migration`

Generalize from `franky-source-migration` only under #12 portability evidence.

Prefer DEFER/MOVE_ON_DEMAND now unless current OpenCode materialization requires a bounded migration slice.

# Phase C — engineering-discipline qualification

Do not create a local clone merely because the family is desirable.

For each family below, compare at least one maintained/high-quality existing skill against current control-plane semantics and a representative task.

## C1 — repo reconnaissance

Questions:

- Does #2 need a lightweight read-only orientation skill, a broad documentation generator, or no model-visible skill at all?
- `acquire-codebase-knowledge` is thorough but writes seven docs; do not use it for every orientation by accident.
- Benchmark a smaller `repo-recon` pattern for routine unfamiliar-repo mapping.

## C2 — change-surface / impact mapping

Target behavior:

```text
objective
-> likely affected surface
-> APIs/data/config/tests/docs/generated artifacts
-> hidden coupling
-> post-change closure comparison
```

Must reinforce #5; do not create another planning authority.

## C3 — systematic debugging

Compare procedures around:

```text
reproduce
-> localize/minimize
-> one hypothesis at a time
-> instrument
-> fix
-> regression evidence
```

Prefer portable external skill if trigger and behavior fit.

## C4 — verification-before-completion

Resolve whether this should be:

- external engineering-discipline skill;
- small parent policy;
- #5 validation procedure only.

Avoid duplicating deterministic validators. Its value, if retained, is behavioral: do not claim success without fresh evidence.

## C5 — safe refactor

Qualify only for behavior-preserving refactor work. Keep separate from architecture redesign and migration planning.

## C6 — self-review

Distinguish:

```text
AUTHOR SELF-REVIEW
!=
INDEPENDENT REVIEW #6
```

A self-review skill may be useful before PR/acceptance; it cannot replace Athena/fresh-context review when independence matters.

## C7 — instruction/docs freshness

Compare:

- GitHub `harness-engineering`;
- SteveVitali `agent-docs` / `refresh-repo-docs` patterns.

Prefer narrow deterministic drift detectors plus scoped correction over periodic giant doc rewrites.

## C8 — skill authoring/evaluation

Resolved primarily by #38.

Prefer current built-in/maintained `skill-creator` baseline plus only the smallest qualified tooling needed for:

- static package lint;
- activation positive/negative scenarios;
- cross-skill description conflict;
- outcome eval;
- periodic model-drift checks.

No external testing framework becomes a dependency solely because it has many features.

# Phase D — workflow consumer proof

For each YAML under `workflows/franky/**`, answer:

```text
Who consumes this?
What state survives between steps/runs?
What gate is actually enforced?
What recovery/resume behavior exists?
Why is Issue/PLAN + skill/script insufficient?
Where is runtime/CI evidence of use?
```

Disposition:

```text
KEEP
GENERALIZE
MERGE
RETIRE
DEFER
```

Strong default: if no consumer/state/gate/recovery proof exists, RETIRE the machine workflow without creating a replacement.

Valid final shape may be only:

```text
workflows/
`-- AGENTS.md
```

Keep workflow validators only if a retained workflow or another independent consumer actually uses them.

# Phase E — trigger and outcome quality proof

Do not judge skill quality from prose alone.

For every changed or newly admitted active skill, use #38's quality contract proportionally.

## E1 activation scenarios

Create a compact test set:

- positive/direct prompts;
- indirect/semantic positives;
- adjacent negatives;
- at least one likely-conflict prompt when a neighbor exists.

Record whether the intended skill activates/gets selected in the actual runtime where observable.

## E2 co-loaded routing

For the final active catalog, test representative conflict-prone skills together rather than certifying each one only in isolation.

If co-loaded testing reveals trigger theft/interference, prefer narrowing/merging/removing skills over endlessly broadening descriptions.

## E3 outcome scenarios

Run representative tasks and verify:

- expected bounded output;
- no forbidden side effect;
- stop/escalation behavior;
- deterministic helper result where applicable;
- measurable lift over no-skill baseline for material/new engineering-discipline capabilities when practical.

## E4 portability check

For skills intended to be portable, prove standard structure and one OpenCode-compatible discovery/load path where practical.

Do not duplicate source files into independently editable Codex/OpenCode copies.

# Phase F — implement in small groups

Only after the disposition matrix is accepted and #38 has produced a usable admission gate.

Suggested groups:

1. **Stale-coupling fixes**
   - absolute paths;
   - obsolete authority/model defaults;
   - stale references.

2. **Control-plane generalization**
   - guidance -> instruction maintenance;
   - maintenance -> read-first audit;
   - agent installer -> runtime adapter management;
   - creator/admission integration from #38.

3. **Merge/narrow**
   - project-link helper integration;
   - session-closeout simplification;
   - scheduler on-demand boundary;
   - docs-drift vs instruction-maintenance boundary.

4. **Engineering discipline admission**
   - only candidates with positive trigger/outcome/baseline evidence;
   - prefer installed/upstream source over local copy;
   - keep catalog pressure visible.

5. **Workflow retirement**
   - remove unconsumed Franky YAML and dead validators/references;
   - no replacement orchestration layer.

6. **Catalog-level regression**
   - co-loaded routing checks on conflict-prone capabilities;
   - outcome regression on representative tasks.

7. **Canonical reconciliation**
   - CURRENT/DECISIONS/roadmap only for accepted long-lived outcomes.

Do not create one branch per skill by ritual. Group changes by coherent independently reviewable behavior.

# Disposition schema

Every current local skill/workflow:

```text
KEEP
GENERALIZE
MERGE
REPLACE_WITH_MAINTAINED
MOVE_ON_DEMAND
RETIRE
DEFER
```

Every proposed capability:

```text
USE_EXISTING
ADAPT_EXISTING
CREATE_SKILL
SCRIPT_NOT_SKILL
POLICY_NOT_SKILL
REFERENCE_NOT_SKILL
TOOL_NOT_SKILL
DEFER
```

# Guardrails

- #38 creator/admission gate before broad new skill authoring;
- no mass `cp -r` from OSS skill catalogs;
- no target-name-driven creation: a capability hypothesis may legitimately resolve to policy/tool/merge/reuse/defer;
- no agent-per-skill architecture;
- no workflow-per-procedure symmetry;
- no hardcoded model binding in portable skill semantics;
- no absolute local paths in canonical portable packages;
- no duplicate Codex/OpenCode editable copies;
- no auto-promotion from one successful test;
- no replacing deterministic checks with LLM prose;
- no generic self-reflection loop without criterion + stop condition;
- no large skill-testing dependency before measured value;
- no deletion solely because a component looks old;
- no active-catalog growth without considering co-loaded trigger interference.

# Evidence matrix required before final mutation

| Surface | Evidence required |
| --- | --- |
| Current skill | trigger, consumer, assets, overlap, legacy coupling, runtime evidence |
| Proposed skill | #38 necessity disposition, positive/negative/conflict triggers, unique procedure, candidate source, representative outcome |
| External candidate | exact repo/path/ref where practical, provenance/license, overlap, runtime fit, disposition |
| Engineering-discipline candidate | with/without-skill outcome evidence when material, routing fit, catalog conflict risk, cost/context overhead where observable |
| Workflow | consumer, state, gates, recovery, refs, reason workflow beats skill/script/PLAN |
| Retired component | reference search + replacement/absence justification + rollback |
| Generalized component | before/after trigger and authority boundary + validator results |
| Portable capability | no machine-specific path/model authority + Codex/OpenCode compatible proof where claimed |
| Final active catalog | representative co-loaded conflict/routing evidence |

# Stop conditions

Stop or DEFER a change when:

- #38 admission/creator gate is not yet usable for a proposed new skill;
- current runtime consumer cannot be identified confidently;
- external candidate has unclear provenance/licensing for reuse;
- trigger overlap cannot be resolved without broader redesign;
- a proposed local skill duplicates a maintained capability without measurable gain;
- a proposed skill adds negligible behavioral lift over current model/policy while increasing active routing surface;
- workflow state/gates appear real but runtime evidence is unavailable;
- simplification would remove a meaningful permission, validation, rollback, or provenance boundary;
- a tooling dependency would exceed the complexity of the problem it solves;
- active discovery size or co-loaded interference becomes worse without corresponding capability value.

# Definition of done

Issue #35 is complete when:

1. every current skill/workflow has an evidence-backed disposition;
2. #38's creator/admission quality gate has been used to govern new/adapted skill decisions;
3. the active local skill surface is capability-first rather than persona-first;
4. control-plane maintenance procedures are narrow and current;
5. all engineering-discipline capability gaps are explicitly resolved through reuse/adaptation/local creation/policy/tool/defer, with only evidence-backed skills admitted;
6. the ordinary active discovery surface remains small and high-signal, with representative co-loaded routing evidence;
7. legacy absolute paths/model/AI-Labs authority assumptions are gone or explicitly isolated;
8. every remaining machine workflow proves a real persisted-state consumer or the workflow tree is reduced accordingly;
9. Codex remains the primary orchestration/acceptance authority and OpenCode consumes portable skills only as a bounded executor path;
10. the resulting system is simpler to route correctly even if its optional capability library becomes richer.

## Execution report — 2026-08-10

This matrix is the current evidence-backed reconciliation after the #38
creator gate. It distinguishes the package disposition from whether a future
semantic replacement has earned a new runtime-visible name.

The current matrix rerun found 10 tracked package names with no omissions;
the additional `franky-workflow-organizer` row is an explicit retired-package
disposition. The repository has zero tracked workflow YAML files, and the
retirement block below contains 17 historical workflow paths. These counts are
structural evidence only; runtime activation and cross-runtime retirement stay
under their stated gates.

The deterministic interface validator now resolves the Git-tracked package
surface rather than scanning only `franky-*` directories; the current run
validates all 10 tracked packages and ignores personal/plugin overlays that are
outside the repository allowlist.

### Current local skill disposition

| Current package | Disposition | Semantic owner/result | Evidence and boundary |
| --- | --- | --- | --- |
| `external-handoff` | **KEEP** | `external-handoff` | Role-neutral bounded handoff; no control-plane persona coupling. |
| `franky-agent-installer` | **GENERALIZE** | `runtime-adapter-management` | Keep compatibility name for now; stale model/path assumptions were repaired; owns adapter schema, scope, collision, permission and rollback checks. |
| `franky-cron-installer` | **MOVE_ON_DEMAND** | `scheduler-management` | No active scheduler consumer; retain only as deferred/on-demand capability until usage earns discovery. |
| `franky-guidance-manager` | **GENERALIZE** | `instruction-maintenance` | Real Codex dogfood passed bounded read-only guidance review; compatibility name retained pending migration evidence. |
| `franky-maintenance` | **GENERALIZE** | `control-plane-audit` | Narrow diagnostic/audit owner; mutation remains Issue/PLAN/owning capability, not universal authority. |
| `franky-promotion` | **MOVE_ON_DEMAND / DEFER** | promotion under #12 | No current destination consumer; do not expose in ordinary discovery. |
| `franky-source-migration` | **MOVE_ON_DEMAND / DEFER** | `harness-migration` under #12 | Portability gate is not yet accepted; no local duplicate is created. |
| `franky-workflow-organizer` | **RETIRE** | workflow policy in `workflows/AGENTS.md` + Issue/PLAN | No retained machine workflow has a real persisted-state consumer; deterministic validators are not a reason to keep the model-visible package. |
| `install-project-link` | **MOVE_ON_DEMAND** | project-link safety primitive | Distinct safety boundary remains; not merged blindly into `project-bootstrap`, and not ordinary global discovery. |
| `project-bootstrap` | **KEEP** | `project-bootstrap` | #19 implementation and 9-test integration suite provide a real reusable contract. |
| `shared-session-closeout` | **GENERALIZE / KEEP** | `session-closeout` | Role-neutral acceptance/next-action/evolution observation; invalid metadata repaired. |

### Proposed capability admission matrix

| Capability hypothesis | #38 decision | Active result |
| --- | --- | --- |
| `skill-creator` | **USE_EXISTING** | Installed Codex/OpenAI creator; no local duplicate. |
| `capability-qualification` | **POLICY_NOT_SKILL** | #14 plan plus deterministic evidence tables; no separate package yet. |
| `control-plane-audit` | **ADAPT_EXISTING** | Generalize `franky-maintenance`. |
| `instruction-maintenance` | **ADAPT_EXISTING** | Generalize `franky-guidance-manager`; dogfood evidence. |
| `runtime-adapter-management` | **ADAPT_EXISTING** | Generalize `franky-agent-installer`. |
| `external-handoff` | **USE_EXISTING** | Existing role-neutral package. |
| `project-bootstrap` | **USE_EXISTING** | Existing validated package. |
| `session-closeout` | **ADAPT_EXISTING** | Generalize existing role-neutral package. |
| `scheduler-management` | **MOVE_ON_DEMAND / DEFER** | Existing cron package is not active core. |
| `harness-migration` | **DEFER** | #12 portability gate remains open. |

### Tier 2 engineering-discipline qualification

| Capability | Disposition | Rationale |
| --- | --- | --- |
| `repo-recon` | **POLICY_NOT_SKILL / REFERENCE_ONLY** | Parent orientation and #2 bounded context are sufficient; broad `acquire-codebase-knowledge` writes seven docs and adds context cost. |
| `change-surface` | **POLICY_NOT_SKILL** | Keep as #5 closure/impact-frontier procedure until a repeated reusable trigger is measured. |
| `systematic-debugging` | **REFERENCE_ONLY / DEFER** | Senior-agent artifact has unresolved redistribution terms; no local copy. |
| `verification-before-completion` | **POLICY_NOT_SKILL** | #5 validation plus final-critique policy already own the boundary. |
| `safe-refactor` | **REFERENCE_ONLY / DEFER** | External pattern inspected; no measured local gap or licensed runtime proof. |
| `self-review` | **REFERENCE_ONLY / DEFER** | SteveVitali MIT pattern is useful, but no Codex/OpenCode behavioral lift was observed; it cannot replace #6. |
| `docs-drift` | **POLICY_NOT_SKILL / ADAPT instruction-maintenance** | Scoped guidance and deterministic checks are sufficient until repeated use proves separation. |
| skill authoring/evaluation | **USE_EXISTING** | Installed creator and existing validators; external evaluators remain tools/references. |

### Tier 3 and workflow disposition

`scheduler-management` remains on-demand/deferred. `harness-migration` remains
deferred under #12. No Tier-3 capability is added to ordinary discovery.

The following 17 machine workflow YAMLs have no named runtime dispatcher,
persisted state store, recovery/resume implementation, or independent consumer
that beats Issue/PLAN plus a skill/script. They are therefore **RETIRE**:

```text
workflows/franky/franky.yaml
workflows/franky/lifecycle-contract.yaml
workflows/franky/franky-install/agent.yaml
workflows/franky/franky-install/cron.yaml
workflows/franky/franky-install/guidance.yaml
workflows/franky/franky-install/project-link.yaml
workflows/franky/franky-install/skill.yaml
workflows/franky/franky-install/workflow.yaml
workflows/franky/franky-maintenance/git-finalize.yaml
workflows/franky/franky-maintenance/inventory.yaml
workflows/franky/franky-maintenance/migrate-to-codex.yaml
workflows/franky/franky-maintenance/promotion.yaml
workflows/franky/franky-maintenance/update-agents.yaml
workflows/franky/franky-maintenance/update-cron.yaml
workflows/franky/franky-maintenance/update-guidance.yaml
workflows/franky/franky-maintenance/update-skills.yaml
workflows/franky/franky-maintenance/update-workflows.yaml
```

`workflows/AGENTS.md` remains as policy: a future YAML is admitted only when
its real consumer, state, gates, transitions and recovery are demonstrated.
The pending personal scheduler definition is not a workflow consumer; it is a
Tier-3 candidate and now uses the semantic `issue-plan-skill` route.

### Effective catalog and portability evidence

| Runtime | Observed catalog | Finding |
| --- | --- | --- |
| Codex `0.146.0` | Current root scan: 60 source files / 54 unique basenames; earlier runtime snapshot: 61 files / 49 unique names; fresh model-visible prompt-input snapshot: 86 entries / 58 unique names | Earlier runtime scan recorded ten duplicate-name groups and 2% description-budget shortening; current prompt-input snapshot records 13 duplicate-name groups. `--disable skill_search` leaves the initial catalog metadata present, while implicit activation remains `NOT_ASSESSED`. |
| OpenCode `1.18.15` | 89 effective skills / 89 unique IDs; 90 in the disposable shadow fixture | Path/config aliases and precedence observed. A synthetic project-local `shadow-demo` shadows the same configured-path ID, while a config-only fixture resolves the configured candidate; each effective catalog has one ID. Toggling both external-skill scan flags kept 89/89 IDs but changed the source root for 9 entries, confirming an overlay distinction without proving equivalence. Activation is `SMOKE_PASS`; permission enforcement and completed behavioral equivalence remain `NOT_ASSESSED`; semantic mapping is `PORTABLE_WITH_ADAPTER`, not equivalence. |

The OpenCode catalog also exposes external, non-`.codex` Franky overlay skills
named `franky-workflow-manager` and `franky-install-workflow`. Their metadata
describes YAML workflow execution/registration under external `ops/` paths.
The latest refresh resolved them from the `ai-labs/franky.workflow/` and
`ai-labs/franky.install/` overlay paths; direct aliases remain present but were
not the effective locations.
This means the repository-level retirement cannot be promoted to
cross-runtime retirement. The external overlay is recorded as an explicit
#12 portability/ownership boundary; no external control-plane files were
mutated in this issue.

### Conditional reconciliation

The current result is **CONDITIONAL_PASS**. The active surface is reduced by
retiring the unconsumed Franky workflow tree and its workflow-organizer
package, while preserving existing safety/provenance boundaries. Full #35
acceptance remains gated on the missing host-observable co-loaded routing and
cross-runtime behavior evidence rather than being inferred from static files.

The disposable shadow probe strengthens the catalog/precedence evidence:
OpenCode discovers configured skill paths and deterministically prefers a
project-local ID over a configured-path collision. It does not close the
remaining host-observable co-loaded activation or cross-runtime behavior gate.
