# Scheduled execution protocol

Load this reference only while implementing, recovering, or auditing a run.

## Ledger

Keep one machine-local record per execution key, outside tracked repository
content:

```yaml
execution_key: taixuann/<repo>#<issue-or-group>
issue_numbers: [N]
thread_id: <native-thread-id>
goal_id: <native-goal-id>
repo: <owner>/<repo>
cwd: <canonical-absolute-path>
worktree: <canonical-absolute-path>
pr_number: <N-or-null>
issue_updated_at: <observed-value>
base_sha: <sha-or-null>
local_head_sha: <sha-or-null>
remote_head_sha: <sha-or-null>
pr_head_sha: <sha-or-null>
checkpoint_sha: <sha-or-null>
native_goal_gate: PAUSED | IDLE_BY_TURN_BOUNDARY | UNVERIFIED
requires_review: false
review_request_id: <id-or-null>
reviewed_sha: <sha-or-null>
review_status: NOT_ASSESSED
marker_state: NONE
consumed_review_tuple: <tuple-or-null>
pending_review_transition: <null-or-{tuple, verdict, target_state}>
todoist_task_ids: []
state: ACTIVE
```

Never store prompts, transcripts, hidden reasoning, credentials, or mutable
raw scientific source in this record.

## Transitions

```text
ACTIVE -> CHECKPOINT_READY       final validation + checkpoint recorded
CHECKPOINT_READY -> STALLED_FOR_REVIEW  publication + exact readback complete
REVIEW_RECEIPT_APPLYING -> ACTIVE  CHANGES_REQUESTED transition committed
REVIEW_RECEIPT_APPLYING -> READY_FOR_PARENT  APPROVED transition committed
REVIEW_RECEIPT_APPLYING -> HUMAN_ESCALATION  human decision transition committed
STALLED_FOR_REVIEW -> ACTIVE     exact CHANGES_REQUESTED receipt
STALLED_FOR_REVIEW -> READY_FOR_PARENT  exact APPROVED receipt
STALLED_FOR_REVIEW -> HUMAN_ESCALATION  exact REQUIRES_HUMAN_DECISION receipt
STALLED_FOR_REVIEW -> WAIT       mismatch or unavailable evidence
READY_FOR_PARENT -> terminal handoff; no code mutation
```

`READY_FOR_PARENT` is not merge or acceptance. `WAIT` preserves the source
state until evidence or human action changes.

`STALLED_FOR_REVIEW` is valid only when `native_goal_gate` is `PAUSED` or
`IDLE_BY_TURN_BOUNDARY`; it is never native Goal `BLOCKED`. If the host cannot
prove either gate, keep `CHECKPOINT_READY` and do not publish an active review
marker; return `WAIT` with reason `GOAL_CONTINUATION_UNVERIFIED`.
`REVIEW_RECEIPT_APPLYING` is a recoverable local transaction state, not a new
review request.

## Profile input

The automation supplies the profile; never infer it from a path and never let
it expand authorization:

- `wiki`: preserve source/evidence provenance; no automatic scientific
  promotion.
- `workspace-tools`: stay inside the named capability; no research-evidence
  interpretation as a side effect.
- `research-projects`: preserve raw evidence; human scientific acceptance is
  required and missing acceptance remains `NOT_ASSESSED`.

The runtime preflight must verify the declared CWD and remote identity before
any mutation. Missing machine, project, network, or connector capability is
`RUNTIME_UNAVAILABLE`; another checkout is never an acceptable fallback.

## Idempotent publication

Reconcile in this order and stop at the first unknown result:

1. re-fetch all owning Issue/group members and base SHA; reject `STALE_SPEC`
   or `BASE_MOVED` before final validation or publication;
2. validate candidate and record `checkpoint_sha`;
3. verify intended branch and push only if allowed;
4. read back remote branch SHA;
5. find the owned Draft PR for the execution key, or create exactly one when
   none exists; an open unowned PR on the intended base/head is
   `LEGACY_PR_CONFLICT`;
