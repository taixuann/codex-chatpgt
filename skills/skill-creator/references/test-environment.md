# Test Environment

Owner: isolated trial lifecycle. Consumers: CREATE probe/evaluation and UPDATE U9. Persistence: raw runs and reports stay outside the runtime package. Non-overlap: issue-execution owns repository session state.

Allocate a temporary copy/worktree, prepare the exact candidate, run baseline before substantive updates, freeze raw events/snapshots, report compact evidence, archive only what is needed, and clean temporary state. Exclude runtime homes/caches from artifact snapshots. Preserve baseline purity and stop on orphaned worktrees, dirty overlap, unavailable auth, or ambiguous candidate identity.
