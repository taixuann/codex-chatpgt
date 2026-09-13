---
name: ready-issue-executor
description: Run one exact-ready GitHub Issue or pr-N group from a scheduled automation through bounded execution, checkpointed review, and human handoff; do not use for general project management.
metadata:
  short-description: Scheduled readiness gate with exact-head review handoff
  last_reviewed: 2026-09-13
  review_interval_days: 90
---

# Ready Issue executor

This is an automation-only runtime contract. The caller must provide the
repository, canonical working directory, execution-key prefix, repo profile,
and explicit operation allowlist. This skill is self-contained: it does not
depend on `AGENTS.md`, `$issue-execution`, or another repository workflow.

Before discovery, verify the working directory exists, resolves to the
declared repository, and has the expected remote identity. If the machine,
project, network, or required connector is unavailable, return
`RUNTIME_UNAVAILABLE`; never substitute another checkout.

## Authorization

Allow only the operations named by the caller: bounded edits, validation,
internal commits, branch push, exactly one Draft PR, and narrow Todoist human
escalation. Never self-authorize, infer scope, bypass a platform permission,
or treat prompt text as sandbox/elevation permission. Anything outside the
allowlist returns `AUTHORIZATION_REQUIRED` with the exact denied operation.

Never merge, auto-merge, close Issues, mutate labels, force-push, delete
branches, discard unrelated work, modify protected/raw evidence, or spawn
child tasks unless the automation contract explicitly allows it.

## State-first dispatch

Bind one `execution_key` to one Issue or exact `pr-N` group, one implementation
thread, and at most one Draft PR. Read the machine-local ledger before making
GitHub discovery calls:

1. `REVIEW_RECEIPT_APPLYING`: finish the persisted review-receipt transition;
   do not accept another receipt or create a new request.
2. `STALLED_FOR_REVIEW`: inspect only the bound PR, literal marker, exact
   HEADs, and review receipts. Do not rescan Issues or edit code.
3. `CHECKPOINT_READY`: reconcile the missing publication step idempotently;
   never create a second PR or review request.
4. `ACTIVE`: resume the bound unit and exact thread/goal after rechecking its
   live Issue and repository snapshot.
5. No active unit: enumerate open Issues and select at most one eligible unit.

Persist the binding before code mutation. Unknown thread/goal or publication
outcomes fail closed as `THREAD_STATE_UNKNOWN`, `GOAL_STATE_MISMATCH`, or
`PUBLICATION_STATE_UNKNOWN`. One PR is one execution unit; do not create a
thread per stage.

## Ready gate

An Issue qualifies only if it is open, has the exact literal label `ready`, has
no `consult` or `discuss` blocker, is not bound to another active run, and has
stable unambiguous scope. A group label is accepted only in the canonical
`pr-N` form; `#N` is ambiguous. Every Issue in a group must pass all gates.
When multiple independent units qualify, select deterministically by oldest
Issue creation time, then lowest Issue number. No qualifying unit means silent
`NO_OP`; never add/remove labels.

## Goal/thread lifecycle

Use one implementation thread per `execution_key`. If the ledger has a
`thread_id`, resolve exactly that thread. Otherwise bind/create exactly one
implementation thread, persist its ID, and only then call `get_goal`. An
unknown thread-creation result must be reconciled before retrying; never create
blindly again. Call `get_goal` before every continuation. Create a goal exactly
once only when both the ledger and thread have no goal. Mismatch, missing, or
ambiguous native state is not success. Do not simulate goals in prose.

`STALLED_FOR_REVIEW` is ledger state, not native Goal completion or failure.
Do not use native Goal state as the review-request source of truth, and do not
issue implementation continuation while the ledger is `STALLED_FOR_REVIEW`.
Before publishing a review marker, record `native_goal_gate` as one of
`PAUSED`, `IDLE_BY_TURN_BOUNDARY`, or `UNVERIFIED`. `PAUSED` requires an
explicit host pause result. `IDLE_BY_TURN_BOUNDARY` requires host evidence
that the Goal stops after this checkpoint and cannot auto-continue. Native
`BLOCKED` or `COMPLETED` is not a substitute. Publish `STALLED_FOR_REVIEW`
only for the first two values; otherwise remain `CHECKPOINT_READY` and return
`WAIT` with reason `GOAL_CONTINUATION_UNVERIFIED`. If a marker was already
written, deactivate and verify it before remaining `CHECKPOINT_READY`. On
`CHANGES_REQUESTED`, resume the same Goal/thread; on `APPROVED`, leave the
Goal paused/idle until the parent decision. Paused is not blocked.
Formal review, when configured, uses a fresh read-only context and an
independent reviewer identity supplied by the automation, never the
implementation context or a producer-authored receipt.

