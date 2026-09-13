# Coupled contracts

The three surfaces have one ownership boundary.

## Request

```yaml
version: 1
request_id: issue-<N>:<task>:attempt-<N>
authority: {repository: ..., issue: <N>, task: ...}
lane: execute | repair
repo: {root: ..., cwd: ..., worktree: ...}
scope: {allowed_paths: [...], mutation_boundary: ...}
session: {policy: fresh | resume | resume_or_start | rebind}
route_requirements:
  {semantic_route: economy | balanced | strong | strongest,
   semantic_complexity: ..., mutation_risk: ...,
   requested_model: ..., requested_effort: ...}
delegation:
  executor_profile: agy | prometheus | identity
  task_contract: {canonical bounded task contract}
permission_policy: read-only | bounded-write
expected_context: {required_skills: [...], instruction_fingerprint_expectation: ..., effective_context_fingerprint_expectation: <sha256>}
outputs: {registry: /absolute/session-registry.json, receipt: /absolute/receipt.yaml}
return_contract: normalized-runtime-receipt-v1
```

An AGY implementation request must include `delegation.executor_profile: agy`
and a canonical `task_contract`; the parent compiler renders it before worker
invocation and the worker binds the renderer fingerprint to the session and
receipt. A native Prometheus
fallback is parent-owned and uses the `prometheus` presentation without
entering this worker. `identity` is qualification-only.

If the parent returns a native Prometheus fallback result, every reported
`changed_paths` entry must also satisfy the original request's `allowed_paths`
scope. Path syntax validation alone is insufficient evidence of bounded
mutation.

The request contains execution facts and explicit harness-owned output paths
only. Output parents must already exist, cannot traverse symlinks, and cannot
be repository paths; the adapter also binds the actual Git worktree identity,
AGY options, and exact native session. The outer native sandbox and Git
reconciliation enforce the actual mutation boundary. It must not become a
second Issue body or acceptance ledger.

The task ledger carries trusted `repository` and numeric `issue` authority;
reconciliation consumes the matching preflight session and rejects a ledger
from another Issue. Ignored lifecycle state and `.git` metadata are runtime
state, not Issue-owned changed files. Bounded-write scopes must name concrete
relative files or subdirectories; `.` and `./` are rejected as whole-repository
allowances. Review evidence must bind to a result whose `stale` flag is
explicitly `false` before technical eligibility can be recorded. The local
kernel ends at `awaiting_parent_decision`; the host owns reviewer trust, parent
acceptance, and Draft PR publication. Detached Git worktrees are
represented explicitly, and sentinel native-session values are never
resumable.

Each task may retain at most eight compact execution attempts in `executions[]`.
Each entry records only actor/primitive, display label, attempt number, receipt
reference, result (`success`, `failed`, `unavailable`, `timed_out`, or
`not_assessed`), and deterministic validation state. A legacy singular
`execution` slot is rejected; this is bounded attempt history, not a transcript
or execution database.

Worker routing is explicitly two-stage. Stage 1 is always the requested AGY
attempt: an availability failure records `actual_worker: agy`,
`fallback_triggered: true`, its normalized `fallback_reason`, and
`fallback_required: prometheus`. Stage 1 never claims that Prometheus ran.
Only the parent/native host may return stage 2 with `actual_worker:
prometheus`, native-terminal provenance, and `native_prometheus_result` bound
to the parent request ID, Issue/repository/CWD/worktree, availability reason,
attempt, result status, changed paths, observed validation, and an `agy_failure`
record carrying the same request ID, AGY worker, availability error code, and
failed/timed-out status. Any non-AGY worker fallback shape is invalid.

For a provider run, the child receives a small runtime-specific environment
allowlist rather than the caller's complete environment. Existing runtime
directories may be declared through `HEADLESS_CLI_RUNTIME_WRITE_ROOTS`, and
`HEADLESS_CLI_ALLOW_NETWORK=1` is the explicit outbound-provider opt-in. Both
are outside the worktree and are bounded by the native macOS sandbox.

## Receipt

