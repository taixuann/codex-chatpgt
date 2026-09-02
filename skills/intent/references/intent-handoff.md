# Intent handoff

For focused/deep or otherwise non-trivial intent, call the shared
`session-packet-management` capability. Keep only minimum sufficient resolved
context, canonical pointers, decisions, unknowns, orientation, and trust
signals. Do not copy raw inspected files or research dumps.

All repositories use `<repository-root>/.agents/sessions/<session-id>/` for new
live packets. Existing `documentation/sessions/**` material is legacy history
only. The packet is a bounded envelope, not canonical authority. The handoff
must expose:
`freshness`, `completeness`, `integrity`, `scope_match`, and
`evidence_traceability`.
