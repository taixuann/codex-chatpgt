---
id: AGENT-LIFECYCLE-HARDENING
status: accepted_deterministic_with_runtime_limits
updated: 2026-08-16
---

# Argus, Prometheus, and Athena hardening

## Athena review boundary (Issue #61)

Athena's formal interface is the thin `athena.review.v1` request and
`athena.review-result.v1` result validated by
`ops/scripts/validate_athena_review.py`. The visible review surface is
deliberately three packages: `independent-artifact-review` (implementation,
architecture, readiness), conditional `scientific-peer-review`, and
conditional `risk-security-review`. Shared procedure lives in
`skills/references/athena-review-kernel.md`; it is not a workflow engine.

The result is revision-bound, criterion-level, evidence-anchored, and may only
recommend a parent decision. Missing/stale evidence remains `not_assessed` or
`insufficient_evidence`. Mutation, criterion rewriting, repair, final
acceptance, recursive spawning, and policy promotion remain forbidden. Formal
review receives bounded fresh context rather than producer history; interactive
critique is a separate mode. External anchors and KEEP/ADAPT/REJECT decisions
are recorded in `skills/references/athena-upstream-adaptation-records.yaml`.

This control-plane slice keeps lifecycle execution in the existing task and
Franky contracts. `manifests/agent-contracts.yaml` is explicitly scoped to the
Argus/Prometheus/Athena shared lifecycle slice; it is not a global role
registry. `manifests/agent-capability-repertoires.yaml` records capability
eligibility and forbidden boundaries, not canonical role authority.

Canonical deployment role identity is separate: the external AI Labs registry
is used when available, while its absolute local path is runtime-only and the
portable semantic reference is `agents/AGENTS.md` plus
`AGENT-BOUNDARIES.md`. Local TOML files are adapters; the root `AGENTS.md` is
repository runtime policy; and documentation is explanatory. The four host
runtime limitations remain `NOT_ASSESSED`.

The shared envelopes are declared in
`ops/schemas/shared-contracts.schema.yaml`: `request.v1`, `context.v1`,
`handoff.v1`, `result.v1`, `review.v1`, and `run.v1`. Each carries provenance,
evidence, claims, unknowns, conflicts, readiness, and validation status.
Artifact states and authority fields are declared in
`ops/schemas/artifact-lifecycle.schema.yaml`.

`ops/scripts/validate_agent_lifecycle.py` is a deterministic evaluator only.
It rejects unsupported claims, missing provenance/evidence, same-agent
handoffs, unauthorized mutation, wrong capability use, incomplete closeout,
and direct artifact-to-state promotion. State promotion requires the ordered
chain `Evidence -> Claim -> Review -> Decision -> State`.

## Issue evidence map

| Issue | Evidence | Status |
| --- | --- | --- |
| #68 | Argus contract, registry entries, provenance/evidence checks, handoff negative case | PASS (deterministic) |
| #69 | Prometheus contract, quality/artifact capabilities, result/closeout checks | PASS (deterministic) |
| #70 | Athena contract, review/evidence capabilities, independent-review boundary | PASS (deterministic) |
| #61 | Thin Athena request/result contracts, bounded review skills, and evidence validator | Implemented on work-unit branch; independent review pending |
| #71 | Shared envelopes, artifact states, evidence chain, seven negative evaluator cases | PASS (deterministic) |

Host-mediated agent selection, native skill loading/model-mediated selection,
runtime mutation enforcement, and host permission enforcement remain
`NOT_ASSESSED`; this repository does not claim those from static contracts or
no-model tests.
