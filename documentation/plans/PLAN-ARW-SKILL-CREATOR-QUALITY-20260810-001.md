---
id: PLAN-ARW-SKILL-CREATOR-QUALITY-20260810-001
issue: 38
status: conditional-pass
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

## Execution report — 2026-08-10

This report records the end-to-end run against the installed runtimes. It is
deliberately evidence-level specific: unavailable host behavior remains
`NOT_ASSESSED` and is not promoted to a pass by static configuration.

### Phase A — provenance and baseline

| Source | Exact artifact/ref | License/provenance | Decision |
| --- | --- | --- | --- |
| Installed Codex/OpenAI creator | `/Users/tai/.codex/skills/.system/skill-creator`, Codex `0.146.0` | Local Apache-2.0 `license.txt`; `SKILL.md` SHA-256 `da44c88f6b3845a8fa8c60792ec9a722110a55a9793c279757b48fefb11f819c`; `quick_validate.py` `6cc9dc3199c935916cf6f73fcbbbb0e3bb1b58c8f5109fefa499978908164f51`; `init_skill.py` `f40cb8fafc34e2d5dbbb8b6b04297af128b70844b67bc9445ef69790e0cdb49` | **USE_EXISTING** |
| Anthropic creator | `anthropics/skills/skills/skill-creator` at `b0cbd3df1533b396d281a6886d5132f623393a9c` | Skill `LICENSE.txt` Apache-2.0; Claude Code/`claude -p` assumptions observed | **REFERENCE_ONLY** |
| OSS comparison set | `github/awesome-copilot` `3f0bba475ec40b9680e1d0311b9caffeec5ad4c3` (MIT); `SteveVitali/agent-skills` `6f6c5843148443d3d3c4fe034c03eda669754bfc` (MIT) | Real SKILL.md artifacts inspected; no local copies | **REFERENCE_ONLY / DEFER** |
| `adityaarakeri/senior-agent-skills` | `1a6c8523504f145db1ef917b123b7c052abca5ba` | Repository license metadata unresolved | **REFERENCE_ONLY / DEFER** |

No competing creator package was copied into this repository.

### Phases B–D — contract, bootstrap, and deterministic checks

The installed creator already provides the required authoring, progressive
disclosure, initialization, OpenAI metadata generation, and quick-validation
procedures. The local decision contract is therefore represented by this PLAN
and existing deterministic tools rather than another visible skill.

The creator decision set used for #35 is:

```text
USE_EXISTING | ADAPT_EXISTING | CREATE_SKILL | SCRIPT_NOT_SKILL
POLICY_NOT_SKILL | REFERENCE_NOT_SKILL | TOOL_NOT_SKILL | DEFER
```

Tracked control-plane skills: **10/10** pass the installed OpenAI
`quick_validate.py` after removing unsupported metadata from
`shared-session-closeout`. Existing interface/routing validators and four
focused Franky maintenance tests pass. Four ignored personal overlay packages
still fail the quick validator because of extra frontmatter; they are runtime
overlay findings only and were not silently promoted or edited.

The stale hard-coded model/path findings repaired in this run were limited to
the tracked installer, maintenance, project-link, and session-closeout
packages. No secrets, destructive commands, or external dependencies were
introduced.

### Phase E — effective runtime discovery

- Codex `0.146.0`, configured model `gpt-5.6-terra`, reasoning `medium`:
  the earlier 2026-08-10 root scan found 61 `SKILL.md` files, 49 unique
  names, and ten duplicate-name groups. A fresh read-only probe returned
  `PROBE_OK` and reported description shortening to fit the 2% skills-context
  budget. The current root scan is 60 files / 54 unique basenames after the
  retirement cleanup; hidden implicit-selection policy and adapter metadata
  remain **NOT_ASSESSED**.
- A fresh `codex debug prompt-input` snapshot on 2026-08-10 exposed the
  model-visible catalog as 86 entries, 58 unique public names, and 13
  duplicate-name groups across the configured skill roots. Repeating the
  snapshot with `--disable skill_search` produced the same initial catalog;
  the flag therefore does not by itself remove catalog metadata. The runtime
  baseline observation below is based on the absence of a skill-tool event,
  not on catalog removal.
- OpenCode `1.18.15`: 89 effective skills with 89 unique effective IDs.
  Path-derived/config aliases and precedence were observed, including
  `franky-install-guidance`, `franky-install-project-link`, and a native
  `config.opencode.skill-creator`; direct activation and selected-agent
  permission enforcement remain **NOT_ASSESSED**. The resolved default
  `build` agent is permissive, so no portability claim is made from that
  configuration alone.

A bounded OpenCode run in the same disposable synthetic fixture produced a
real `skill` tool load for `franky-install-guidance` and a read-only directory
inspection. The process ended before emitting its final audit response, and
the fixture hashes were unchanged; this upgrades OpenCode **activation smoke
evidence** to `SMOKE_PASS` but leaves behavioral utility and permission
enforcement **NOT_ASSESSED**.

