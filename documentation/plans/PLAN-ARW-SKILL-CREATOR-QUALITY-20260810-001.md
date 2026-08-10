---
id: PLAN-ARW-SKILL-CREATOR-QUALITY-20260810-001
issue: 38
status: ready-for-end-to-end-execution
scope: skill-creator-quality-system
updated: 2026-08-10
---

# Plan — Production-grade skill-creator quality system

## Objective

Bootstrap the smallest credible `skill-creator`, prove it against real Codex behavior, then dogfood it as the admission/update gate for #35.

Do not build a registry, marketplace, workflow engine, telemetry platform, or generic evaluation service.

## Authority

- #38 = skill creation/admission/update quality contract.
- #14 = external skill/tool provenance and qualification evidence.
- #35 = final local/system skill + workflow disposition matrix.
- #8 = production executor/model/session routing.
- #5/#6 = ordinary deterministic validation and independent review.
- #12 = later packaging/portable adapter architecture.

## Non-negotiable rules

1. Creator may return `DO NOT CREATE A SKILL`.
2. Reuse/adapt is checked before local authoring.
3. Validators/evaluators remain tools unless they independently earn skill status.
4. `NOT_ASSESSED != PASS`.
5. Utility and security are separate evidence axes.
6. Effective runtime discovery matters more than source-folder appearance.
7. Co-loaded routing matters more than isolated demos.
8. Material claims should compare `WITH_SKILL` vs `WITHOUT_SKILL` when practical.
9. Portable claims require actual Codex + OpenCode evidence.
10. Previously passing skills are re-checkable after material model/runtime/catalog changes.
11. Creator must support on-demand, deprecate/replace, simplify and retire outcomes.
12. Prefer the smaller implementation when measured behavior is equal or better.

# Phase A — Baseline + provenance

## A1. Audit actual installed Codex creator

Record:
- source/path/version if observable;
- full procedure/resources;
- current authoring/eval behavior;
- system-owned behavior that should not be duplicated.

## A2. Audit Anthropic creator

Inspect real `SKILL.md` and relevant scripts/references/evals at an exact ref.

Record:
- intent capture/interview;
- progressive disclosure;
- eval generation/grading;
- baseline/A-B or blind comparison behavior;
- description/trigger optimization;
- packaging/runtime assumptions.

## A3. Verify reuse path

Resolve license/provenance before copying.

Preferred order:

```text
USE_INSTALLED_OPENAI_CREATOR
→ ADAPT_PINNED_UPSTREAM
→ AUTHOR_MINIMAL_LOCAL_COMPOSITE
→ DEFER
```

Do not create an untracked verbatim fork.

## A4. Baseline decision

Write one explicit disposition with rationale and exact source/ref.

# Phase B — Define creator contract

Before implementation, creator must support these decisions:

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

For a proposed component, classify:

```text
merge_into_parent
internal_procedure_or_reference
reusable_satellite_skill
shared_module_or_schema
deterministic_script_or_tool
external_dependency
```

Only an independently reusable and discriminatively triggered capability increases active skill count.

Each serious skill must expose:
- trigger + negative boundary;
- inputs/context;
- output contract;
- side effects/permissions;
- dependencies/resources;
- stop/retry/fallback/escalation;
- validation expectations;
- provenance;
- portability claim/status.

# Phase C — Bootstrap minimal creator

Use the Phase A disposition.

If a local layer is needed, default shape:

```text
skills/skill-creator/
├── SKILL.md
├── references/   # only progressive-disclosure policy/detail actually needed
├── scripts/      # deterministic helpers only
├── evals/        # small durable regression/dogfood set
└── agents/openai.yaml  # only if runtime convention requires it
```

Do not copy all upstream assets by default.

# Phase D — Cheap deterministic validation first

Check before model-based evals:
- frontmatter/spec/name/path consistency;
- broken/orphan resource references;
- absolute local paths;
- stale hardcoded model/runtime assumptions;
- secrets/credential-like content;
- dangerous/destructive commands;
- unbounded external mutation/network assumptions;
- dependency declarations/provenance;
- progressive-disclosure quality;
- duplicated instructions/resources;
- host-specific assumptions behind portability claims.

