---
kind: codex.session-artifact.v1
artifact: tasks
session_id: 20260829_athena-issue-61_001
status: needs_review
provenance: {source_commit: 61f16a596a9da7b58f3d72b907ceb514bd464775, observed_at: '2026-08-29T17:00:00+07:00', recorded_by: franky}
upstream: [plan.md]
downstream: []
---

# Tasks

- [x] Audit Issue #61 and canonical baseline.
- [x] Inspect overlapping review, security, and scientific skill content.
- [x] Implement Athena contracts, kernel, validator, fixtures, and skills.
- [x] Reconcile adapter/manifests and record upstream provenance.
- [x] Run local validation for the repaired strict contracts and commit the work unit.
- [ ] Fresh independent Athena review refreshed against the reconciled candidate `61f16a596a9da7b58f3d72b907ceb514bd464775`.
- [x] Parent opened PR #92 and hosted CI run #333 passed on candidate `61f16a5…`.

Repair evidence: the strict executable validator now rejects undeclared request/result
fields and the fixture contains behavior-bearing assertions for all 20 required
cases. Candidate `61f16a5…` has hosted CI run #333 recorded; the prior review
`dd51328814a61b0584282009803f5f1cbee88acd` is retained as historical evidence
but is stale for acceptance of this reconciled candidate;
GitHub merge remains pending the PR ready state; scientific acceptance remains
out of scope.
