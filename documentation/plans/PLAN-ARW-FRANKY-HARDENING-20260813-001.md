---
id: PLAN-ARW-FRANKY-HARDENING-20260813-001
issue: 57
status: conditional-pass-pending-pr-ci-acceptance
updated: 2026-08-13
owner: parent-control-plane
---

# Issue #57 — Franky agent-first lifecycle hardening audit

## Audit objective

Audit the Issue #56 implementation as a separate proof/correctness unit. Keep
`franky.task.v1` and `franky.result.v1` thin bounded invocation contracts while
proving lifecycle evidence, capability composition, acceptance authority, and
runtime limitations end to end.

No router service, catch-all Franky skill, duplicate agent, recursive
delegation, or second workflow engine is introduced.

## Required evidence model

```text
REQUEST → CONTRACT → ADMISSION → ROUTING → IMPACT → EXECUTION
         → VALIDATION → CLOSURE → ACCEPTANCE READY
```

The result carries one ordered evidence envelope with source references. It
does not execute transitions, persist workflow state, or make a worker claim
advance state without evidence. A consequential result must identify:

- one primary capability declared by the task;
- only impact-triggered supporting capabilities declared by the task;
- `shared-session-closeout` as lifecycle capability;
- impact evidence and closure dispositions;
- a completed non-self review PASS before `acceptance_ready`.

The parent or independent reviewer retains final acceptance and durable-state
authority.

## Runtime evidence boundary

The installed Codex probe reports independently:

- configuration parsing;
- native/actual dispatch observation;
- `skills.config` behavior;
- mutation-escalation enforcement.

Parsing `skills.config` is not runtime behavior. The current live model probe is
expected to remain `NOT_ASSESSED`/`BLOCKED` if network access prevents a
completed observable turn. Contract-level mutation authority is deterministic;
host permission enforcement remains separate evidence.

## Closure matrix

| Surface | Disposition | Evidence |
| --- | --- | --- |
| Task contract objective/scope/authority | UPDATED | `ops/schemas/franky-task.schema.yaml` |
| Done criteria and stop conditions | UPDATED | task schema/example |
| Thin result/evidence status | UPDATED | `ops/schemas/franky-result.schema.yaml` |
| Ordered lifecycle evidence | UPDATED | result schema/example and validator |
| Primary/supporting/lifecycle routing | UPDATED | repertoire, evaluator, validator, fixture |
| Impact discovery evidence | UPDATED | result routing and control-plane audit skill |
| Acceptance authority | UPDATED | Franky adapter, result validator, negative tests |
| Issue #38 skill ownership | UNCHANGED_VALID | skill catalog/evidence and D-009/D-012 |
| Runtime parsing | UPDATED | `probe_codex_agent_runtime.py`, CI parser step |
| Actual dispatch behavior | NOT_ASSESSED | no completed observable child-agent trace |
| `skills.config` behavior | NOT_ASSESSED | parser is not behavior proof |
| Host mutation escalation | NOT_ASSESSED | contract gate is proven; host enforcement unavailable |
| Canonical docs and references | UPDATED | `AGENTS.md`, `CURRENT.md`, `DECISIONS.md`, workflow docs |
| Independent review | UPDATED | Athena final read-only re-review: conditional pass; no remaining High/Medium/Low findings |
| PR acceptance evidence | PENDING | #57 follow-up branch/PR and hosted CI still required |

## Validation commands

- `python ops/scripts/validate_franky_contracts.py`
- `python ops/scripts/evaluate_franky_agent.py ops/scripts/fixtures/franky-agent-evaluation.yaml`
- `python ops/scripts/probe_codex_agent_runtime.py`
- `PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s ops/scripts/tests -v`
- all retained agent adapter validators
- catalog, evidence, routing, skill-quality, control-plane, and CI-equivalent gates
- stale-reference and boundary searches
- independent read-only review of the implementation diff

## Stop conditions

Stop and report `blocked` or `escalated` when mutation authority, required
runtime evidence, independent review, or canonical-state reconciliation is
missing. Do not convert a parser pass, worker claim, or green narrow test into
final acceptance.