Reuse existing repo validators first. Qualify external lint/security tooling through #14 before adding dependencies.

# Phase E — Runtime discovery + collision audit

This is mandatory before trigger certification.

## Codex

Inspect actual effective discovery/config:
- active skill sources;
- duplicate names/sources;
- implicit vs explicit invocation policy;
- whether a skill is disabled from implicit discovery;
- catalog pressure / omitted or shortened descriptions if observable;
- current runtime/model configuration relevant to tests.

Treat active discovery as a constrained resource. Do not make every qualified skill implicitly active.

## OpenCode

Inspect actual effective discovery/config:
- path-derived skill ID;
- global/project/compatibility/config sources;
- precedence/shadowing;
- autoinvoke visibility;
- selected agent skill permissions;
- project root / working-directory assumptions.

A shared `SKILL.md` is not automatically a shared effective capability.

# Phase F — Trigger/co-loaded evaluation

Minimum release-candidate cases:

```text
positive_core
positive_oblique
adjacent_negative
sibling_conflict
```

Test:

```text
ISOLATED
vs
CO_LOADED_ACTIVE_CATALOG
```

where observability permits.

Use repeated runs when stochasticity makes one-shot results misleading. Candidate backends such as `skill-probe` remain optional until #14 qualification demonstrates net value.

Description optimization must improve held-out/negative/conflict behavior, not merely wording aesthetics.

# Phase G — Behavioral utility

Run representative tasks through the real canonical harness.

For at least one dogfood skill:

```text
WITHOUT_SKILL
vs
WITH_SKILL
```

Measure the useful observable subset:
- acceptance/correctness;
- scope control/change-surface correctness;
- validation evidence;
- repeated reliability/pass@k where useful;
- tokens/reasoning tokens if available;
- wall time;
- cost if available.

Possible disposition:

```text
ACTIVE_CORE
ON_DEMAND
ECONOMY_LANE_HELPER
RUNTIME_SPECIFIC
REFERENCE_ONLY
REDUNDANT
REJECT
DEFER
```

Near-zero lift plus meaningful routing/context overhead is evidence against active installation.

# Phase H — Safety / dependency evidence

Do not build a custom scanner unless needed.

Qualify the smallest useful backend slice from candidates such as SkillSpector/SkillLens or equivalent.

Assess proportionally:
- prompt/instruction override;
- exfiltration/secret access;
- excessive/destructive agency;
- tool/permission misuse;
- supply-chain/unpinned dependencies;
- unsafe output/command handling;
- memory/MCP poisoning only where relevant;
- trigger abuse / broad shadowing.

Record scanner/ref/version/mode. Static-only and semantic/dynamic evidence remain distinct.

# Phase I — Portability proof

For skills claiming portability:
1. prove Codex discovery/execution;
2. prove one OpenCode-compatible path;
3. record effective model/runtime/config + relevant catalog state;
4. classify:

```text
PORTABLE
PORTABLE_WITH_ADAPTER
CODEX_ONLY
RUNTIME_SPECIFIC
NOT_PROVEN
```

# Phase J — Freshness + lifecycle

A byte-identical skill can regress or become redundant after model/runtime/catalog changes.

For material release evidence, retain compact tested-against metadata where observable:
- skill source/ref/digest;
- harness/runtime version;
- effective model/model tier;
- reasoning setting where material;
- relevant active catalog/config state.

Re-run high-value trigger/outcome regressions after material changes. Do not build a registry solely for freshness.

Lifecycle outcomes must include:

```text
ACTIVE_CORE
ON_DEMAND
RUNTIME_SPECIFIC
DEPRECATED_BY:<replacement>
REFERENCE_ONLY
REDUNDANT
REJECT
DEFER
```

When deprecating, name replacement/migration when one exists and remove overlapping implicit discovery after migration rather than leaving both live forever.

# Phase K — Regression + simplification

Keep a small durable eval suite.

When a material failure appears:

```text
reproduce
→ add stable regression case
→ fix
→ rerun relevant suite
→ accept only without material regression
```

For bloated skills, compare current vs simplified candidate. Prefer simpler if routing/outcome/safety are equal or better.

