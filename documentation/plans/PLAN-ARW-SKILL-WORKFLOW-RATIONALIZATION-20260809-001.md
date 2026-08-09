---
id: PLAN-ARW-SKILL-WORKFLOW-RATIONALIZATION-20260809-001
issue: 13
status: execution-ready
blocked_by: [2, 5, 6, 10]
activation_gate: core-plus-project-evidence
scope: skill-workflow-rationalization
---

# Objective

Audit and rationalize the existing skill/workflow surface using real runtime/project evidence while preserving distinct useful procedures, permissions, validation, and rollback guarantees.

# Activation gate

Execute only after #2/#5/#6/#10 provide enough evidence to distinguish stable capability from legacy wrapper, decorative workflow, or still-unproven behavior. Consume #14 external-skill evidence where relevant.

This plan is execution-ready for bounded follow-up PRs, but the activation gate
remains in force. The matrix below records the current target without silently
retiring a capability whose runtime consumer has not yet been observed.

## Confirmed disposition matrix (2026-08-09)

| Skill | Current consumer / unique procedure | Disposition | Follow-up |
| --- | --- | --- | --- |
| `franky-agent-installer` | Agent TOML/schema, collision, sandbox, and registry-boundary checks; used by Franky install branches and CI | GENERALIZE | #13 group 2: remove persona coupling and retain adapter validation |
| `franky-cron-installer` | Scheduler inventory, timezone/collision checks, and approval-bound job mutation | GENERALIZE | #13 group 2: retain scheduler-specific safety boundary |
| `franky-external-handoff` | Role-neutral handoff packet with scope, evidence, rollback, and no implicit execution | MERGE | Fold into `skills/external-handoff` or operating guidance after overlap test |
| `franky-github-review` | PR comment triage; delegates procedure to installed `gh-address-comments` | REPLACE | #13 group 1: use `gh-address-comments`; preserve only unique governance text if proven |
| `franky-goal-session` | Legacy goal-package, walkthrough, and promotion metadata lifecycle | RETIRE | #13 group 1: use Issue/PLAN/PR; retain no package ceremony without a real consumer |
| `franky-guidance-manager` | Scoped `AGENTS.md` discovery, precedence, and approval boundary | GENERALIZE | #13 group 2: keep as instruction-chain maintenance |
| `franky-maintenance` | Read-first control-plane inventory and deterministic validators | GENERALIZE | #13 group 2: remove mandatory audit-record writing from ordinary maintenance |
| `franky-project-linker` | Reversible skill/workspace links and link audit | MERGE | Coordinate with `install-project-link` and #10; retain link audit if independently used |
| `franky-promotion` | Explicit Codex-to-AI-Labs export with hashes, registry destinations, and rollback | DEFER | #12: preserve boundary until portability/export is accepted |
| `franky-skill-installer` | Skill scope, collision, metadata, dependency, and rollback checks | REPLACE | #13 group 1: use installed `skill-installer`/`skill-creator`; retain unique local checks only if needed |
| `franky-source-migration` | Report-first migration from Claude/OpenCode/Antigravity into Codex artifacts | DEFER | #12: do not implement portability before evidence |
| `franky-workflow-factory` | Staged workflow-package generation and flaw detection | RETIRE | #13 group 1 unless a real machine workflow consumer is demonstrated |
| `franky-workflow-organizer` | Thin workflow contract authoring and deterministic YAML validator used by CI | GENERALIZE | #13 group 4: keep validator while retained workflow contracts exist; narrow agent-facing authoring |
| `shared-session-closeout` | Role-neutral session acceptance/continuation record and shared closeout YAML | KEEP | Retain one shared closeout procedure; compare YAML consumer before any merge |

No disposition above authorizes a mass rename or deletion. Each mutation must
be a small PR with a before/after reference audit, focused tests, and rollback
path.

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
