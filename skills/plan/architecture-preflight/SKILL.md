---
name: architecture-preflight
description: Resolve material architecture and cross-domain decisions before a plan is accepted. Use only when design uncertainty could change scope, dependencies, risk, or verification; do not clarify Intent or implement.
metadata:
  family: plan
  stage: plan
  last_reviewed: 2026-09-04
  review_interval_days: 90
---

# Architecture preflight

Use this leaf only after Intent is accepted and a material design uncertainty
could invalidate the plan. Inspect the repository and existing evidence first;
do not reopen goal, scope, or success-criteria clarification. Return a compact
architecture contract with decisions, alternatives rejected, assumptions,
authority escalations, risks, and verification implications. Stop before task
execution, approval, implementation, or commit.

## Procedure

1. Identify the decision or coupling that could change the plan.
2. Inspect existing interfaces, canonical patterns, dependencies, ownership,
   trust boundaries, durable state, and rollback constraints relevant to it.
3. Resolve the smallest sufficient set of design decisions. Reuse a canonical
   pattern when evidence already settles the choice; do not expand a corpus or
   introduce components without a demonstrated need.
4. Record unresolved authority decisions explicitly and map each decision to
   affected tasks, acceptance criteria, and verification.
5. Report what was inspected, what remains `NOT_ASSESSED`, and the evidence
   needed before the parent can accept the Plan.

Use the bounded [retrieval policy](references/retrieval-policy.md) and its
selector (`scripts/select_references.py`) for
selective reference loading. It is consulted only for a matching material
signal and is skipped when canonical repository evidence resolves the design.

## Boundaries

This is a design-preflight procedure, not a requirements interview,
specification writer, task decomposer, agent/model selector, reviewer, or
executor. For accepted Intent with no material architecture uncertainty, do
not load this leaf. Independent Plan critique belongs to
`review/independent-artifact-review` with review class `plan_contract`.
