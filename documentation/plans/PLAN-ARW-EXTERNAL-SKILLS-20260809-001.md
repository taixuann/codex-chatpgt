---
id: PLAN-ARW-EXTERNAL-SKILLS-20260809-001
issue: 14
status: conditional-pass
activation_gate: none-for-qualification
scope: external-skill-qualification
---

# Objective

Build a small evidence-backed external skill collection by qualifying maintained implementations before creating or retaining local equivalents.

# Initial candidates

Prioritize:

- skill creator/evaluator;
- `gh-address-comments`;
- `acquire-codebase-knowledge`;
- `planning-and-task-breakdown`;
- `idea-refine`;
- `refactor-plan`;
- `agentic-eval`.

Reference-only patterns may include quality playbooks, Anthropic structure patterns, Microsoft testing harnesses, and Agent Skills specifications.

# Execution phases

1. Record exact source/path, maintainer, license where relevant, ref/SHA/version.
2. Inspect actual SKILL.md/scripts/references, not catalog prose.
3. Record trigger, outputs, tools, side effects, context footprint, tests, mutation boundary.
4. Compare against built-in/local capability and note replacement risk.
5. Test positive/negative trigger prompts where runtime supports it.
6. Run one representative task before canonical approval.
7. Score with Issue #14 quality gate.
8. Classify APPROVE_CORE / APPROVE_ON_DEMAND / REFERENCE_ONLY / REJECT / DEFER.
9. Feed replacement/retirement evidence to #13; do not remove local components here.

# Validation

- provenance is exact;
- runtime qualification is observed rather than assumed;
- collection remains intentionally small;
- no external skill is promoted solely from popularity/score;
- no new external-skill catalog/top-level folder is required unless evidence later justifies one.

# Immediate integration points

Use #2 to compare repository/codebase acquisition candidates and #5/#6 for planning/eval/review candidates. Qualification can run in parallel with core execution.

# Stop conditions

Reject/defer skills with vague triggers, wrapper-only value, unclear provenance, hidden mutation, excessive context cost, or no measurable advantage over existing behavior.

# Definition of done

The first small collection has evidence-backed dispositions and exact provenance, with only runtime-proven candidates eligible for canonical promotion.

## Qualification snapshot — 2026-08-10

This snapshot is the bounded evidence handoff to #38 and #35. It records
artifact-level inspection and runtime observations; it does not install an
external catalog or copy upstream packages into this repository.

### Creator/evaluation candidates

| Candidate | Exact source/ref and license | Artifact evidence | Runtime/overlap finding | Disposition |
| --- | --- | --- | --- | --- |
| Installed Codex/OpenAI creator | `/Users/tai/.codex/skills/.system/skill-creator`; Codex `0.146.0`; local `license.txt` Apache-2.0 | `SKILL.md`, `init_skill.py`, `quick_validate.py`, `generate_openai_yaml.py`, `references/openai_yaml.md`, and `agents/openai.yaml` inspected; SHA-256 recorded for the three core files in the #38 release report | System-owned and already available to Codex; copying would create a drifting duplicate | **USE_EXISTING** |
| Anthropic creator | `anthropics/skills/skills/skill-creator` at `b0cbd3df1533b396d281a6886d5132f623393a9c`; skill `LICENSE.txt` Apache-2.0 | `SKILL.md`, `agents/{analyzer,comparator,grader}.md`, eval viewer, schemas, `run_eval.py`, `run_loop.py`, `aggregate_benchmark.py`, `improve_description.py`, and `package_skill.py` inspected | Strong A/B/eval ideas, but scripts assume Claude Code/`claude -p`; no Codex/OpenCode execution proof in this run | **REFERENCE_ONLY**; adapt concepts only if a later measured gap earns it |
| `github/awesome-copilot` creator/eval patterns | repo `main` at `3f0bba475ec40b9680e1d0311b9caffeec5ad4c3`; MIT | `skills/agentic-eval/SKILL.md` inspected; generic reflection/evaluator-optimizer examples | Duplicates #38 contract at a higher abstraction and has no needed deterministic backend | **DEFER / REFERENCE_ONLY** |
| `raddue/crucible` | repo `main` MIT; exact current ref was inspected through GitHub metadata only | No artifact was needed after the installed creator passed structural validation | Large orchestration surface would exceed the bounded need | **DEFER** |
| `skill-probe`, SkillSpector, SkillLens and similar scanners | Candidate names only; no artifact/ref/license/runtime qualification was required for the current gate | No package was installed or copied | A scanner would add cost before a concrete missing gate is reproduced | **DEFER** |