The adapter accepts runtime facts only from the documented AGY JSON result
envelope. The
receipt reports observed runtime facts: AGY-primary worker routing with
parent-owned Prometheus availability fallback decision, including
`fallback_required: prometheus`, `requested_worker`, `actual_worker`,
`fallback_triggered`, and `fallback_reason`, plus requested route and actual route,
requested/resolved profile, provider, actual model/effort, exact native session ID, session state,
executor provenance, canonical repo/CWD/worktree, permission observation,
process status, one normalized `error_code` for failures, context/skill
observation, usage/capacity, and limitations. Structured stdout/stderr is
bounded to a fixed receipt limit before parsing. A non-`UNKNOWN` capacity state
must identify an observed source; `source: none` can only remain `UNKNOWN`. It
must not contain claims such as `AC satisfied`, `review passed`,
`accepted_head`, or `final success`. The local eligibility transition does not
consume a parent envelope or reviewer-trust callback. A repository-
controlled event dictionary cannot unlock STOP or manufacture reviewer trust;
the host must perform those transitions after this kernel returns.

Preflight records NUL-delimited Git status records, including both sides of a
rename, so quoted paths and rename delimiters cannot change ownership checks.
Draft PR publication also rejects an `origin.pushurl` that resolves to a
different GitHub repository than `origin`.
The host owns the STOP/Draft PR transition; the repository kernel neither
creates nor consumes an acceptance event.

AGY is the only active native terminal lane in v1. Deferred providers are
outside this harness until they have a separately owned adapter and
qualification contract. The adapter normalizes only facts exposed by the
selected runtime; one-shot success with no native session remains
`NOT_ASSESSED`. It does not infer qualification from command acceptance.

The deferred OMP selector remains documentation-only as
`opencode-zen/muse-spark-1.3-contributor-free`; no OMP adapter or live
qualification is part of active v1.

The coupled local qualification loop ends at `awaiting_parent_decision`.
Parent acceptance, Draft PR publication, and STOP verification belong to the
external host boundary and are verified there rather than by this repository
kernel.

## Review packet/result

The packet binds Issue authority, accepted criteria, exact base/candidate,
changed files, validation, document impact, constraints, evidence, and
canonical repository/worktree identity. The packet also carries a workspace
fingerprint captured at the exact candidate snapshot. It covers regular-file
content and modes, directory modes, and symlink targets; the lifecycle state
directory is excluded. Acceptance recomputes this candidate fingerprint so a
review cannot be reused after an unreviewed workspace mutation. The preflight
baseline remains the separate guard for unexpected Git status changes. The
result keeps the axes separate:

```yaml
work_review: {status: pass | concerns | fail}
goal_review: {status: complete | partial | incomplete | insufficient_evidence}
```

Candidate, criteria, rubric, or evidence mutation invalidates the affected
review snapshot. Reviewer context is fresh/disposable and carries only a
host-observed, non-trusted native-session record. Executor continuity is exact
and resumable only after compatibility checks. The eligibility helper cannot
write accepted state; the trusted parent/host owns that decision outside the
repository kernel.

Child executors never commit. Task, repair, test, and tool completion do not
imply a commit; the parent owns commits and creates a candidate checkpoint only
after coherent validation, reconciliation, and review-boundary value exist.
Terminal history is deterministically classified as `semantic checkpoint`,
`repair checkpoint`, `authority/config reconciliation`, or `history noise`.
Overlapping consecutive noise commits fail terminal hygiene. Short-horizon
state stays in the compact session/task pointers rather than a commit registry
or transcript archive. A material repair may create one new candidate
checkpoint, followed by fresh exact-head review; do not rewrite history after
the final review begins.

Known normalized failure classes include `ISSUE_AUTHORITY_INVALID`,
`STALE_BASE`, `DIRTY_BASELINE_CONFLICT`, `RUNTIME_UNAVAILABLE`,
`MODEL_ROUTE_UNAVAILABLE`, `AUTH_REQUIRED`, `CAPACITY_UNKNOWN`,
`CAPACITY_LOW`, `QUOTA_EXHAUSTED`, `RATE_LIMITED`, `SESSION_INVALID`,
`SESSION_CONTEXT_MISMATCH`, `CONTEXT_CONTRACT_UNVERIFIED`,
`REQUIRED_SKILL_UNAVAILABLE`, `PERMISSION_NOT_ASSESSED`, `PERMISSION_DENIED`,
`STRUCTURED_RESULT_INVALID`, `TIMED_OUT`, `EXECUTION_FAILED`,
`MUTATION_SCOPE_VIOLATION`, `GIT_RECONCILIATION_FAILED`, `VALIDATION_FAILED`,
`REVIEW_NOT_REVIEWABLE`, `REVIEW_INSUFFICIENT_EVIDENCE`, `REVIEW_STALE`,
`PARENT_ACCEPTANCE_REQUIRED`, `OSCILLATING`, and `BUDGET_EXHAUSTED`.
