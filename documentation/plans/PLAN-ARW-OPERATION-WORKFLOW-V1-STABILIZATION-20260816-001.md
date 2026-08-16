---
id: PLAN-ARW-OPERATION-WORKFLOW-V1-STABILIZATION-20260816-001
status: active
updated: 2026-08-16
owner: Prometheus
issue: "#62"
---

# Operation Workflow v1 stabilization

## Objective

Reconcile the repository's current control-plane documentation with the live
Issue/PR lifecycle so a new work unit can identify its authority, follow the
Issue → optional PLAN → PR → CI/review → merge path, and record post-merge
state without implying unavailable runtime behavior.

## Confirmed baseline

This pass starts from `origin/main` at merged PR #76 (`4ef68b2`). PR #72
(Argus/Prometheus/Athena hardening) and PR #74 (role-boundary hardening) are
also merged. PR #77 is still open and is not treated as merged state.

The canonical lifecycle is documented in `documentation/OPERATING-WORKFLOW.md`:

```text
Human request → Issue → optional PLAN → one branch/PR → CI/tests
→ independent review when justified → merge → CURRENT/DECISIONS reconciliation
```

The current repository does not expose native host traces for agent selection,
skill loading, runtime mutation enforcement, or host permissions. Those remain
`NOT_ASSESSED` and are not upgraded by static validation.

## Scope

- `CURRENT.md` and `DECISIONS.md` wording and ownership reconciliation.
- This stabilization plan as the single execution design for the documentation
  change.
- Live ownership clarification for Issues #60 and #62, without closing either.
- Deterministic documentation, lifecycle, role-boundary, and diff validation.

## Non-goals

- No implementation or runtime changes.
- No new agent, skill, workflow engine, router, memory layer, graph system, or
  MCP runtime.
- No scientific interpretation or project-specific research logic.
- No claim of native dispatch, skill loading, permission enforcement, or full
  runtime workflow completion.

## Issue classification

### Complete / accepted evidence

- #5 bounded execution and deterministic closure (accepted through PR #33).
- #68–#71 lifecycle hardening (accepted through PR #72).
- #74 role-boundary hardening (merged).
- #76 Personal Wiki v1 foundation (merged).

### Superseded

- #16 is closed as superseded by #75; no additional closure is proposed here.

### Blocking the v1 stabilization pass

- #62 owns the operational Issue → optional PLAN → branch/PR → CI/review →
  merge/reconciliation procedure. This pass records the current boundary but
  does not claim the issue complete without an additional end-to-end proof.
- #60 remains the approval/remote-validation hardening dependency for a fully
  accepted lifecycle, including negative human decisions.

### Active roadmap / conditional proof

#2, #6, #7, #8, #9, #10, #11, #12, #14, #15, #17, #31, #38, #44, #46, #47,
#48, #49, #56, #59, #61, and #75 remain open or conditional according to the
live issue state. Their scopes are not silently merged into #62 and no issue
is closed by this documentation-only reconciliation.

## Accepted plan

1. Keep the shared lifecycle semantic source in `OPERATING-WORKFLOW.md` and
   retain the Issue-first, PLAN-conditional, one-work-unit-branch rule.
2. Reconcile `CURRENT.md` and `DECISIONS.md` with merged PR history and the
   live open state of #62 and #77.
3. Preserve the existing role boundaries: Feynman performs scientific review;
   Argus prepares context and provenance; Prometheus executes and validates;
   Athena reviews independently; Human authority accepts or rejects.
4. Run deterministic repository validation and report host/runtime gaps as
   `NOT_ASSESSED`.

## Acceptance criteria

- `CURRENT.md` describes a stabilized control-plane foundation and explicitly
  says runtime evidence remains pending.
- `DECISIONS.md` records Issue-first and PLAN-conditional semantics without
  creating a mandatory artifact family.
- #62 is the parent lifecycle integration owner; #60 is a dependency for
  runtime context/session continuation and approval/validation hardening.
- No issue is closed without its own acceptance evidence.
- The changed documentation passes the repository validators and diff checks.

## Validation

Run `git diff --check`, the role-boundary, Feynman, and lifecycle validators,
the skill/catalog/allowlist/changelog checks, and the focused `ops/scripts`
unit suite. Verify live #60/#62 state with GitHub CLI before publication.

## Deferred items

Native host dispatch, runtime materialization, native skill loading, host
permissions, mutation enforcement, Personal Wiki runtime, Scientific Wiki
runtime, full session continuation evidence, approval-state enforcement, and
scientific acceptance remain deferred or `NOT_ASSESSED` under their owning
issues.

## Closure evidence audit

The current work unit provides a reproducible partial lifecycle trace:

```text
request (closure objective)
→ Issue #62
→ this PLAN
→ codex/operation-workflow-v1-stabilization
→ PR #78
→ hosted `validate` check: PASS
→ review: pending
→ merge: pending
→ reconciliation: pending
```

This is evidence through CI only; it is not a claim that the full lifecycle
has completed. The branch is three commits ahead of the latest `origin/main`
and contains only the intended documentation files.

A fresh bounded context packet was generated read-only from the explicit
allowlist. It recovered the repository instructions, `CURRENT.md`,
`DECISIONS.md`, the canonical operating workflow, and this PLAN with no
conflicts. Its only uncertainty was the unavailable native runtime dispatch
trace. This demonstrates deterministic context recovery, not a native session
manager or memory system.

The minimal materialization contract oracle passed 13 Franky cases and the
Codex `[agents]` configuration parser passed. The installed runtime probe
reported configuration `PASS`, while native dispatch, skill loading, and host
mutation enforcement remained `NOT_ASSESSED`.

The existing Feynman vertical artifact and Athena review provide one bounded
scientific evidence/reasoning/review slice. That slice explicitly records
Scientific Wiki as `NOT_USED` because declared project evidence was sufficient;
therefore the combined #7 + #59 + #61 proof is not complete and those issue
acceptance claims must not be closed from this artifact alone.

## Plan critique and non-goals

This is deliberately a thin documentation/state reconciliation. It does not
create a workflow engine, session database, router, new agent, new skill, or
project-specific research logic. It does not implement native dispatch,
model-mediated skill loading, host permission enforcement, or scientific
acceptance. Those require separate evidence-bearing work units.

## Completion criterion

The stabilization pass is complete only when the repository documents the
current accepted lifecycle and its limits without contradiction, validators
pass, and the next bounded work unit is explicit. Full Operation Workflow v1
acceptance remains `NOT_ASSESSED` until #62/#60 provide the missing end-to-end
and approval evidence.
