# UPDATE

UPDATE changes an existing owned skill only after an observed need and a pinned baseline. Every intended change maps to an approved delta; every protected behavior maps to regression evidence.

## Lifecycle

U0 BIND → U1 BASELINE → U2 IMPACT → U3 DESIGN DELTA → U4 REVIEW/APPROVE → U5 PLAN MAPS → U6 MUTATE → U7 VALIDATE → U8 STATIC WALKTHROUGH → U9 AFFECTED EVALUATE → U10 REGRESSION → U11 REPAIR/RE-ENTRY → U12 QUALIFY → U13 HANDOFF

### U0–U4: bind and approve

Bind target, governing Issue, repository/CWD, allowed paths, base branch/HEAD, current action surface, acceptance signal, and scope envelope. Record IN_SCOPE, OUT_OF_SCOPE, forbidden expansion, and observed-but-unrequested items.

Establish structural, behavioral, and ownership baselines. Missing behavior is NOT_ASSESSED, never assumed PASS. Trace requested change → affected behavior → state/workflow → artifacts/dependencies → tests/evals → regression surface. Classify as NON_MATERIAL, MATERIAL_LOCAL, or MATERIAL_ARCHITECTURAL, never by diff size.

Record CURRENT → DELTA → PROPOSED, protected invariants, removed/new behavior, affected cases, and open risk. No design gate is required for non-material wording/link changes; local changes need a focused diagnostic challenge; architectural changes need full design review and human approval.

### U5–U8: map, mutate, validate, walk

Keep these sections in the existing task-scoped `intent.md` evidence note on the
Issue/session surface; they are maps, not a second workflow state store:

    Change Map       path, current owner, delta, reason, validation, status
    Preservation Map protected behavior, owner, baseline, risk, must-not-change
    Regression Map   protected behavior, baseline/candidate evidence, class, status

Change the smallest correct semantic surface. Preserve upstream-derived scripts, references, tests, state, and behavior unless the approved delta changes their ownership. Do not add a generic workflow engine or drive-by cleanup.

Validate the changed contract and protected contract separately. Then walk one changed path and the highest-risk preserved path from request through routing, state, tool boundary, branch, and terminal output.

### U9–U11: evaluate, compare, repair

Run changed behavior, adjacent high-risk behavior, and must-pass protected cases in an isolated test environment. Compare outcome, workflow fidelity, routing, state transitions, artifacts/receipts, side effects, and authority boundaries.

Classify each dimension EXPECTED_CHANGE, IMPROVEMENT, UNCHANGED, REGRESSION, NOT_COMPARABLE, or NOT_ASSESSED. For stochastic output, compare semantic checkpoints and forbidden actions, not prose bytes.

Repair at the earliest invalidated owner: mechanical → mutation/validation; authoring → mutation/validation/walk; behavior → through evaluation; evaluator → fix evaluator and rerun the same candidate; design or scope invalidation → U2/U3; architecture/authority invalidation → full design review. A repair stales downstream evidence; do not restart without cause.

### U12–U13: qualify and hand off

Freeze exact candidate/base/evidence. Require requested change, protected invariants, explained diff, current validation, affected evaluation, regression map, approval, and explicit limitations. Issue-driven targets then use fresh separate terminal WORK and GOAL review through issue-execution.

Return baseline, candidate, approved delta, changed surfaces, preserved invariants, validation, real-task/regression results, repair lineage, NOT_ASSESSED, rollback reference, and technical disposition. Stop at awaiting_parent_decision; UPDATE never accepts, publishes, merges, or closes.

## Real UPDATE cases

- skills/issue-execution: keep Issue/session/Git ownership, bounded worker routing, fresh WORK → GOAL, technical eligibility, and parent handoff. Existing preflight/reconcile/acceptance helpers remain the state owner.
- skills/athena-review: preserve WORK, GOAL, and diagnostic joint semantics; add a subordinate fingerprinted review_contract.references dimension. Caller references never replace Issue authority or criteria manifests.
