---
id: PLAN-ARW-SKILL-WORKFLOW-RATIONALIZATION-20260809-001
issue: 13
status: completed
blocked_by: [2, 5, 6, 10]
activation_gate: core-plus-project-evidence
scope: skill-workflow-rationalization
---

# Objective

Audit and rationalize the existing skill/workflow surface using real runtime/project evidence while preserving distinct useful procedures, permissions, validation, and rollback guarantees.

# Activation gate

Execute only after #2/#5/#6/#10 provide enough evidence to distinguish stable capability from legacy wrapper, decorative workflow, or still-unproven behavior. Consume #14 external-skill evidence where relevant.

This plan is now completed for the control-plane baseline. The activation gate
was satisfied by the merged #19 implementation, the live workflow/consumer
inventory, and the explicit user authorization to finish the bounded cleanup.
Future portability and scientific-runtime extensions remain separately gated.

## Current-state supersession note — 2026-08-10

This document is retained as the historical Issue #13 v1 rationalization
record, not as the current execution destination. Its original package table
and follow-up groups are superseded by the creator-gated #35 matrix in
`PLAN-ARW-SYSTEM-SKILLS-V2-20260810-001.md` and D-009. In particular,
`franky-workflow-organizer` is currently `RETIRE`, and the unconsumed Franky
machine workflow tree is retired; do not reactivate the historical `KEEP` or
`GENERALIZE` rows without a new evidence-backed issue.

## Confirmed disposition matrix (2026-08-09)

| Skill | Current consumer / unique procedure | Disposition | Follow-up |
| --- | --- | --- | --- |
| `franky-agent-installer` | Agent TOML/schema, collision, sandbox, and registry-boundary checks; used by Franky install branches and CI | GENERALIZE | #13 group 2: remove persona coupling and retain adapter validation |
| `franky-cron-installer` | Scheduler inventory, timezone/collision checks, and approval-bound job mutation | GENERALIZE | #13 group 2: retain scheduler-specific safety boundary |
| `franky-external-handoff` | Role-neutral handoff packet with scope, evidence, rollback, and no implicit execution | MERGE | Replaced by tracked `skills/control-plane/external-handoff` |
| `franky-github-review` | PR comment triage; delegated to installed `gh-address-comments` | REPLACE | Removed; use `gh-address-comments` |
| `franky-goal-session` | Legacy goal-package, walkthrough, and promotion metadata lifecycle | RETIRE | Removed; use Issue/PLAN/PR unless an explicit AI Labs goal package is required |
| `franky-guidance-manager` | Scoped `AGENTS.md` discovery, precedence, and approval boundary | GENERALIZE | #13 group 2: keep as instruction-chain maintenance |
| `franky-maintenance` | Read-first control-plane inventory and deterministic validators | GENERALIZE | #13 group 2: remove mandatory audit-record writing from ordinary maintenance |
| `franky-project-linker` | Reversible skill/workspace links and link audit | MERGE | Replaced by tracked `skills/install-project-link` and its audit helper |
| `franky-promotion` | Explicit Codex-to-AI-Labs export with hashes, registry destinations, and rollback | DEFER | #12: preserve boundary until portability/export is accepted |
| `franky-skill-installer` | Skill scope, collision, metadata, dependency, and rollback checks | REPLACE | Removed; use installed `skill-installer`/`skill-creator` |
| `franky-source-migration` | Report-first migration from Claude/OpenCode/Antigravity into Codex artifacts | DEFER | #12: do not implement portability before evidence |
| `franky-workflow-factory` | Staged workflow-package generation and flaw detection | RETIRE | Removed with proposal-only factory pipelines; no machine consumer existed |
| `franky-workflow-organizer` | Thin workflow contract authoring and deterministic YAML validator used by CI | GENERALIZE | #13 group 4: keep validator while retained workflow contracts exist; narrow agent-facing authoring |
| `shared-session-closeout` | Role-neutral session acceptance/continuation record | KEEP | Retained as the single procedure; duplicate YAML workflow removed |

Each mutation is a small reviewable change with a before/after reference audit,
focused tests, and rollback path. The bounded cleanup in this plan is the
approved implementation for this repository.

## Bounded execution groups

1. **Thin wrappers and legacy packages** — replace GitHub/skill/goal/workflow
   wrappers only where installed capabilities or Issue/PLAN/PR semantics cover
   the same behavior.
2. **Retained control-plane capabilities** — generalize agent, scheduler,
   guidance, and maintenance procedures without removing their permission or
   safety boundaries.
3. **Deferred portability/export** — keep source migration and promotion
   boundaries unchanged until #12 provides runtime evidence.
4. **Workflow machinery** — remove factory/organizer validators only after the
   workflow consumer inventory identifies which contracts remain in use.

# Execution phases

1. Inventory every current skill/workflow: trigger, purpose, consumers, scripts/assets, mutation boundary, observed use.
2. Compare against built-in/official/external alternatives from #14.
3. Classify each as KEEP / GENERALIZE / MERGE / REPLACE / RETIRE / DEFER.
4. Challenge both over-complexity and over-aggressive cleanup.
5. Change only items with enough evidence; leave uncertain components DEFERRED.
6. Validate all changed references, deployment paths, behavior, and rollback.
7. Reconcile only accepted architectural outcomes to CURRENT/DECISIONS.

# Validation

- complete inventory exists;
- every changed component has evidence-backed disposition;
- retained skill descriptions are discriminative;
- retained workflows have real state/gate/runtime value;
- deterministic work remains scripts/tools where appropriate;
- no broad rename/refactor occurs solely for aesthetics;
- required capability is not lost during simplification.

# Stop conditions

Defer any component when evidence is insufficient. Do not optimize for minimum file count. Stop broad cleanup if migration risk exceeds demonstrated value.

# Definition of done

The active surface is smaller or more coherent, with every change justified by observed use/overlap and no loss of meaningful procedure, permission, validation, or recovery behavior.
