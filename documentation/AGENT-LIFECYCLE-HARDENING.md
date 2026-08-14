---
id: AGENT-LIFECYCLE-HARDENING
status: conditionally-validated
updated: 2026-08-14
---

# Argus, Prometheus, and Athena hardening

This control-plane slice keeps lifecycle execution in the existing task and
Franky contracts. `manifests/agent-contracts.yaml` is the single semantic
registry for the three support/implementation/review boundaries, while
`manifests/agent-capability-repertoires.yaml` is the single capability list.

Canonical role authority is separate: the AI Labs role registry and canonical
definitions own Feynman, Prometheus, and Franky; local TOML files are adapters;
the root `AGENTS.md` is repository runtime policy; and documentation is
explanatory. See [`AGENT-BOUNDARIES.md`](AGENT-BOUNDARIES.md) for the call
boundary and the four runtime limitations that remain `NOT_ASSESSED`.

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
| #71 | Shared envelopes, artifact states, evidence chain, seven negative evaluator cases | PASS (deterministic) |

Host-mediated agent selection, model behavior, native skill loading, and
runtime mutation enforcement remain `NOT_ASSESSED`; this repository does not
claim those from static contracts or no-model tests.
