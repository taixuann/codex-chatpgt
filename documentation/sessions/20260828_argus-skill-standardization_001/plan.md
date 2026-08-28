---
kind: codex.session-artifact.v1
artifact: plan
session_id: 20260828_argus-skill-standardization_001
status: in_progress
provenance: {source_commit: 8ed22d5ba77732d72f4d094a2312dcaf8448c3b7, observed_at: '2026-08-28T08:45:00+07:00', recorded_by: franky}
upstream: [context.md, spec.md]
downstream: [task.md, franky.ticket.yaml]
---

# Plan

1. Audit overlapping skills and upstream provenance.
2. Add one internal reconnaissance kernel and three narrow Argus profiles.
3. Reconcile Argus adapter, manifests, catalog, and allowlist without adding
   agent skill-hint fields or a second lifecycle subsystem.
4. Run structural, contract, routing, packet, and focused tests; retain
   runtime limitations as `NOT_ASSESSED`.
5. Hand off for independent Athena challenge review and parent acceptance.