6. read back PR number, base, draft state, and head SHA;
7. verify `native_goal_gate` is `PAUSED` or `IDLE_BY_TURN_BOUNDARY`, then
   write/replace the one literal marker block and reject duplicates;
8. read back marker and all four head values;
9. write `STALLED_FOR_REVIEW`.

If an operation may have succeeded but its result is unknown, query the remote
surface before retrying; never evade dedupe with a new identifier.

## Review tuple

The only consumable receipt binds the same observed revision to:

```text
(execution_key, pr_number, checkpoint_sha, review_request_id, reviewed_sha)
```

When using GitHub review APIs, anchor the review to
`commit_id=checkpoint_sha`. Verify the configured independent reviewer
identity, event, author, body tuple, reviewed SHA, and current PR HEAD before
consuming it. A producer-authored receipt is not independent. Persist the
exact tuple, verdict, and target state before deactivation in
`pending_review_transition`; after marker readback, atomically record the
consumed tuple, target state, and clear the pending field. A restart resumes
this transaction and never re-reviews the tuple. For `CHANGES_REQUESTED`, the
target is `ACTIVE`; for `APPROVED`, deactivate it with `state=READY_FOR_PARENT`;
for `REQUIRES_HUMAN_DECISION`, deactivate it and create the allowed
human-action projection without resuming code. Missing/stale receipts remain
`NOT_ASSESSED`.

An open PR on the intended base/head without the owned execution binding is
`LEGACY_PR_CONFLICT`: do not retrofit it or create a second PR; escalate.

## Receipt

```yaml
schema: ready-issue-executor/v1
execution_key: <key>
disposition: EXECUTED | NO_OP | WAIT | HUMAN_ESCALATION | AUTHORIZATION_REQUIRED
state: <state>
issue_numbers: [N]
pr_number: <N-or-null>
thread_id: <id-or-null>
goal_id: <id-or-null>
native_goal_gate: PAUSED | IDLE_BY_TURN_BOUNDARY | UNVERIFIED
heads:
  base_sha: <sha-or-null>
  local_head_sha: <sha-or-null>
  remote_head_sha: <sha-or-null>
  pr_head_sha: <sha-or-null>
  checkpoint_sha: <sha-or-null>
validation: PASS | FAIL | NOT_ASSESSED
review:
  request_id: <id-or-null>
  reviewed_sha: <sha-or-null>
  status: APPROVED | CHANGES_REQUESTED | REQUIRES_HUMAN_DECISION | NOT_ASSESSED
todoist:
  status: NOT_APPLICABLE | CREATED | UPDATED | UNCHANGED | FAILED
changed_paths: []
limitations: []
```

## Acceptance matrix

These are small deterministic protocol cases, not evidence of native runtime
execution. A future sandbox run must record observed traces and may not mark a
case `PASS` from prose alone.

| case | setup | expected disposition |
| --- | --- | --- |
| A1 | no exact `ready` Issue | `NO_OP` |
| A2 | first eligible Issue, empty binding | one thread, then one goal |
| A3 | crash at `CHECKPOINT_READY` | resume publication; no duplicate |
| A4 | marker write/readback failure | remain `CHECKPOINT_READY` |
| A5 | stalled checkpoint, no receipt | no mutation; `WAIT` |
| A6 | exact `CHANGES_REQUESTED` receipt | deactivate marker; same goal; `ACTIVE` |
| A7 | stale or mismatched SHA receipt | `NOT_ASSESSED`; no mutation |
| A8 | exact `APPROVED` receipt | deactivate marker; `READY_FOR_PARENT`; exactly one owned Todoist projection (created, updated, or unchanged) |
| A9 | crash after marker deactivation before ledger transition | resume `pending_review_transition`; consume once; target state committed |
| A10 | existing open legacy PR on intended base/head | `LEGACY_PR_CONFLICT`; no retrofit; no second PR; human escalation |
