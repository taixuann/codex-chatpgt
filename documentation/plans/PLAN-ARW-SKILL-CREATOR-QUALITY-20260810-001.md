---
id: PLAN-ARW-SKILL-CREATOR-QUALITY-20260810-001
issue: 38
status: ready
scope: skill-creator-quality-system
updated: 2026-08-10
---

# Plan — Production-grade skill-creator quality system

## Objective

Bootstrap one strong `skill-creator` baseline, then harden it into the control plane's canonical admission/update procedure for future skills.

The plan must remain smaller than a bespoke evaluation platform. Reuse maintained creator/eval/security tooling when it earns the role, preserve provenance, and prove behavior in real Codex/OpenCode harnesses before claiming readiness.

## Authority and issue relationships

- Issue #38 owns this implementation and its acceptance criteria.
- Issue #14 owns external skill/tool provenance and qualification evidence.
- Issue #35 consumes the hardened creator during system-skill/workflow rationalization.
- Issue #8 owns production executor/model/session routing.
- Issues #5/#6 own ordinary execution-validation and independent acceptance semantics.
- Issue #12 owns later packaging/portability architecture.

Do not move those authorities into the creator.

## Non-negotiable design rules

1. `skill-creator` may return `DO NOT CREATE A SKILL`.
2. Search/reuse/adaptation precedes local authoring.
3. One visible creator may compose deterministic tools and external evaluators without exposing them as more active skills.
4. Utility evidence and safety evidence stay separate.
5. `NOT_ASSESSED` is not `PASS`.
6. Trigger quality must consider the active catalog, not only isolated examples.
7. Material skill claims should measure lift over a no-skill baseline when practical.
8. Portability is claimed only after runtime proof.
9. Failures that matter become durable regression cases.
10. Prefer simpler instructions/resources when measured behavior is equal or better.

## Phase A — Resolve upstream baseline and legal/provenance path

### A1. Inspect the installed OpenAI/Codex creator

Record:
- actual installed source/path/version if observable;
- procedure and bundled resources;
- trigger/authoring/eval behavior;
- what is system-owned and should not be duplicated locally.

### A2. Inspect Anthropic skill-creator at the real artifact level

Read the current upstream `SKILL.md`, scripts, agents/references/evals resources and exact commit/ref.

Record at minimum:
- intent/interview workflow;
- progressive-disclosure guidance;
- eval creation and grading;
- quantitative benchmark aggregation;
- blind comparison;
- trigger-description optimization;
- packaging behavior;
- host-specific assumptions.

### A3. Verify reuse terms before copying

Determine the exact license/redistribution situation for the chosen source tree/path.

Preferred bootstrap order:

```text
installed maintained capability
-> pinned upstream/install/reference mechanism
-> adapted/re-authored local implementation with explicit provenance
```

Do not create an untracked verbatim fork simply because `cp -r` is easy.

### A4. Produce baseline disposition

Choose one:

```text
USE_INSTALLED_OPENAI_CREATOR
ADAPT_ANTHROPIC_BASELINE
AUTHOR_LOCAL_COMPOSITE
DEFER
```

The decision must explain what unique control-plane behavior justifies any local layer.

## Phase B — Define the creator contract before implementation

### B1. Necessity gate

For every requested capability, resolve:

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

Evidence should include overlap with installed/local/external capabilities and expected reuse frequency/stability.

### B2. Component classification

Before creating multiple visible skills, classify every proposed component:

```text
merge_into_parent
internal_procedure_or_reference
reusable_satellite_skill
shared_module_or_schema
deterministic_script_or_tool
external_dependency
```

Only independently reusable, discriminatively triggered capability should increase the catalog.

### B3. Skill contract fields

Each serious created/adapted skill must make these inspectable:
- trigger and negative boundary;
- stable inputs/context requirements;
- output contract;
- side effects and permissions;
- deterministic assets/dependencies;
- stop/retry/fallback/escalation conditions;
- validation expectations;
- portability claims;
- provenance for imported/adapted assets.

## Phase C — Bootstrap the creator

Use the disposition from Phase A.

If a local layer is justified, keep the first implementation deliberately small:

