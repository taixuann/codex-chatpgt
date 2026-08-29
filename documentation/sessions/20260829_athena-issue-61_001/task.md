---
kind: codex.session-artifact.v1
artifact: tasks
session_id: 20260829_athena-issue-61_001
status: needs_review
provenance: {source_commit: c6e0a1c80dd5c27ae940bf7d09203e34d0215f8f, observed_at: '2026-08-29T14:20:00+07:00', recorded_by: franky}
upstream: [plan.md]
downstream: []
---

# Tasks

- [x] Audit Issue #61 and canonical baseline.
- [x] Inspect overlapping review, security, and scientific skill content.
- [x] Implement Athena contracts, kernel, validator, fixtures, and skills.
- [x] Reconcile adapter/manifests and record upstream provenance.
- [x] Run local validation for the repaired strict contracts and commit the work unit.
- [ ] Parent opens one draft PR and obtains fresh independent Athena review.

Repair evidence: the strict executable validator now rejects undeclared request/result
fields and the fixture contains behavior-bearing assertions for all 20 required
cases. The latest repair evidence commit is
`c6e0a1c80dd5c27ae940bf7d09203e34d0215f8f`; independent review and publication
remain pending.
