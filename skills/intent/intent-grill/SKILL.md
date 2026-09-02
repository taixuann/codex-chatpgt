---
name: intent-grill
description: Ask the smallest evidence-aware set of user questions for unresolved intent or authority gaps; use after evidence intake, not for routine interviews, planning, or confidence scoring.
metadata:
  family: intent
  stage: converge
  last_reviewed: 2026-09-02
  review_interval_days: 90
---

# Intent grill

## Trigger

Use only after local, canonical, and targeted external evidence cannot resolve
a material question.

## Inputs

The bounded intent run, evidence/claim map, and unresolved questions.

## Procedure

1. Remove questions answerable from retained evidence.
2. Classify each remaining question as `OUTCOME`, `BOUNDARY`, `PRIORITY`,
   `AUTHORITY`, `EVIDENCE`, or `TRADE_OFF`.
3. Batch independent questions; ask sequentially only when one answer changes
   the next question.
4. Record the user's answer as `USER_DECISION`, or preserve an explicit
   unresolved blocker.

## Output

A small question set and the resulting decision/open-question updates for the
root intent run.

## Boundary

No mandatory confidence percentage, prediction of future questions, magic
confirmation phrase, repository-fact questions, plan generation, or
`PLAN_READY` transition.

## Stop

Stop when no material user-only gap remains or the user defers a required
decision; return the explicit blocker.

## Validation

`intentctl validate` checks decision and open-question structure. Whether the
questions were truly necessary remains a behavioral review concern.
