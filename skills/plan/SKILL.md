---
name: plan
description: Turn a confirmed user or GitHub Issue intent into a bounded, validated plan packet by routing to one planning subskill. Use when requirements or implementation tasks need structure; do not use to implement, commit, or replace Issue/PLAN authority.
metadata:
  family: plan
  status: explicit_only
  last_reviewed: 2026-09-02
  review_interval_days: 90
---

# Plan family

This family packages planning capabilities; it is not a universal lifecycle or
workflow engine. The repository's Issue/PLAN contract and
`documentation/architecture/workflow/operation.md` remain authoritative for
durable state, gates, approvals, and sequencing.

## Accepted inputs

A plan must be grounded in either:

1. a confirmed `intent_packet` produced from a user request or GitHub Issue; or
2. a GitHub Issue with enough scope to plan directly.

Do not treat a memory entry, review, arbitrary document, or agent suggestion as
the origin of a plan. Read [plan-packet.md](references/plan-packet.md) before
constructing the output.

When a confirmed intent or plan must survive across sessions, read the shared
[intent-plan-session-bridge.md](../references/intent-plan-session-bridge.md)
and use `session-packet-management` only at the explicitly approved
persistence boundary. The bridge records provenance; it does not grant build,
commit, or publication authority.

## Scenario router

| Signal | Load | Do not use when |
| --- | --- | --- |
| Requirements/specification is absent, contradictory, or needs explicit assumptions and success criteria | `spec-driven-development` | a validated specification already exists |
| Architecture or cross-domain decisions may invalidate the approach | `socratic` | the task is already mechanically decomposed |
| Intent/specification is accepted and needs ordered tasks, dependencies, acceptance, and verification | `planning-and-task-breakdown` | the request is still an unconfirmed idea |

Use [scenario-routing.md](references/scenario-routing.md) for tie-breaks. Load
only the selected leaf and its necessary references; do not load the whole
family by default.

## Bounded procedure

1. Verify the input source and confirmation state. Stop if no user/GitHub Issue
   provenance is available or if an intent packet is unconfirmed.
2. Select one primary scenario. Record any unresolved architecture or
   requirements question rather than silently inventing an answer.
3. Run that leaf's procedure. The leaf may recommend a supporting capability,
   but the parent must not turn the recommendation into an automatic lifecycle.
4. Produce a `plan_packet` containing source, objective, assumptions,
   dependencies, ordered tasks, acceptance criteria, verification commands,
   checkpoints, out-of-scope items, and open questions.
5. Run the deterministic validator:

   ```bash
   python3 skills/plan/scripts/validate_plan_packet.py PACKET.yaml
   ```

   Add `--ready-for-build` only after the responsible human has explicitly
   approved the plan and all material open questions are closed.

## Output and stop conditions

The default output is a plan packet in the conversation or in the task's
approved PLAN location. This family does not write code, create commits,
choose agents, close Issues, or claim runtime acceptance. Stop on missing
provenance, unresolved authority decisions, cyclic dependencies, or missing
verification evidence.
