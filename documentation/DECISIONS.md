---
id: DECISIONS-CODEX-CONTROL-PLANE
status: active
updated: 2026-08-09
---

# Architecture decisions

## D-001 — Registry authority is separate from runtime adapters

The AI Labs registry defines the three canonical planning roles: Feynman,
Prometheus, and Franky. Argus and Athena may exist as bounded runtime support
adapters, but they are not additional canonical roles and must not acquire
independent workflow ownership.

## D-002 — Workflows follow lifecycle, not persona

Use shared task lifecycle workflows and conditional role routing. Do not create
one workflow per agent personality.

## D-003 — Agents, skills, and task contracts have separate jobs

- Agent: execution topology, permission boundary, and context isolation.
- Skill: reusable procedure and expertise.
- Workflow: ordered lifecycle and gates.
- Task contract: explicit glue between objective, scope, capabilities, output,
  validation, review, and stop conditions.

Do not create a new agent merely to represent domain expertise. Add or reuse a
skill and provide project context first.

## D-004 — Cloud handoff is a thin coordination layer

`CLOUD-BRIEF.md`, `CURRENT.md`, `DECISIONS.md`, plans, and handoffs provide
progressive disclosure for ChatGPT Cloud. They do not mirror project data or
replace local runtime authority.

## D-005 — Knowledge planes remain distinct

`AGENTS.md` governs behavior; `CURRENT.md` and `DECISIONS.md` hold accepted
state; agentmemory holds historical observations; Wiki holds compiled
knowledge; RAG/source corpora hold original evidence. Promotion is explicit:
`OBSERVE → PROPOSE → REVIEW → ACCEPT → UPDATE`.

## D-006 — Review is independent from execution

Deterministic validation and, where justified, an independent review remain
separate acceptance checks. A successful worker or passing command is not by
itself user or scientific acceptance.

## D-007 — General workflow semantics have one canonical human-readable source

`documentation/OPERATING-WORKFLOW.md` is the canonical human-readable
specification for the shared operating lifecycle across cloud reasoning,
GitHub coordination, local execution, validation, review, and durable state
updates.

`AGENTS.md` keeps concise runtime policy and boundaries. Machine-readable
workflow files are justified only when tooling consumes or enforces their
state, gates, routing, recovery, or validation semantics. Project workflows may
extend the general lifecycle only when a real project demonstrates materially
different states, ordering, domain steps, or validation gates.

Do not duplicate the full general workflow across persona-specific workflows,
skills, Issue templates, or project instructions.
