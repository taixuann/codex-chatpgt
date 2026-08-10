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

## D-008 — Quality-hardening baseline (Issue #24, superseded by #35)

The 2026-08-09 baseline kept eleven packages. That historical disposition is
retained for provenance but is superseded for current routing by D-009 after
the #38 creator gate and #35 workflow-consumer audit.

| Skill | Existence | Name | Boundary/neighbor decision |
| --- | --- | --- | --- |
| `project-bootstrap` | KEEP | KEEP NAME | distinct from guidance-only and link-only work |
| `install-project-link` | KEEP | KEEP NAME | safety-critical link operation with a named Franky branch |
| `external-handoff` | KEEP | KEEP NAME | cross-runtime approval/rollback procedure; ordinary task packets remain separate |
| `franky-agent-installer` | KEEP | KEEP NAME | Franky runtime-adapter permission boundary |
| `franky-cron-installer` | KEEP | KEEP NAME | governed scheduler lifecycle and overlap checks |
| `franky-guidance-manager` | KEEP | KEEP NAME | scoped instruction locality and precedence |
| `franky-maintenance` | KEEP | KEEP NAME | control-plane audit plus approved repair, not project work |
| `franky-promotion` | KEEP | KEEP NAME | explicit Codex-to-AI-Labs export boundary |
| `franky-source-migration` | KEEP | KEEP NAME | external-tool source boundary and collision review |
| `franky-workflow-organizer` | KEEP | KEEP NAME | persisted workflow design judgment; validator remains deterministic helper |
| `shared-session-closeout` | KEEP | KEEP NAME | role-neutral durable session-state procedure |

The static contrastive fixture at
`skills/franky-maintenance/scripts/fixtures/skill-routing.yaml` covers
positive, negative, nearest-neighbor, expected-none, and ambiguous cases. It
is metadata/fixture evidence only; this repository does not claim to observe
LLM skill selection when the active runtime does not expose that behavior.

## D-009 — Creator-gated system-skill and workflow reconciliation (Issue #35)

The installed Codex/OpenAI creator is the canonical admission baseline. No
new skill is admitted without a necessity, provenance, trigger, runtime-fit,
and proportional outcome decision. The current package dispositions are:

| Package | Current disposition |
| --- | --- |
| `external-handoff` | KEEP |
| `franky-agent-installer` | GENERALIZE as `runtime-adapter-management` |
| `franky-cron-installer` | MOVE_ON_DEMAND |
| `franky-guidance-manager` | GENERALIZE as `instruction-maintenance` |
| `franky-maintenance` | GENERALIZE as `control-plane-audit` |
| `franky-promotion` | MOVE_ON_DEMAND / DEFER under #12 |
| `franky-source-migration` | MOVE_ON_DEMAND / DEFER under #12 |
| `franky-workflow-organizer` | RETIRE |
| `install-project-link` | MOVE_ON_DEMAND |
| `project-bootstrap` | KEEP |
| `shared-session-closeout` | GENERALIZE / KEEP |

All seventeen `workflows/franky/**` YAMLs are retired because no named
dispatcher, persisted state, recovery/resume implementation, or independent
consumer was found. `workflows/AGENTS.md` remains the admission policy for a
future real machine workflow. Issue/PLAN/task contracts and retained skills
are the active routing surface; no replacement workflow engine is introduced.