```text
skills/skill-creator/
├── SKILL.md
├── references/      # only detailed policy/schemas that need progressive disclosure
├── scripts/         # deterministic checks/helpers only where justified
├── evals/           # creator's own regression/dogfood suite
└── agents/openai.yaml if the runtime convention requires it
```

Do not copy every upstream asset automatically. Import/adapt only resources needed by the chosen contract and preserve attribution/provenance where required.

## Phase D — Static and package validation

Establish a deterministic first gate that can run cheaply before model calls.

Check at minimum:
- required frontmatter/spec shape;
- name/path consistency;
- broken or orphan resource references;
- absolute machine paths;
- stale hardcoded model/runtime assumptions;
- secrets/credential-like content;
- dangerous/destructive command patterns;
- unbounded network/external mutation assumptions;
- dependency declarations and pinning/provenance where material;
- SKILL.md size/progressive disclosure;
- duplicated instructions/resources;
- host-specific assumptions behind portability claims.

First reuse the repo's existing validators. Qualify external linter/package tooling through #14 before adding a dependency.

## Phase E — Security qualification

Do not build a custom security scanner unless existing maintained options fail qualification.

Evaluate candidates such as NVIDIA SkillSpector / SkillLens / Skill Forge / Skill Guard for the exact required slice.

Security evidence should cover the capability-proportional subset of:
- prompt injection / instruction override;
- data exfiltration / secret access;
- destructive or excessive agency;
- privilege/tool/permission misuse;
- supply-chain/unpinned dependency risk;
- memory poisoning where relevant;
- MCP/tool poisoning where relevant;
- trigger abuse / broad shadowing;
- unsafe output/command handling.

Record scanner/version/mode. Static-only and full semantic/dynamic scans must not be conflated.

## Phase F — Trigger and catalog-coexistence evaluation

### F1. Minimum case matrix

For each active release candidate include:

```text
positive_core
positive_oblique
adjacent_negative
sibling_conflict
```

Prompts must be realistic, not just repeat skill-name keywords.

### F2. Isolation vs co-loaded catalog

Where the runtime/tooling can observe activation:
- test skill alone;
- test with the active catalog;
- identify trigger theft/interference where present.

Use repeated runs when stochasticity makes one-shot results unreliable.

Candidate tools such as `skill-probe`, Tripwire or equivalent remain optional until qualified; Codex-specific observability limitations must be documented instead of papered over.

### F3. Description optimization

Description edits are accepted only when they improve held-out/negative/conflict behavior, not because the prose looks nicer.

Prefer train/held-out separation or equivalent anti-overfit discipline when automated optimization is used.

## Phase G — Behavioral utility evaluation

### G1. Real harness requirement

Run representative material skills through the actual canonical harness, not only a raw-model proxy.

Preferred initial targets:
- Codex canonical runtime;
- OpenCode as portability/secondary-executor proof where claimed.

### G2. With-skill vs without-skill

For at least one dogfood skill, run comparable cases:

```text
WITHOUT_SKILL
WITH_SKILL
```

Measure the useful observable subset of:
- acceptance/correctness pass rate;
- scope control/change-surface correctness;
- validation evidence;
- repeated reliability/pass@k if useful;
- tokens/reasoning tokens if observable;
- wall time;
- cost if observable.

Unknown telemetry stays unknown.

### G3. Net-value disposition

A technically correct skill may still become:

```text
ACTIVE_CORE
ON_DEMAND
ECONOMY_LANE_HELPER
REFERENCE_ONLY
REDUNDANT
REJECT
```

Near-zero utility lift plus meaningful context/cost overhead is evidence against active installation.

## Phase H — Portability proof

If a skill claims portable Agent Skills semantics:

1. prove Codex discovery/execution;
2. prove one OpenCode-compatible path;
3. record effective model/runtime/config;
4. classify:

```text
PORTABLE
PORTABLE_WITH_ADAPTER
CODEX_ONLY
NOT_PROVEN
```

Do not generalize from identical filesystem format alone.

## Phase I — Regression and evolution contract

### I1. Durable eval cases

Keep a small high-value suite near the skill or in the smallest canonical test location.

