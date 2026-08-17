---
id: PLAN-ARW-RUNTIME-MATERIALIZATION-V1-20260816-001
status: active
updated: 2026-08-16
owner: Prometheus
issue: "#56"
---

# Runtime Materialization v1

## Objective

Produce the smallest observable proof that one named agent contract can load a
declared skill contract, execute one bounded task, emit an artifact, and pass
deterministic validation.

## Current gap

Repository contracts, adapters, capability repertoires, task packets, and
deterministic evaluators exist. The installed host currently exposes only
configuration parsing; native agent dispatch, skill loading, and host mutation
enforcement are not observable.

## Scope

- One existing named agent and one existing reusable skill.
- One read-only or explicitly mutation-authorized bounded task.
- One machine-readable task/result or artifact packet with provenance.
- One deterministic validator and one negative authority case.
- Evidence captured in the owning Issue/PR, not a new runtime database.

## Non-goals

- No orchestration engine, model router, autonomous-agent framework, or new
  agent.
- No new skill family or global policy.
- No scientific interpretation, research-project mutation, or MCP runtime.
- No claim that static contracts prove native host behavior.

## Architecture boundary

The host remains responsible for actual agent/thread dispatch and skill loading.
The repository owns semantic contracts, capability eligibility, bounded task
packets, artifact provenance, and deterministic validation. If the host does
not expose a required trace, record `NOT_ASSESSED` and stop rather than
simulating runtime behavior in repository code.

## Artifact I/O

Input:

- named agent contract;
- selected skill contract;
- explicit task objective, scope, authority, and stop conditions.

Output:

- result/artifact packet with producer, provenance, evidence, validation status,
  and mutation outcome;
- negative-case record when authority or scope is invalid.

## Validation

- Validate the agent adapter and skill interface.
- Validate the task/result or lifecycle envelope.
- Run the bounded execution fixture and negative authority case.
- Capture host configuration, dispatch, skill-loading, and mutation statuses
  separately; do not collapse `NOT_ASSESSED` into PASS.
- Require clean diff and focused tests.

## Acceptance criteria

- One agent contract resolves to one declared skill contract.
- One bounded execution produces a provenance-bearing artifact.
- The artifact passes deterministic validation.
- An unauthorized or out-of-scope execution is rejected.
- Evidence identifies exactly which runtime stages are observed and which remain
  `NOT_ASSESSED`.
- No new architecture or global policy is introduced.

## Risks

- Host traces may not expose dispatch or skill loading.
- A passing contract oracle may be mistaken for native runtime proof.
- Mutation tests may validate repository policy without proving host permissions.
- Provider/runtime availability may block a repeatable execution.

## Proof result

The deterministic slice now resolves `franky` with the canonical
`control-plane-audit` skill, executes only the supported `audit` boundary, and
emits a `VALIDATED` artifact with request identity, agent/skill identity,
provenance, lifecycle state, validation result, and explicit
`DRAFT->VALIDATED` transition evidence. A mutation request with `mutate: false`
emits `REJECT`; invalid actions, mismatched input identity, malformed
permissions, invalid skills, missing provenance, and illegal artifact
transitions are covered by focused tests.

This is repository-level policy and artifact proof only. It does not prove
native host dispatch, native skill loading, or host OS permission enforcement.

## Exit state

If all observable stages pass, update #56 and `CURRENT.md` with the exact
evidence. Otherwise retain #56 as open with a stage-specific `NOT_ASSESSED`
record and do not claim Runtime Materialization v1 complete.