### Engineering-discipline candidates

| Candidate | Exact artifact/ref and license | Unique evidence / overlap | Runtime fit | Disposition |
| --- | --- | --- | --- | --- |
| `github/awesome-copilot/skills/acquire-codebase-knowledge/SKILL.md` | `3f0bba475ec40b9680e1d0311b9caffeec5ad4c3`, repository MIT | Produces seven `docs/codebase/*.md` documents plus a scan; broader and more mutating than #2's bounded context packet | No Codex/OpenCode run; would add catalog/context cost | **REFERENCE_ONLY / DEFER**; do not replace #2 |
| `github/awesome-copilot/skills/refactor-plan/SKILL.md` | same ref, repository MIT | Strong plan-before-edit boundary, but duplicates Issue/PLAN and parent planning policy | No runtime activation proof | **REFERENCE_ONLY** |
| `github/awesome-copilot/skills/harness-engineering/SKILL.md` | same ref, repository MIT | Useful instructions→checks→drift pattern; overlaps #24, `franky-maintenance`, and scoped AGENTS policy | No runtime activation proof | **REFERENCE_ONLY**; adapt policy only |
| `adityaarakeri/senior-agent-skills` | `1a6c8523504f145db1ef917b123b7c052abca5ba`; repository license metadata absent | Eight small skills inspected (`repo-recon`, `debug-protocol`, `safe-refactor`, `self-review`, `verify-done`, `plan-first`, `tdd-loop`, `git-hygiene`); useful discipline patterns but redistribution terms are unresolved | No runtime install; no copy | **REFERENCE_ONLY / DEFER** |
| `SteveVitali/agent-skills` | `6f6c5843148443d3d3c4fe034c03eda669754bfc`; MIT | `agent-docs`, `refresh-repo-docs`, and `self-review` inspected; useful drift/self-review procedures, but each has its own scripts and assumptions | No Codex/OpenCode execution proof; local duplicate would add catalog pressure | **REFERENCE_ONLY** |

### Effective runtime observations

- Codex `0.146.0`, configured model `gpt-5.6-terra`, reasoning `medium`.
- The earlier Codex local discovery contained 61 `SKILL.md` files and 49
  unique frontmatter names; 10 name groups had duplicate source paths. After
  retirement cleanup, the current root scan is 60 files / 54 unique basenames.
  A fresh model-visible prompt-input snapshot records 86 entries / 58 unique
  names and 13 duplicate-name groups. A fresh read-only startup returned
  `PROBE_OK` but emitted the observable warning that descriptions were
  shortened to fit the 2% skills context budget. This is catalog-pressure
  evidence, not a claim about hidden selection behavior.
- OpenCode `1.18.15` resolved 89 effective skills with unique effective names.
  `debug config` showed path-based global skill sources, built-in
  `customize-opencode`, permissive default `build` permissions, and a separate
  OpenCode-native `config.opencode.skill-creator`. The effective catalog exposed
  `franky-install-guidance` and `franky-install-project-link` adapters, not the
  Codex `franky-guidance-manager` package. Therefore cross-runtime identity is
  **NOT_ASSESSED**, not portable by folder resemblance.
- A real Codex read-only dogfood on a synthetic guidance fixture selected and
  applied `franky-guidance-manager`'s scoped-chain procedure without writes.
  An earlier natural-prompt no-skill attempt could not be isolated because
  `--ignore-user-config` still loaded the host skill. A later explicit
  `--disable skill_search` baseline completed without a skill-tool event, but
  no matching with-skill rerun was authorized; baseline delta remains
  **NOT_ASSESSED** rather than PASS.

### Handoff decisions

1. #38 should use the installed OpenAI creator as the canonical creator and
   keep Anthropic/OSS material as references unless a measured missing gate
   justifies an adapter.
2. #35 should resolve Tier-2 families through policy/tool/reference or
   maintained reuse before any local package is created.
3. No registry, marketplace, telemetry, dependency graph, workflow engine, or
   external skill catalog was created by this qualification slice.