After the #35 retirement was merged, a fresh Codex `0.146.0` read-only startup
probe returned `PROBE_OK`. It emitted only the previously observed stale model
cache schema and rollout-state fallback warnings; no missing
`franky-workflow-organizer` or malformed tracked-skill warning appeared.

### Phases F–G — trigger and behavioral evidence

The static routing fixture covers direct positive, adjacent negative,
nearest-neighbor, expected-none, and ambiguous cases; it passes with the
existing validator. A real read-only Codex run in a synthetic, non-sensitive
guidance fixture selected `franky-guidance-manager`, inspected the scoped
instruction chain, and returned a bounded review without writes. This is
`BEHAVIORAL_PASS` for the with-skill path.

An earlier natural-prompt attempt did not isolate a no-skill baseline. A fresh
read-only run on 2026-08-10 used `--ignore-user-config --disable
skill_search` against a disposable fixture without project skills and
completed with `CODEX_BASELINE_DONE`; its JSON trace contained only the
requested command execution and final message, with no skill-tool event. A
separate disposable fixture with a project-local skill produced a matching
with-skill activation trace, and a two-skill co-loaded run selected only the
matching sibling; the bounded results are recorded below. This proves a safe
runtime activation/negative slice, but not a material utility lift for the
real #35 skill. Real-skill baseline delta, broad catalog co-loading, and hidden
trigger selection therefore remain **NOT_ASSESSED**, not a claimed lift.

### Phase H — safety and dependencies

Static package and allowlist checks pass for tracked files. Dynamic prompt-
injection, supply-chain, and dependency scanner evidence was not available
without adding an unqualified backend, so those axes are **NOT_ASSESSED**.
No external package was installed and no credential-bearing operation was
performed.

### Phases I–J — portability, freshness, lifecycle

Codex execution is observed. OpenCode exposes an adapter/alias catalog and a
skill-load smoke trace but not the same Codex skill identity or completed
behavioral result; the honest classification is `PORTABLE_WITH_ADAPTER` for
the semantic procedure and `NOT_PROVEN` for cross-runtime behavioral
equivalence. The release was checked against Codex
`0.146.0`, OpenCode `1.18.15`, model `gpt-5.6-terra`, and catalog snapshots
from 2026-08-10. Lifecycle dispositions are recorded in the #35 matrix below;
no registry or telemetry store was created.

### Phases K–L — regression and release fields

The four focused maintenance tests, tracked-skill quick validation, static
routing checks, agent validation, and whitespace checks are rerunnable. The
minimal simplification was to use the installed creator and remove invalid
metadata rather than adding a creator framework. Release evidence is:

```yaml
necessity: CONDITIONAL_PASS
provenance: RELEASE_READY
structure: STATIC_PASS
security: NOT_ASSESSED
runtime_discovery: CONDITIONAL_PASS
trigger_isolated: STATIC_PASS
trigger_coloaded: BEHAVIORAL_PASS (bounded synthetic fixture; catalog-wide remains NOT_ASSESSED)
behavioral_utility: BEHAVIORAL_PASS
baseline_delta: NOT_ASSESSED (real #35 skill; synthetic path comparison only)
efficiency: NOT_ASSESSED
portability: PORTABLE_WITH_ADAPTER / NOT_PROVEN
freshness_tested_against: Codex-0.146.0; OpenCode-1.18.15; 2026-08-10 catalog
regression: STATIC_PASS
lifecycle_disposition: RELEASE_READY for bounded admission semantics
independent_review: CONDITIONAL_PASS
verdict: CONDITIONAL_PASS
```

### Phase M — #35 dogfood

`franky-guidance-manager` was dogfooded on the synthetic guidance fixture.
The result is **ADAPT_EXISTING / GENERALIZE** toward the semantic capability
`instruction-maintenance`, while retaining the compatibility name until a
future migration earns a cleaner runtime identity. The creator correctly
returned a non-creation outcome; no competing package was authored.

### Gate conclusion

The installed creator is the canonical admission baseline and is ready for
bounded #35 decisions. #38 remains **conditional** rather than fully accepted
because real-skill baseline delta, broad catalog co-loaded behavior, dynamic
security, and direct OpenCode execution evidence are unavailable. The
synthetic fixture supplies bounded activation, sibling-selection, and negative
runtime evidence only. These limitations are recorded explicitly and do not
justify a registry, marketplace, telemetry, workflow engine, or general
evaluation platform.

### Supplemental runtime audit — 2026-08-10

- Codex `0.146.0` baseline path: `codex exec --ignore-user-config
  --disable skill_search --ephemeral --json -s read-only` against
  `/tmp/skill-dogfood-fixture` returned `CODEX_BASELINE_DONE`. The trace showed
  the fixture guidance being read by a shell command and no skill-tool event;
  no files were written.
- A matching with-skill rerun was not performed because the host would expose
  private skill/config content to the provider without a separate data-export
  approval. Existing prior with-skill evidence remains unchanged; this audit
  does not upgrade `baseline_delta` or co-loaded activation.
