# Test Environment

Owner: isolated trial lifecycle. Consumers: CREATE probe/evaluation, INSTALL
materialization/real-task checks, and UPDATE U9. Persistence: raw runs and reports stay outside the runtime package.
Non-overlap: issue-execution owns repository session state.

## Trial lifecycle

```text
ALLOCATE → PREPARE → BASELINE → RUN → FREEZE EVIDENCE → REPORT → ARCHIVE → CLEAN
```

- `ALLOCATE`: choose a temporary copy, worktree, or sandbox and record why it fits the boundary.
- `PREPARE`: load the exact candidate, required instructions, dependencies, and fixture inputs.
- `BASELINE`: run the unchanged baseline before a substantive update and freeze its identity.
- `RUN`: execute the selected portfolio without repairing between individual cases. When intermediate state matters, finish each operation in a separate process and snapshot the workspace from the runner before continuing.
- `FREEZE EVIDENCE`: preserve raw events, ordered transition snapshots, candidate fingerprint, test fingerprint, and trial identity. Never treat model-authored snapshots as runner observations.
- `REPORT`: classify outcomes, artifacts, side effects, cost, and limitations.
- `ARCHIVE`: retain only the raw evidence and compact pointers required for review.
- `CLEAN`: remove temporary state only after evidence is frozen and no review hold applies.

Terminal cleanup states are explicit:

- `CLEANED`: temporary state was removed after evidence freeze;
- `PRESERVED_FOR_REVIEW`: state remains intentionally available for an active review;
- `CLEANUP_BLOCKED`: cleanup could not safely occur because of dirty overlap, ownership, or missing evidence.

Every trial records a fresh trial identity, exact candidate fingerprint, test
fingerprint, base identity when comparing, selected environment kind, and
runtime/auth status. Exclude runtime homes and caches from artifact snapshots.
Preserve baseline purity, do not reuse a dirty fixture, and stop on orphaned
worktrees, dirty overlap, unavailable auth, or ambiguous candidate identity.

## Environment selection and fingerprints

- Use a temporary copy when the trial must isolate ordinary files and the
  candidate can be materialized without Git history.
- Use a worktree when Git identity, tracked/untracked state, or exact revision
  comparison is part of the contract.
- Use a sandbox only when its filesystem and provider/auth capabilities are
  explicitly available; an unavailable sandbox is `NOT_ASSESSED`, not a
  successful empty trial.

At `PREPARE`, record the fresh trial ID, candidate revision/tree fingerprint,
test/case fingerprint, base revision for paired comparisons, environment kind,
and runtime/auth status. The before/after snapshot covers only the operation
workspace; temporary `CODEX_HOME`, caches, and disposable provider state are
excluded. Freeze these records before cleanup so a later report cannot silently
substitute a different candidate or test corpus.
