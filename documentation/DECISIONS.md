---
id: DECISIONS-CODEX-CONTROL-PLANE
status: active
updated: 2026-08-16
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

## D-010 — Runtime catalog evidence is conditional, not semantic authority

The 2026-08-10 Codex/OpenCode probes are accepted as runtime catalog evidence
only. Codex exposed 86 entries / 58 unique public names with duplicate-name
groups; OpenCode exposed 89 effective entries / 89 unique IDs. OpenCode's
read-only synthetic probe confirmed configured-path discovery and
project-local shadowing for a colliding ID; toggling external-skill scan flags
kept the ID count stable while changing the source root for nine entries.

These observations inform routing and overlay audits but do not establish
model-mediated activation, permission enforcement, or cross-runtime behavioral
equivalence. The OpenCode overlay also retains external workflow-manager and
install-workflow entries outside this repository's allowlist; this is an
explicit #12 portability/ownership boundary, not a permission to mutate that
external control plane. Those gates remain `NOT_ASSESSED`/conditional under
#38 and #35.

The deterministic skill-interface validator now resolves the Git-tracked
package surface and validates all 10 tracked packages; ignored personal or
plugin overlays are excluded. A disposable Codex fixture also demonstrated
project-local activation, sibling selection, and a clear arithmetic negative,
but this bounded evidence does not establish catalog-wide activation or
real-skill utility lift.

## D-011 — Skill admission is explicit and utility-gated (Issue #50)

`manifests/skill-catalog.yaml` is the checked-in reconciliation of the live
tracked skill surface. Every tracked package has exactly one disposition:
`KEEP`, `ADAPT`, `EXPLICIT_ONLY`, `REFERENCE_ONLY`, `MERGE`, or `RETIRE`.
Only `KEEP` packages with repository-grounded capability/utility evidence may
appear in `canonical_active`; local overlays and vendor/reference roots are
listed separately and are not silently promoted.

The deterministic catalog validator is a CI gate. It checks completeness,
duplicate ownership, canonical admission, evidence paths, and explicit
`NOT_ASSESSED` limitations. Structural/package validation remains necessary
but is not sufficient to claim utility or model-mediated routing behavior.
Issue/PLAN and `OPERATING-WORKFLOW.md` remain semantic authority; the catalog
does not create a routing service, workflow engine, or persona-owned skill
namespace.

## D-012 — Canonical-main reconciliation before behavioral admission

Issue #35's integration dependency is accepted. PR #53 reconciled the validated
`codex/system-skill-consolidation` branch into `main` with merge commit
`e1e05c096bb0912a9a3759f349ad97e3a5424e7d`; canonical-main control-plane
validation run #163 passed. The reconciled `main` retains the independent
planning commit and verifies 50 catalogued dispositions, six canonical active
capabilities, and explicit noncanonical overlay boundaries.

The separate behavioral phase remains owned by #38. No model-mediated routing,
WITH/WITHOUT utility lift, or cross-runtime equivalence is inferred from this
reconciliation. Antigravity migration remains outside scope.
## D-013 — Issue #57 hardens Franky evidence without adding a workflow engine

The #57 audit keeps `franky.task.v1` and `franky.result.v1` as bounded
invocation contracts. The result may carry one ordered evidence record for
`REQUEST` through `ACCEPTANCE_READY`, but it does not execute transitions,
persist workflow state, or replace the shared operating lifecycle. Consequential
results must identify a primary capability, impact-triggered supporting
capability, lifecycle closeout, closure evidence, and a non-self review PASS.
`acceptance_ready` remains parent/reviewer evidence, never final acceptance.
The task contract also carries a version compatibility declaration and a
machine-checkable Franky authority matrix. Each result evidence item records
source state, commit, timestamp, and result; freshness flags invalidate an
acceptance claim after later mutation. Routing includes a reason for the
primary, supporting, and lifecycle capabilities, and runtime evidence remains
split across configuration, dispatch, skill loading, and mutation enforcement.
When native skill loading is unavailable, the task packet is the tested
fallback materialization path. Review records declare both scope and
not-reviewed runtime behavior; evolution records explicitly say whether a
promotion candidate exists.
The checked-in example uses `source_commit: HEAD`; the validator resolves that
reference and requires a clean checkout for an acceptance-ready claim.