# Phase L — Release report

Minimum evidence fields:

```text
necessity:
provenance:
structure:
security:
runtime_discovery:
trigger_isolated:
trigger_coloaded:
behavioral_utility:
baseline_delta:
efficiency:
portability:
freshness_tested_against:
regression:
lifecycle_disposition:
independent_review:
verdict:
```

Evidence levels:

```text
NOT_ASSESSED
STATIC_PASS
SMOKE_PASS
BEHAVIORAL_PASS
CROSS_RUNTIME_PASS
RELEASE_READY
```

No aggregate score overrides a blocking failure/missing gate.

# Phase M — Dogfood #35

Before #38 completes, evaluate at least one real legacy/current skill from #35.

Preferred candidates:
- `franky-guidance-manager` → challenge/generalize toward instruction maintenance;
- `franky-maintenance` → challenge catch-all decomposition;
- `install-project-link` → challenge whether it should remain a visible skill.

Dogfood must demonstrate at least one non-creation result such as merge/generalize/policy/script/reuse/retire.

Feed resulting disposition evidence directly to #35.

# Tool qualification strategy

Do not install every discovered evaluator.

For each backend record:
- exact repo/ref/license;
- unique evidence it adds;
- supported harnesses;
- overlap with existing validators;
- dependencies/credentials;
- side effects/trust boundary;
- observability quality;
- cost/latency;
- disposition `USE | OPTIONAL | REFERENCE | REJECT | DEFER`.

Initial comparison set may include:
- installed Codex/OpenAI creator;
- Anthropic creator;
- `agent-skill-eval`;
- `skill-probe`;
- SkillSpector;
- SkillLens;
- other lint/eval tools only if they add a unique missing gate.

# Validation matrix

| Gate | Minimum proof |
|---|---|
| Upstream/provenance | exact source/ref + reuse method + license check |
| Necessity | at least one CREATE-style and one DO-NOT-CREATE-style case |
| Structure | deterministic validator output |
| Runtime discovery | actual effective Codex config; OpenCode when portability claimed |
| Security | qualified scan or explicit NOT_ASSESSED |
| Trigger positive | core + oblique |
| Trigger negative | adjacent + sibling conflict |
| Co-loaded | runtime/tool proof where observable |
| Behavioral | real Codex task outcome |
| Baseline | with-vs-without for at least one dogfood candidate |
| Efficiency | measured or explicitly unobservable |
| Portability | OpenCode proof for portable claim |
| Freshness | tested-against runtime/model/catalog context recorded |
| Regression | rerunnable case set |
| Lifecycle | active/on-demand/deprecate/retire disposition supported |
| Independence | separate review when consequential |

# Stop / fallback conditions

Stop or reduce scope when:
- installed creator already satisfies the contract with a small extension;
- external tooling costs more than the evidence it adds;
- activation is not observable enough for the proposed claim;
- evaluation cost exceeds expected skill value;
- security tooling cannot run safely;
- copying upstream creates licensing/provenance ambiguity;
- the creator starts turning into a registry, marketplace, workflow engine, telemetry platform, or general eval service.

Use the smallest reliable fallback and record the limitation.

# Execution grouping

Recommended order:

1. Phase A provenance/baseline audit.
2. Phase B contract + Phase C minimal bootstrap.
3. Phase D deterministic validation.
4. Phase E runtime discovery/collision audit.
5. Phase F/G trigger + behavioral evidence.
6. Phase H only the smallest useful security backend.
7. Phase I/J portability + freshness/lifecycle semantics where claimed.
8. Phase K regression/simplification.
9. Phase L release report.
10. Phase M dogfood #35.
11. Remove superseded creator/factory behavior only after replacement evidence exists.

Do not do a giant mass-refactor PR.

# Definition of done

#38 is done only when one canonical creator can reject unnecessary skills, preserve/reuse strong upstream capability, author bounded skills, validate effective runtime discovery, test routing among siblings, measure at least one real behavioral lift, keep safety separate from utility, avoid false portability claims, retain rerunnable freshness/regression evidence, support deprecation/retirement, and successfully drive one real #35 rationalization decision.