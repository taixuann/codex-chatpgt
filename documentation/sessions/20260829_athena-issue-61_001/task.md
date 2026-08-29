---
kind: codex.session-artifact.v1
artifact: tasks
session_id: 20260829_athena-issue-61_001
status: acceptance_ready
provenance: {source_commit: 911c243, observed_at: '2026-08-29T16:30:00+07:00', recorded_by: franky}
upstream: [plan.md]
downstream: []
---

# Tasks

- [x] Audit Issue #61 and canonical baseline.
- [x] Inspect overlapping review, security, and scientific skill content.
- [x] Implement Athena contracts, kernel, validator, fixtures, and skills.
- [x] Reconcile adapter/manifests and record upstream provenance.
- [x] Run local validation for the repaired strict contracts and commit the work unit.
- [x] Fresh independent Athena review completed against `dd51328814a61b0584282009803f5f1cbee88acd`; result is `clear_for_parent_decision` with no findings.
- [x] Parent opened PR #92 and hosted CI run #331 passed on final candidate `911c243`.

Repair evidence: the strict executable validator now rejects undeclared request/result
fields and the fixture contains behavior-bearing assertions for all 20 required
cases. Final candidate `911c243` has independent review
`dd51328814a61b0584282009803f5f1cbee88acd` and hosted CI run #331 recorded;
GitHub merge and scientific acceptance remain out of scope and pending parent
authorization.