## D-014 — External role registry is a deployment dependency, not portable repository authority

The external AI Labs registry supplies canonical role identity when the
deployment runtime is connected. Its absolute local path is runtime-only and
must not be treated as portable repository state. `agents/AGENTS.md` and
`documentation/AGENT-BOUNDARIES.md` provide the repository's portable semantic
reference; `agents/*.toml` remain adapters. A conflict is escalated rather than
resolved by silently promoting a local adapter or manifest.

## D-015 — Shared lifecycle contracts are explicitly scoped

`manifests/agent-contracts.yaml` is the
`argus_prometheus_athena_shared_lifecycle_slice` contract registry. It covers
shared evidence, artifact, and lifecycle boundaries only. It is not a global
role registry and does not duplicate the richer Franky contracts or define the
canonical Feynman role.

## D-016 — Operation Workflow v1 remains Issue-first and PLAN-conditional

The shared operating lifecycle uses the smallest durable GitHub surface that
matches the work: an execution-ready repository work unit becomes an Issue, a
PLAN is retained when the work is consequential, one branch carries one work
unit and its PR, CI and review provide evidence, and merge is followed by `CURRENT.md`/
`DECISIONS.md` reconciliation. A mandatory GOAL/PLAN/session database or
separate workflow engine is not part of this contract. Full operational and
approval acceptance remains open under #62 and #60; static documentation does
not establish native host dispatch, skill loading, mutation, or permission
enforcement.

## D-017 — Role boundaries remain distinct during lifecycle stabilization

Feynman owns scientific reasoning, evidence calibration, and methodology
critique. Argus owns context and provenance preparation. Prometheus owns
bounded execution and tooling validation. Athena owns independent review.
Human authority remains final for scientific and repository acceptance. These
boundaries do not grant any role native dispatch, skill loading, mutation, or
permission enforcement.
## D-018 — Feynman v1 boundary is accepted without runtime overclaim

The bounded Feynman v1 slice is accepted after codex-chatpgt PR #76 and the
selected-project binding in research-projects PR #22. Feynman owns scientific
reasoning, evidence calibration, hypothesis/method critique, and bounded
scientific communication intent. Argus owns context and provenance
preparation; Prometheus owns implementation and execution; Athena owns
independent review; and the human owner remains final scientific authority.

The three reusable scientific procedures remain `ADAPT` candidates rather than
canonical `KEEP` skills. Scientific Wiki remains an on-demand evidence
capability owned by Issue #7; Personal Wiki is a reusable context plane whose
runtime is not yet assessed. No automatic Personal Wiki synchronization,
bidirectional mutation, knowledge graph/database, or Scientific Wiki
replacement is introduced. Native dispatch, skill materialization/runtime,
host mutation/permission enforcement, and human scientific acceptance remain
`NOT_ASSESSED`.

Future Personal Wiki MCP work, if separately authorized, may provide reusable
personal scientific context for the Feynman context plane, knowledge retrieval,
and promotion proposals. It does not include automatic synchronization,
bidirectional mutation, a knowledge graph/database, or replacement of the
Scientific Wiki capability.

## D-019 — Merge readiness requires current review, decision, and authorization

CI success and executor completion are evidence inputs, not acceptance. A
merge-readiness record must carry explicit review, decision, and authorization
outcomes bound to the current head and bounded artifact/action/scope/evidence
snapshot. `APPROVED`, `REJECTED`, and `CHANGES_REQUESTED` remain distinct
review/decision outcomes. Human decisions require reviewer, reason, timestamp,
revision, and an ordered decision history whose current entry matches the
active decision. Material unresolved findings block readiness unless an
authorized human waiver records both the authority and rationale. This is a
deterministic evaluator boundary, not a new workflow or approval platform;
native host merge enforcement remains `NOT_ASSESSED`.
