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
requires_review: false
review_request_id: <id-or-null>
reviewed_sha: <sha-or-null>
review_status: NOT_ASSESSED
marker_state: NONE
consumed_review_tuple: <tuple-or-null>
todoist_task_ids: []
state: ACTIVE
```

Never store prompts, transcripts, hidden reasoning, credentials, or mutable
raw scientific source in this record.

## Transitions

```text
ACTIVE -> CHECKPOINT_READY       final validation + checkpoint recorded
CHECKPOINT_READY -> STALLED_FOR_REVIEW  publication + exact readback complete
STALLED_FOR_REVIEW -> ACTIVE     exact CHANGES_REQUESTED receipt
STALLED_FOR_REVIEW -> READY_FOR_PARENT  exact APPROVED receipt
STALLED_FOR_REVIEW -> WAIT       mismatch or unavailable evidence
READY_FOR_PARENT -> terminal handoff; no code mutation
```

`READY_FOR_PARENT` is not merge or acceptance. `WAIT` preserves the source
state until evidence or human action changes.

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

1. validate candidate and record `checkpoint_sha`;
2. verify intended branch and push only if allowed;
3. read back remote branch SHA;
4. find or create exactly one Draft PR for the execution key;
5. read back PR number, base, draft state, and head SHA;
6. write/replace the one literal marker block and reject duplicates;
7. read back marker and all four head values;
8. write `STALLED_FOR_REVIEW`.

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
consuming it. A producer-authored receipt is not independent. Missing/stale
receipts remain `NOT_ASSESSED`.

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
  status: APPROVED | CHANGES_REQUESTED | NOT_ASSESSED
todoist:
  status: NOT_APPLICABLE | CREATED | UPDATED | UNCHANGED | FAILED
changed_paths: []
limitations: []
```
