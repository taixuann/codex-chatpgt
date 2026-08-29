---
kind: codex.session-artifact.v1
artifact: tasks
session_id: 20260829_athena-issue-61_001
status: needs_review
provenance: {source_commit: a5c79e9f47ac4f6d5858d5fd2542b5ee1e82c937, observed_at: '2026-08-29T17:30:00+07:00', recorded_by: franky}
upstream: [plan.md]
downstream: []
---

# Tasks

- [x] Audit Issue #61 and canonical baseline.
- [x] Inspect overlapping review, security, and scientific skill content.
- [x] Implement Athena contracts, kernel, validator, fixtures, and skills.
- [x] Reconcile adapter/manifests and record upstream provenance.
- [x] Run local validation for the repaired strict contracts and commit the work unit.
- [x] Fresh independent Athena review refreshed against the reconciled candidate `a5c79e9f47ac4f6d5858d5fd2542b5ee1e82c937`; result is `clear_for_parent_decision` with no findings.
- [ ] Hosted CI rerun on the review-record candidate is pending after publication of this evidence.

Repair evidence: the strict executable validator now rejects undeclared request/result
fields and the fixture contains behavior-bearing assertions for all 20 required
cases. Candidate `a5c79e9…` has independent Athena review recorded; hosted CI
run #333 passed on its implementation predecessor `61f16a5…` and must be
rerun after this evidence publication;
GitHub merge remains pending the PR ready state; scientific acceptance remains
out of scope.
