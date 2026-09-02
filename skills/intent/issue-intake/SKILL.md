---
name: issue-intake
description: Intake and audit a GitHub Issue against current repository evidence, relationships, and stale state; use for Issue-origin intent, not Issue mutation, planning, or implementation.
metadata:
  family: intent
  stage: investigate
  last_reviewed: 2026-09-02
  review_interval_days: 90
---

# Issue intake

## Trigger

Use when a GitHub Issue is the explicit intent source.

## Inputs

Canonical `owner/repo#number` or Issue URL, current workspace anchor, and the
Issue's live body/comments/state.

## Procedure

1. Preserve the exact Issue locator and observed timestamp.
2. Capture material title/body, labels, state, comments, and linked PRs.
3. Inspect only repository/canonical surfaces implicated by the Issue.
4. Classify claims as confirmed, inferred, unknown, user decision, or proposed.
5. Check stale assumptions and material duplicate/overlap/dependency/
   parent-child/supersession relationships.
6. Return bounded observations, evidence IDs, unresolved authority questions,
   and a suggested depth. The root intent skill owns convergence and readiness.

Use the root references [issue-audit.md](../references/issue-audit.md) and
[relationship-audit.md](../references/relationship-audit.md) for the detailed
claim and relationship checklists.

## Output

An Issue intake contribution with source identity, current observations,
relationship findings, claim classifications, and blockers/open questions.

## Boundary

This skill does not edit, assign, close, or comment on Issues; choose a plan;
create tasks; or emit `PLAN_READY`.

## Stop

Stop on an unverifiable locator, repository mismatch, inaccessible canonical
state, or contradictory evidence that needs reconciliation.

## Validation

Use `intentctl validate` for the run state and retain evidence locators; a
successful schema check does not prove semantic Issue quality.