When a material failure is discovered:
- reproduce;
- encode it as an eval/regression case when stable;
- fix;
- rerun existing cases;
- accept only without material regression.

### I2. Skill simplification challenge

For bloated or repeatedly patched skills, compare current vs simplified candidate.

Prefer the simpler version if routing, outcome and safety are equal or better.

Repeated deterministic invariants should migrate from prose into tests/scripts when appropriate.

## Phase J — Creator release report

Produce one compact readiness artifact/report for the creator itself and for dogfood candidates.

Required evidence fields:

```text
necessity: PASS|FAIL|NOT_ASSESSED
provenance: ...
structure: ...
security: ...
trigger_isolated: ...
trigger_coloaded: ...
behavioral_utility: ...
baseline_delta: ...
efficiency: ...
portability: ...
regression: ...
independent_review: ...
verdict: ...
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

No aggregate 0-100 score may override a blocking missing/failing gate.

## Phase K — Dogfood on Issue #35

Before declaring #38 complete, use the hardened creator on at least one real legacy/current skill from #35.

Good candidates:
- `franky-guidance-manager` -> potential `instruction-maintenance`;
- `franky-maintenance` -> challenge catch-all decomposition;
- `install-project-link` -> challenge whether this should be a visible skill at all.

The dogfood run must demonstrate the necessity gate can produce a non-creation/merge/generalize result, not only author a shiny new skill.

Feed the evidence back to #35's disposition matrix.

## Tool qualification strategy

Do not install every evaluator discovered in research.

For each candidate backend, record:
- exact repository/ref/license;
- unique capability;
- runtime support actually needed;
- overlap with existing validators;
- external dependencies/credentials;
- side effects and trust boundary;
- observability quality;
- cost;
- disposition: `USE`, `OPTIONAL`, `REFERENCE`, `REJECT`, `DEFER`.

Likely comparison set:
- installed OpenAI/Codex skill-creator;
- Anthropic skill-creator;
- agent-skill-eval;
- skill-probe;
- SkillSpector;
- SkillLens;
- Tripwire / SkillCI / SkillKit / Skill Guard / Skill Forge only where they add unique evidence.

## Validation matrix

| Gate | Minimum proof |
|---|---|
| Upstream/provenance | exact source/ref + reuse method + license check |
| Necessity | at least one CREATE and one DO-NOT-CREATE style disposition case |
| Structure | deterministic validator output |
| Security | qualified scan or explicit NOT_ASSESSED with reason |
| Trigger positive | core + oblique cases |
| Trigger negative | adjacent + sibling conflict cases |
| Co-loaded | runtime/tool proof where observable |
| Behavioral | real Codex task outcome |
| Baseline | with-vs-without on at least one dogfood candidate |
| Efficiency | observable tokens/time/cost or `unobservable` |
| Portability | OpenCode proof for portable claim |
| Regression | rerunnable case set |
| Independence | review separate from creator's self-claim when consequential |

## Stop / fallback conditions

Stop or reduce scope when:
- installed OpenAI creator already satisfies the desired contract with only a tiny policy extension;
- external tooling requires more infrastructure than the evidence it adds;
- runtime cannot expose activation reliably and proxy evidence would be misleading;
- evaluation cost exceeds the skill's expected value;
- security tooling cannot be run safely in the available environment;
- copying upstream would create licensing/provenance ambiguity;
- the proposed creator starts becoming a general workflow/eval platform.

In these cases record the limitation and use the smallest reliable fallback.

## Implementation grouping

Do not do one giant PR.

Suggested sequence:

1. upstream/provenance audit + creator contract;
2. baseline creator bootstrap/adaptation;
3. deterministic structural checks;
4. targeted trigger/outcome eval integration;
5. optional security/backend qualification;
6. dogfood on one #35 skill;
7. final reconciliation and removal of superseded creator/factory behavior.

## Definition of done

Issue #38 is done only when one canonical creator is backed by real evidence that it can reject unnecessary skills, preserve/reuse strong upstream capability, author bounded skills, test routing among siblings, measure at least one real behavioral lift, keep safety separate from utility, avoid false portability claims, preserve regressions, and successfully drive one real #35 rationalization decision.