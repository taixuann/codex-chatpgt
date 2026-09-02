---
name: intent
description: Acquire and converge evidence-backed intent from a user request or GitHub Issue before planning; use for bounded context intake and handoff, not implementation planning, workflow execution, or review.
metadata:
  family: intent
  status: explicit_only
  last_reviewed: 2026-09-02
  review_interval_days: 90
---

# Intent family

Intent is a bounded context-acquisition and convergence stage. It is not a
planning engine, workflow engine, memory platform, or lifecycle database. GitHub
Issues/Plans/PRs and `documentation/architecture/workflow/operation.md` remain
the durable authority.

## Origins and routing

There are exactly two origins:

| Origin | Load | Contribution |
| --- | --- | --- |
| GitHub Issue | `issue-intake` | canonical intake, Issue audit, relationships, and stale-state observations |
| User idea/request | `idea-intake` | preserve wording, resolve relevant context, and identify material gaps |

Load `intent-grill` only when evidence leaves an authority, boundary, priority,
outcome, evidence, or trade-off question that only the user can answer. Existing
`interview-me`, `idea-refine`, and `define-goal` remain optional specialized
reasoning contributions; they do not declare readiness.

Read [source-contract.md](references/source-contract.md), then the selected
origin skill. Load only references needed for the current request:
[workspace-resolution.md](references/workspace-resolution.md),
[context-resolution.md](references/context-resolution.md),
[evidence-classification.md](references/evidence-classification.md),
[adaptive-depth.md](references/adaptive-depth.md),
[convergence-audit.md](references/convergence-audit.md),
[quality-gates.md](references/quality-gates.md), and
[intent-handoff.md](references/intent-handoff.md).

For Issue origin also read [issue-audit.md](references/issue-audit.md) and
[relationship-audit.md](references/relationship-audit.md). For a non-trivial
human projection read [orientation-view.md](references/orientation-view.md).

## Root-owned lifecycle

The root orchestrates a bounded loop, not a blind checklist:

```text
ANCHOR → INVESTIGATE ↔ CONVERGE → HANDOFF
```

1. **ANCHOR** — run `intentctl workspace`, load root-to-CWD instructions, and
   bind the origin. Reuse the active repository; do not hunt sibling repos.
2. **INVESTIGATE** — perform source intake, context resolution, smallest
   sufficient evidence acquisition, claim classification, and Issue
   relationship/staleness checks when material. Promote `light → focused →
   deep` only on evidence-backed triggers.
3. **CONVERGE** — acquire factual gaps, ask only material user questions,
   synthesize objective/success/scope/out-of-scope/decisions/unknowns, run a
   convergence audit, and project a human-readable orientation for
   non-trivial work.
4. **HANDOFF** — use shared `session-packet-management` when required, expose
   compact trust/freshness signals, run fresh-context recovery evaluation, and
   apply the readiness gate.

The inspectable origin × depth requirements live in
[requirement-matrix.yaml](references/requirement-matrix.yaml). Do not invent
per-agent required-stage rules. See [run-state.md](references/run-state.md) for
the compact state contract.

## Run state and gate

Use one compact machine-readable run state (`intent_run`, schema version 1)
with origin, workspace anchor, depth, stage statuses, evidence/claims,
decisions, unknowns, handoff, and trust signals. The controlled stage states
are `passed`, `skipped_with_reason`, `not_applicable`, `blocked`, and `failed`.

The deterministic helper is:

```bash
python3 skills/intent/scripts/intentctl.py workspace
python3 skills/intent/scripts/intentctl.py init --origin github_issue --locator owner/repo#96 --depth focused --output intent-run.yaml
python3 skills/intent/scripts/intentctl.py status intent-run.yaml
python3 skills/intent/scripts/intentctl.py validate intent-run.yaml
python3 skills/intent/scripts/intentctl.py staleness intent-run.yaml
python3 skills/intent/scripts/intentctl.py readiness intent-run.yaml
python3 skills/intent/scripts/intentctl.py fresh-context intent-run.yaml
```

Scripts enforce machine-observable invariants only; they do not interpret
architecture or user intent. `PLAN_READY` is emitted only by the root
readiness gate after applicable gates G1–G6 pass. Otherwise return an explicit
`BLOCKED_*` or validation failure state.

Default output stays in the conversation. Persist a packet only when the work
is non-trivial or the user explicitly requests a governed handoff. Never write
an Issue, plan, task, or repository content as an intent side effect.
