---
kind: codex.session-artifact.v1
artifact: tasks
session_id: 20260829_athena-issue-61_001
status: needs_review
provenance: {source_commit: 831a599be646ffd41bda8daddf3d0b0934b76a27, observed_at: '2026-08-29T14:35:00+07:00', recorded_by: franky}
upstream: [plan.md]
downstream: []
---

# Tasks

- [x] Audit Issue #61 and canonical baseline.
- [x] Inspect overlapping review, security, and scientific skill content.
- [x] Implement Athena contracts, kernel, validator, fixtures, and skills.
- [x] Reconcile adapter/manifests and record upstream provenance.
- [x] Run local validation for the repaired strict contracts and commit the work unit.
- [x] Fresh independent Athena review completed against `85c02d522b64793a9957d691721a02a2a7b7c5e3`; result is `clear_for_parent_decision` with no findings.
- [ ] Parent opens one draft PR and runs hosted CI before merge.

Repair evidence: the strict executable validator now rejects undeclared request/result
fields and the fixture contains behavior-bearing assertions for all 20 required
cases. The latest repair evidence commit is
`85c02d522b64793a9957d691721a02a2a7b7c5e3`; independent review is recorded,
while publication remains pending.
