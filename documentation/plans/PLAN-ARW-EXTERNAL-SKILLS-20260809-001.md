---
id: PLAN-ARW-EXTERNAL-SKILLS-20260809-001
issue: 14
status: active-parallel
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
