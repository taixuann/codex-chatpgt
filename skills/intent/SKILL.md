---
name: intent
description: Normalize an intent from the user's request or a GitHub Issue into a validated intent packet, routing to the smallest intent subskill. Use for ambiguous ideas, goal clarification, or issue intake; do not use for implementation planning or arbitrary documentation.
metadata:
  family: intent
  status: explicit_only
  last_reviewed: 2026-09-02
  review_interval_days: 90
---

# Intent family

This is a small routing family, not a second lifecycle engine. It owns only the
bounded transition from an allowed intent source to a confirmed, testable
intent packet. Issue/PLAN and `documentation/architecture/workflow/operation.md`
remain the authority for durable lifecycle state.

## Allowed sources

An intent may originate only from:

1. the user's current request or explicitly pasted wording; or
2. a GitHub Issue identified by repository and issue number/URL.

Repository files, prior plans, reviews, memory, and agent suggestions may
provide context or evidence, but they cannot silently become the intent source.
Record the source locator in the packet. Do not create or update a GitHub Issue
from this family unless a separate user request authorizes that mutation.

Read [source-contract.md](references/source-contract.md) before constructing a
packet.

For the source-specific evidence checklist, read
[source-audit.md](references/source-audit.md). When the user explicitly asks
for persistence or a governed handoff, also read the shared
[intent-plan-session-bridge.md](../references/intent-plan-session-bridge.md)
and route packet creation through `session-packet-management`. Do not create a
session packet for a raw, unconfirmed idea.

## Scenario router

Choose one primary subskill:

| Signal | Load | Do not use when |
| --- | --- | --- |
| The user does not yet know the desired outcome, audience, constraint, or success bar | `interview-me` | the request is already concrete |
| There is a rough concept and the user wants alternatives or assumption testing | `idea-refine` | the user wants a task list or implementation plan |
| The direction is chosen but needs a measurable objective and acceptance bar | `define-goal` | the request is ordinary implementation with clear scope |

Use [scenario-routing.md](references/scenario-routing.md) for contrastive
examples and tie-breaks. Load only the selected subskill's `SKILL.md` and its
referenced resources; do not load every leaf by default.

## Bounded procedure

1. Classify the source as `user` or `github_issue`; stop if it is neither.
2. Audit the source using the applicable branch in `source-audit.md`.
3. Select the smallest scenario using the router above.
4. Execute that subskill's procedure and keep its negative boundary.
5. Produce an `intent_packet` with objective, success criteria, scope,
   out-of-scope items, assumptions, open questions, source locator, and
   confirmation state. Keep unresolved intent unconfirmed.
6. Run the deterministic validator:

   ```bash
   python3 skills/intent/scripts/validate_intent_packet.py PACKET.yaml
   ```

   Add `--ready-for-plan` only when the user has explicitly confirmed the
   packet and no material open question remains.

## Output and stop conditions

The default output is the packet in the conversation; saving a file requires
explicit user approval. Stop and surface the blocker when the source is not a
user request/GitHub Issue, success cannot be made testable, or confirmation is
missing. This family does not create tasks, implement code, choose an agent, or
approve a plan.

See [intent-packet.md](references/intent-packet.md) for the packet contract.