- A fresh installed-creator rerun on 2026-08-10 invoked
  `skills/.system/skill-creator/scripts/quick_validate.py` for every tracked
  control-plane package. All **10/10** packages returned `Skill is valid!`.
  This is deterministic package validation only and does not upgrade the
  provider-gated runtime fields above.
- OpenCode `1.18.15` was invoked in the same fixture with `--pure --agent
-  build --model opencode/gpt-5.6-terra --format json`. It returned a provider
  `401 CreditsError` (no payment method) before a final response. A fresh
  `opencode debug skill` snapshot still resolves 89 effective skills with 89
  unique IDs and no duplicate effective IDs; path/config precedence remains
  observable, but provider execution is unavailable. The earlier read-only
  activation smoke remains the only OpenCode behavior evidence; completed
  behavior and permission enforcement remain `NOT_ASSESSED`.

### Supplemental OpenCode precedence probe — 2026-08-10

Two synthetic, disposable skills with the same ID (`shadow-demo`) were used
to test effective catalog resolution without invoking a model or transmitting
skill content. With one candidate in the project-local `.opencode/skills/`
tree and one in a configured external `skills.paths` directory,
`opencode debug skill --pure` reported 90 effective entries and one
`shadow-demo` entry, resolved to the project-local path. A companion fixture
with only the configured path resolved the same ID to the configured path.
The result directly confirms configured-path discovery and project-local
shadowing; it does not establish model selection, activation utility, or
permission enforcement.

A second no-model catalog comparison toggled both OpenCode external-skill
scan flags. The effective catalog remained 89 entries / 89 unique IDs, but
9 entries changed only their resolved source root (the direct configured path
versus its `ai-labs` overlay path). This is recorded as an alias/overlay
observation, not as proof that the two implementations are behaviorally
equivalent.

The same effective OpenCode catalog still contains external
`franky-workflow-manager` and `franky-install-workflow` entries whose
descriptions reference YAML workflow execution/registration. These are outside
the `codex-chatpgt` repository allowlist and were not modified; #35's workflow
retirement currently resolves through the `ai-labs/franky.workflow/` and
`ai-labs/franky.install/` overlay paths, so it remains repository-scoped and
cross-runtime retirement is `NOT_ASSESSED` under #12.

### Supplemental Codex fixture comparison — 2026-08-10

A disposable project-local fixture was used to obtain a safe host-observable
runtime comparison without exporting the private global skill catalog. The
fixture contained one bounded `probe-skill` and, for the co-loaded run, one
unrelated `neighbor-skill`; both passed the installed creator's
`quick_validate.py`.

| Run | Runtime observation | Evidence level |
| --- | --- | --- |
| No-skill baseline | Separate fixture with no `.agents/skills/`; Codex read only `input.txt`, emitted `skill_used: none`, and made no skill-tool/skill-procedure load. | `BEHAVIORAL_PASS` for baseline path |
| With skill | Project-local `probe-skill` was discovered and loaded; Codex read its `SKILL.md`, then only `input.txt`, and returned `skill_used: probe-skill`. | `BEHAVIORAL_PASS` for activation smoke |
| Co-loaded siblings | With `probe-skill` and unrelated `neighbor-skill` present, Codex selected only `probe-skill` for the matching fixture prompt. | `BEHAVIORAL_PASS` for this bounded routing case |
| Adjacent negative | In the same skill fixture, an arithmetic-only prompt returned `4` with no skill load. | `BEHAVIORAL_PASS` for this negative case |

This is direct evidence that the current Codex runtime can discover a
project-local skill, select it among a co-loaded sibling, and stay quiet on a
clear negative. It is a synthetic routing fixture, not a claim of utility
lift for a real #35 skill; the real-skill `baseline_delta` and hidden
catalog-wide co-loaded behavior therefore remain `NOT_ASSESSED`.

Rerun provenance for this slice is compact and disposable: Codex CLI
`0.146.0`, `-s read-only`, `--ephemeral`, `--ignore-user-config`, and
`--skip-git-repo-check`; baseline additionally used `--disable skill_search`.
Fixture hashes were `probe-skill/SKILL.md` =
`1e4864e11282d37396fa45b95342c72ddf2e94c92df194550cc3be636fe0eca5`,
`neighbor-skill/SKILL.md` =
`cf46cfef7bafef27b08de56ae80cebce846919040cf28eb09bb9f8e04567b482`, and
`input.txt` = `71f895124b66f9c026c68e643dd1216a4f488a610e29436e3d32c0f112fff027`.
The fixture was outside the repository and was not retained as an active
skill package.


### Latest isolated baseline and privacy boundary — 2026-08-10

A fresh no-skill baseline used a temporary `CODEX_HOME`, `--ignore-user-config`, `--disable skill_search`, `--ephemeral`, and read-only sandboxing against a disposable fixture. Codex read only `AGENTS.md` and `target.txt`, loaded no skill procedure, and made no writes. The matching run with the real private `franky-guidance-manager` package was rejected by the host privacy guard because it would transmit local skill content to the provider without explicit export authorization. This is recorded as a runtime/data boundary observation, not a workaround target; real-skill `baseline_delta` remains `NOT_ASSESSED`.
