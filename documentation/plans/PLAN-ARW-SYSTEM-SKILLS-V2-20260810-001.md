---
id: PLAN-ARW-SYSTEM-SKILLS-V2-20260810-001
issue: 35
status: ready-for-audit
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
- current Agent Skills ecosystems provide stronger patterns for progressive disclosure, engineering discipline, and behavioral skill testing.

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

Prefer current built-in/maintained `skill-creator` for authoring.

Qualification must decide whether to add any external tool for:

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

For every changed or newly admitted active skill:

## E1 activation scenarios

Create a compact test set:

- 2-4 positive/direct prompts;
- 2-4 indirect/semantic positives;
- 2-4 adjacent negatives;
- at least one likely-conflict prompt when a neighbor exists.

Record whether the intended skill activates/gets selected in the actual runtime where observable.

## E2 outcome scenarios

Run at least one representative task and verify:

- expected bounded output;
- no forbidden side effect;
- stop/escalation behavior;
- deterministic helper result where applicable.

## E3 conflict analysis

At minimum compare descriptions pairwise for likely overlapping active skills.

A tool such as Tripwire/SkillGuard/SkillKit may be evaluated, but manual/small deterministic tests are acceptable until dependency value is proven.

## E4 portability check

For skills intended to be portable, prove standard structure and one OpenCode-compatible discovery/load path where practical.

Do not duplicate source files into independently editable Codex/OpenCode copies.

# Phase F — implement in small groups

Only after the disposition matrix is accepted.

Suggested groups:

1. **Stale-coupling fixes**
   - absolute paths;
   - obsolete authority/model defaults;
   - stale references.

2. **Control-plane generalization**
   - guidance -> instruction maintenance;
   - maintenance -> read-first audit;
   - agent installer -> runtime adapter management.

3. **Merge/narrow**
   - project-link helper integration;
   - session-closeout simplification;
   - scheduler on-demand boundary.

4. **Engineering discipline admission**
   - only candidates with positive benchmark/trigger evidence;
   - prefer installed/upstream source over local copy.

5. **Workflow retirement**
   - remove unconsumed Franky YAML and dead validators/references;
   - no replacement orchestration layer.

6. **Canonical reconciliation**
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
CREATE_LOCAL
POLICY_NOT_SKILL
SCRIPT_NOT_SKILL
DEFER
```

# Guardrails

- no mass `cp -r` from OSS skill catalogs;
- no agent-per-skill architecture;
- no workflow-per-procedure symmetry;
- no hardcoded model binding in portable skill semantics;
- no absolute local paths in canonical portable packages;
- no duplicate Codex/OpenCode editable copies;
- no auto-promotion from one successful test;
- no replacing deterministic checks with LLM prose;
- no generic self-reflection loop without criterion + stop condition;
- no large skill-testing dependency before measured value;
- no deletion solely because a component looks old.

# Evidence matrix required before final mutation

| Surface | Evidence required |
| --- | --- |
| Current skill | trigger, consumer, assets, overlap, legacy coupling, runtime evidence |
| Proposed skill | positive/negative triggers, unique procedure, candidate source, representative outcome |
| External candidate | exact repo/path/ref where practical, provenance/license, overlap, runtime fit, disposition |
| Workflow | consumer, state, gates, recovery, refs, reason workflow beats skill/script/PLAN |
| Retired component | reference search + replacement/absence justification + rollback |
| Generalized component | before/after trigger and authority boundary + validator results |
| Portable capability | no machine-specific path/model authority + compatible standard shape |

# Stop conditions

Stop or DEFER a change when:

- current runtime consumer cannot be identified confidently;
- external candidate has unclear provenance/licensing for reuse;
- trigger overlap cannot be resolved without broader redesign;
- a proposed local skill duplicates a maintained capability without measurable gain;
- workflow state/gates appear real but runtime evidence is unavailable;
- simplification would remove a meaningful permission, validation, rollback, or provenance boundary;
- a tooling dependency would exceed the complexity of the problem it solves.

# Definition of done

Issue #35 is complete when:

1. every current skill/workflow has an evidence-backed disposition;
2. the active local skill surface is capability-first rather than persona-first;
3. control-plane maintenance procedures are narrow and current;
4. engineering-discipline gaps are resolved through maintained reuse/adaptation/local creation only where justified;
5. skill activation and outcome quality have representative evidence;
6. legacy absolute paths/model/AI-Labs authority assumptions are gone or explicitly isolated;
7. every remaining machine workflow proves a real persisted-state consumer or the workflow tree is reduced accordingly;
8. Codex remains the primary orchestration/acceptance authority and OpenCode consumes portable skills only as a bounded executor path;
9. the resulting system is simpler to route correctly even if its optional capability library becomes richer.