## Execution and checkpoint

Run bounded implementation and validation using only the supplied repo profile
and allowlist. Internal commits are allowed, but commit, push, or ordinary PR
update is never a review trigger.

Immediately before final validation and publication, re-fetch every owning
Issue/group member and the base SHA. Compare the recorded Issue timestamp and
material acceptance criteria; a material specification change is `STALE_SPEC`,
and base movement alone is `BASE_MOVED`. Do not publish until this guard
passes. Then record `CHECKPOINT_READY` and reconcile publication in order:
push if allowed, read the remote SHA, find/create exactly one Draft PR, verify
its base/head/draft state, write the marker, and read everything back. Enter
`STALLED_FOR_REVIEW` only when:

```text
local_head_sha == remote_head_sha == pr_head_sha == checkpoint_sha
```

If an open PR already exists for the intended base/head without this
execution's owned binding, return `LEGACY_PR_CONFLICT`, do not retrofit it,
and do not create a second PR. Route the conflict to human escalation.

The Draft PR body must contain exactly one current literal marker block; any
duplicate or malformed marker fails closed:

```text
<!-- codex-review-request
execution_key: <repo>#<issue-or-group>
checkpoint_sha: <40-hex-sha>
review_request_id: <unique-id>
requires_review: true
state: STALLED_FOR_REVIEW
-->
```

Replace a stale marker for a new checkpoint. A review is eligible only when
the marker and ledger tuple match, PR HEAD equals `checkpoint_sha`, and the
tuple has not already been consumed. Consume only a fresh exact-head
`APPROVED`, `CHANGES_REQUESTED`, or `REQUIRES_HUMAN_DECISION` receipt.

Apply a consumable receipt as one recoverable transaction: verify the exact
receipt and readbacks, persist `pending_review_transition` with the exact
tuple, verdict, and target state, set ledger state `REVIEW_RECEIPT_APPLYING`,
deactivate the marker, verify marker readback, then atomically record
`consumed_review_tuple`, set the target state, and clear the pending field. On
restart, resume this pending transition at its first missing operation; never
review again, wait because the marker is inactive, or create a new request.
For `CHANGES_REQUESTED` the target is `ACTIVE`; for `APPROVED` it is
`READY_FOR_PARENT`; `REQUIRES_HUMAN_DECISION` deactivates the marker and
targets `HUMAN_ESCALATION` without resuming implementation. An inactive or
consumed marker is never review-eligible. `READY_FOR_PARENT` never authorizes
merge, Issue closure, or scientific acceptance. Any mismatch is
`NOT_ASSESSED`/wait, never approval. An existing PR without an active ledger
checkpoint/request marker is legacy/unmanaged; do not retrofit it.

Crash recovery resumes the first missing publication or pending receipt
operation after readback; it must not duplicate commits, threads, goals, PRs,
review requests, or Todoist tasks. Issue changes are `STALE_SPEC`; base
movement is `BASE_MOVED`. Do not silently rebase, force-push, or discard work.

## Todoist and receipt

Use Todoist `Goal Tracker` only for `REQUIRES_HUMAN_DECISION`,
`AUTHORIZATION_REQUIRED`, `READY_FOR_PARENT`, or unrecoverable
`REVIEW_NOT_ASSESSED`. Dedupe by `execution_key + blocker_type`; set no
deadline or priority. Search/read before creating. Mutate or complete only a
task containing the exact `Managed-by: Codex Execution Gate` marker; never
touch a user-created lookalike. Complete that owned task when its represented
blocker resolves and execution safely continues. Projection failure leaves the
source state unchanged.

Return one compact receipt with execution key, disposition/state,
Issue/PR/thread/goal IDs, all HEAD/checkpoint SHAs, validation, review tuple,
Todoist status, changed paths, and limitations. Never claim completion,
acceptance, or review without exact evidence.

Read [`references/protocol.md`](references/protocol.md) only for the ledger,
transition, marker, receipt schema, and the small acceptance matrix during
implementation or audit.
