---
name: idea-intake
description: Preserve and investigate a user idea or request using the active workspace and targeted evidence; use for user-origin intent, not generic planning or repository hunting.
metadata:
  family: intent
  stage: investigate
  last_reviewed: 2026-09-02
  review_interval_days: 90
---

# Idea intake

## Trigger

Use when the user request itself is the intent source and it needs context
resolution before planning.

## Inputs

The user's exact wording, active CWD/repository anchor when present, and only
the canonical/local surfaces relevant to the request.

## Procedure

1. Preserve the original request and locator before restating it.
2. Determine whether it concerns an existing system and reuse the active
   repository context when available.
3. Resolve factual uncertainty from local/canonical evidence first.
4. Use targeted external authoritative research only when it materially affects
   the problem boundary.
5. Return evidence, claims, unresolved authority/preference gaps, and a bounded
   direction to the root for convergence.

## Output

An idea intake contribution containing original wording, context observations,
claim states, relevant references, and open questions.

## Boundary

Do not search sibling repositories by default, force an interview, prescribe
implementation, create plans/tasks, or authorize a workflow-owned `PLAN_READY` transition.

## Stop

Stop when the request's source is not the current user, the repository boundary
is ambiguous, or a material authority decision remains unresolved.

## Validation

Run `intentctl workspace` for the anchor and `intentctl validate` for the
resulting run state. Semantic quality is evaluated by behavioral fixtures.
