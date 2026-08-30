---
id: CURRENT-CODEX-CONTROL-PLANE
status: active
updated: 2026-08-16
---

# Current state

## Scope

This repository is the Codex-first control plane and cloud coordination bridge. It is deliberately separate from research-project contents.

## Canonical role authority

The external AI Labs registry supplies deployment role identity when available;
its absolute local path is runtime-only. The portable repository semantic
reference is `agents/AGENTS.md` and `AGENT-BOUNDARIES.md`. Exactly three
canonical planning roles remain:

| Role | Ownership | Adapter |
| --- | --- | --- |
| Feynman | scientific evidence, methodology, and protocol review | `agents/feynman.toml` |
| Prometheus | implementation design, code review, testing, and execution handoff | `agents/prometheus.toml` |
| Franky | workflow routing, registry/platform maintenance, and control plane | `agents/franky.toml` |

`Argus` and `Athena` are non-canonical read-only support adapters. They are bounded leaf workers and do not alter the role registry:

- Argus: internal repository/context exploration.
- Athena: independent review and critique.

## Stabilized control-plane foundation

The shared Argus/Prometheus/Athena hardening surface is now represented by
`manifests/agent-contracts.yaml`, the existing capability repertoire, and the
non-routing evaluator `ops/scripts/validate_agent_lifecycle.py`. The six
versioned envelopes (`request.v1`, `context.v1`, `handoff.v1`, `result.v1`,
`review.v1`, and `run.v1`) require provenance, evidence, claims, unknowns,
conflicts, readiness, and validation status. Artifact promotion is accepted
only through Evidence -> Claim -> Review -> Decision -> State; direct
artifact-to-state promotion is rejected. Native host agent selection/dispatch,
native skill loading/model-mediated selection, runtime mutation enforcement,
and host permission enforcement remain `NOT_ASSESSED`; runtime evidence for a
complete end-to-end workflow remains pending.

## Documentation ownership map

| Document | Classification | Authority |
| --- | --- | --- |
| `CURRENT.md` | CANONICAL | accepted current repository state |
| `DECISIONS.md` | CANONICAL | accepted architecture decisions |
| `OPERATING-WORKFLOW.md` | CANONICAL | shared lifecycle semantics |
| `AGENT-LIFECYCLE-HARDENING.md` | HISTORICAL_SUPPORT | merged lifecycle evidence and limitations |
| `CLOUD-BRIEF.md` | CANONICAL | progressive-disclosure cloud entrypoint |
| `GOAL-PLAN-GRAPH.md` | PROPOSED_UNDER_PROOF | proof tracked by Issue #17 |
| `RESEARCH-KNOWLEDGE-WORKFLOW.md` | SUPERSEDED_SUPPORT | full research/knowledge proof is now scoped under Issue #75 |
| `SYSTEM-EVOLUTION-WORKFLOW.md` | ACCEPTED | v1 evidence reconciled through PRs #18, #72, #82, and #84 |

No document in this map overrides the authority order in `AGENTS.md`; no
redundant document was removed in this reconciliation.

- Runtime guidance and bounded delegation policy: [`AGENTS.md`](../AGENTS.md).
- Local cross-workspace discovery: when present, the ignored
  `$CODEX_HOME/ENVIRONMENT.md` map is read during fresh non-trivial orientation
  before capability routing. It names local availability and owner entrypoints
  only; it is neither portable control-plane state nor authority over external
  workspaces.
- Canonical human-readable general lifecycle: [`OPERATING-WORKFLOW.md`](OPERATING-WORKFLOW.md).
- Architecture decisions: [`DECISIONS.md`](DECISIONS.md).
- Cloud progressive-disclosure entrypoint: [`CLOUD-BRIEF.md`](CLOUD-BRIEF.md).
- Runtime adapter contracts: [`agents/AGENTS.md`](../agents/AGENTS.md).
- Canonical role call boundaries and explicit runtime limitations:
  [`AGENT-BOUNDARIES.md`](AGENT-BOUNDARIES.md).
- Active skill surface: [`../skills/`](../skills/); workflow admission policy is
  documented in [`../AGENTS.md`](../AGENTS.md). The unconsumed Franky
  machine-workflow tree and `franky-workflow-organizer` package are retired and
  no longer discoverable.
- Canonical task contract: [`../ops/schemas/task-contract.schema.yaml`](../ops/schemas/task-contract.schema.yaml); ordinary control-plane routing uses Issue/PLAN/task contracts rather than a machine workflow tree.
- Historical change/audit evidence: [`../ops/changes/`](../ops/changes/). New ordinary work does not create a CHG wrapper unless a named consumer requires one.
- Deterministic repository CI: [`../.github/workflows/franky-validate.yml`](../.github/workflows/franky-validate.yml), accepted through PR #18 and retained after #35 reconciliation. It validates active agents, skills, task contracts, schedulers, focused tests, routing fixtures, context packets, audit records, and the Git allowlist; no retired workflow tree is treated as runtime authority.
- The canonical task-contract schema is checked by
  [`../ops/scripts/validate_task_contract.py`](../ops/scripts/validate_task_contract.py)
  against the checked-in example under `ops/schemas/examples/` and by focused
  unit tests.

The shared operating lifecycle remains capability-first, bounded, validation-oriented, and review-selective. `OPERATING-WORKFLOW.md` is the human-readable semantic source; machine-readable workflows are justified only when runtime state/gate enforcement adds value.

## Proposed semantic surfaces under proof

The following documents exist as proposed shared semantics and are **not yet accepted runtime truth merely because they are documented**:

- [`SYSTEM-EVOLUTION-WORKFLOW.md`](SYSTEM-EVOLUTION-WORKFLOW.md) — accepted System Configuration and Change workflow v1.
- [`RESEARCH-KNOWLEDGE-WORKFLOW.md`](RESEARCH-KNOWLEDGE-WORKFLOW.md) — historical research/knowledge workflow support; Issue #16 is superseded by #75.
- [`GOAL-PLAN-GRAPH.md`](GOAL-PLAN-GRAPH.md) — Goal–Plan linking semantics; minimal proof tracked by #17.

Ownership boundaries currently intended for proof:

- #15 owns **how bounded system changes are handled**.
- #11 owns **when repeated/material evidence may become durable self-evolution**.
- #75 owns the **Feynman scientific operating layer**; the historical #16 research/knowledge workflow is superseded.
- #7 owns only **external scientific evidence acquisition/critique capability** used by Feynman when needed.

## Current execution sequence

Core proof remains:

```text
#2 Context acquisition
  -> #5 Bounded execution + deterministic validation
      -> #6 Independent review
          -> #10 One real project pilot
```

Current readiness:

- **#19** — bounded file-first scientific project bootstrap is merged to `main`
  through PR #20 (merge commit `a87a948`); Issue #19 is closed. The packaged
  `project-bootstrap` skill owns the agent-facing procedure around its
  deterministic helper and colocated tests. No workflow or second
  `file-workbench` skill exists.

- **#2** — bounded context acquisition is complete for its deterministic v1
  contract and is conditionally closed. It was implemented and merged through PR #33
  (`edf446c`). The explicit-allowlist packet helper, schema-valid task fixture,
  deterministic tests, and hosted CI step are accepted as the v1 procedure.
  A fresh read-only run against the current `/Users/tai/ai-labs` baseline
  produced 3 canonical and 4 repository-evidence entries with no conflicts or
  uncertainties. Host-observable parent-resume/adapter traces remain
  unavailable; native parent-resume and adapter-selection remain NOT_ASSESSED
  and are delegated to #31/#56 rather than blocking the deterministic v1 closure.
- **#14** — the bounded external provenance/artifact/runtime-fit matrix is recorded in `PLAN-ARW-EXTERNAL-SKILLS-20260809-001.md`; installed Codex creator reuse is accepted and unqualified external catalogs remain reference/deferred.
- **#38** — the installed Codex/OpenAI creator was exercised through Phases A–M and dogfooded on `franky-guidance-manager`. A fresh explicit `--disable skill_search` Codex baseline completed without a skill-tool event, while the model-visible catalog currently exposes 86 entries / 58 unique names with 13 duplicate-name groups. A new disposable fixture demonstrated project-local activation, sibling selection, and a clear arithmetic negative without exporting private host skill content. Real-skill utility lift, broad catalog co-loading, dynamic security, and direct OpenCode behavior remain `NOT_ASSESSED`; the issue remains conditional.
- **#35** — the system-skill consolidation is now canonical on `main` through PR #53 (merge commit `e1e05c096bb0912a9a3759f349ad97e3a5424e7d`). The reconciled branch preserved `main`'s independent planning commit, and canonical-main control-plane validation run #163 passed. The live catalog now reports 50 tracked dispositions, six canonical active capabilities, and explicit noncanonical overlay boundaries. Remaining model-mediated behavioral and cross-runtime gates are owned by #38 and remain explicitly `NOT_ASSESSED`; no Antigravity migration was included.
- **#50** — accepted on canonical `main` through the #35 reconciliation. `manifests/skill-catalog.yaml` records 50 tracked packages with exactly one disposition, 10 ignored local overlays as explicitly noncanonical, and six canonical active governance capabilities. Structural and repository-grounded utility evidence pass; model-mediated runtime routing remains `NOT_ASSESSED` and is now advanced by #38. Antigravity migration remains out of scope.
- **#56** — the minimum repository-level materialization slice now resolves the
  Franky contract to canonical `control-plane-audit`, requires explicit read
  permission, executes a deterministic read-only boundary, emits a
  provenance-bearing `VALIDATED` artifact, records lifecycle transitions in
  the transition function, and rejects unauthorized mutation. Canonical
  nested provenance hashing is stable. Native `@franky` dispatch, native
  skill loading, and host enforcement remain `NOT_ASSESSED` under the still-active
  issue.
- **#57** — closed after PR #58 (merge commit `6fd67dc`) satisfied its deterministic acceptance criteria. Host runtime surfaces remain explicitly `NOT_ASSESSED` outside this issue's accepted scope.
- **#68–#71** — Argus, Prometheus, Athena, and shared lifecycle hardening are accepted on `main` through PR #72 (merge commit `a01e26d`). The deterministic lifecycle evaluator, scoped support contracts, artifact states, evidence chain, and review gates are accepted; host-mediated selection/loading/mutation/permission behavior remains `NOT_ASSESSED`.
- **#62** — Operation Workflow v1 stabilization is documented as Issue-first,
  PLAN-conditional, one-work-unit-branch, CI/review-gated, and reconciled after
  merge. The Operation Workflow control-plane foundation is stabilized, not
  complete; runtime execution evidence depends on #56. #60 owns approval and
  remote validation hardening. Native host behavior remains `NOT_ASSESSED`.
- **#60** — deterministic approval hardening is now represented by the
  merge-readiness evaluator: `APPROVED`, `REJECTED`, and `CHANGES_REQUESTED`
  are distinct; decisions require reviewer/reason/timestamp/revision/history;
  review, decision, and authorization bind the current head and bounded
  artifact/action/scope/evidence/upstream snapshot; stale or malformed records
  are rejected. Native continuation/state recovery remains `NOT_ASSESSED`.
- **#46** — superseded by the bounded owners #2, #17, #31, #56, #60, and #62;
  no distinct context-graph runtime capability is accepted for implementation.

## Milestone roadmap

### Milestone A — Operation Workflow Control Plane v1

**Status:** READY after PR #78 merge. The scope is the request lifecycle,
Issue/PLAN/PR flow, deterministic validation, ownership, and state
reconciliation. This milestone does not claim runtime agent behavior.

### Milestone B — Runtime Materialization v1

**Owner:** #56. Prove the minimum chain:

```text
agent contract → runtime loading → skill resolution → execution
→ artifact output → validation
```

No orchestration platform, model router, or autonomous-agent framework is in
scope. The next bounded execution plan is
`PLAN-ARW-RUNTIME-MATERIALIZATION-V1-20260816-001.md`.

### Milestone C — Scientific Agent Loop v1

**Owners:** #7 remains active; #59 and #61 semantic v1 contracts are
completed. The retained bounded example is:

```text
scientific question → Feynman reasoning → knowledge/context retrieval
→ Argus provenance/context → artifact → Athena review
```

This milestone does not implement a full Scientific Wiki platform.
- **#75** — the bounded Feynman v1 slice is conditionally complete and closed through
  codex-chatpgt PR #76 (merge `4ef68b27a5f7649eddb8ae8efa51779854767bdb`) and
  research-projects PR #22 (merge `dddf5e54e5b5000df14e4f3f556b746e97edf645`).
  It establishes the two-mode read-only adapter, three ADAPT scientific
  procedures, policy guardrails, bounded packet qualification, selected-project
  binding, and the reviewed DC-IV vertical proof. Native dispatch, native skill
  loading/materialization, Personal Wiki runtime, host mutation/permission
  enforcement, and human scientific acceptance remain `NOT_ASSESSED`; the
  scientific result remains `REQUIRES_ADDITIONAL_MEASUREMENT` with no mechanism
  promotion. Future extensions remain with #7, #47, #56, and #61.
- **#17** — NOT_PLANNED/superseded for the current horizon. The earlier
  #2-resumption/PR #3 proof path is obsolete; no current consumer justifies
  graph machinery beyond Issue/optional PLAN/PR links.
- **#5** — accepted through the bounded execution/closure record in
  `PLAN-ARW-EXECUTION-VALIDATION-20260809-001.md`. PR #33 is the bounded
  change surface; its induced failure/repair, impact frontier, syntactic and
  semantic closure, whole-diff check, and revalidation are mapped there.
- **#6** — the consequential slice now has a bounded independent read-only
  review in a separate Athena-style context, recorded in
  `PLAN-ARW-INDEPENDENT-REVIEW-20260809-001.md` as `CONDITIONAL-PASS`. The
  review added judgment beyond deterministic checks and documented a concrete
  low-risk skip case. The current host still does not expose parent-resume or
  adapter-selection traces, so runtime acceptance remains conditional. A
  local Codex review probe found and repaired unsupported `preferred_skills`
  adapter fields in PR #34 (`200b606`); the local discovery root was also
  repaired for two legacy skills missing frontmatter, with follow-up startup
  reports showing zero malformed-agent and missing-frontmatter warnings. A
  fresh Codex 0.146.0 read-only probe with provider connectivity returned
  `PROBE_OK` and reproduced no malformed-agent/frontmatter warnings; it did
  expose unrelated environment/vendor warnings (stale model-cache schema,
  optional plugin manifest fields, rollout-db fallback, skill-description
  budget truncation, and an unavailable optional Computer Use MCP). These are
  recorded as runtime observations, not silently counted as acceptance. The
  deterministic v1 review gate is conditionally closed; native adapter and
  parent-resume traces remain `NOT_ASSESSED` under #31/#56/#61.
- **#10** — the Graph Engineering pilot has conditionally passed and is closed
  for its selected
  read-only integration slice. It consumed the merged #2 helper in
  read-only mode. An earlier live Issue comment records 2 canonical + 3
  repository-evidence entries; the current rerun intentionally used a broader
  explicit allowlist and produced 3 canonical + 4 repository-evidence
  entries. The project validator passed (12 pages, 21 Canvas nodes, 6 edges),
  and the selected project/instruction file hashes were unchanged before and
  after execution. It found no project override, lifecycle adapter,
  project-specific skill/agent, or evolution signal (`NO ACTION`). This
  Host-runtime limitations remain `NOT_ASSESSED` and are owned by #31/#56; the
  exact rerun hashes and review disposition are recorded in the #6 review PLAN.
- **#15** — completed for the v1 workflow family. PR #18 supplies the
  reactive slice; PRs #72, #82, and #84 supply bounded proactive
  control-plane improvement, validation, review, repair, and reconciliation
  evidence without introducing a duplicate lifecycle.
- **#16** — inventory-first; select one real research task and inspect existing Wiki/Personal Wiki/RAG-BM25/OpenScience/Typst interfaces before implementation.
- **#7** — the production Wiki Scientific Evidence MCP is registered once in
  the local global Codex configuration. With the user's bounded data-export
  approval, fresh read-only Codex/OpenAI sessions recorded one successful
  `wiki.query` for factual lookup, mechanism and comparison cases, plus a
  successful insufficient-evidence response (`abstain_or_verify`, one gap).
  Four contrastive computation/plotting/fitting/coding sessions recorded zero
  Wiki calls. A second fresh positive and negative pair reproduced the same
  behavior. The event traces show no duplicate retrieval calls. The accepted
  boundary is therefore registration, discovery, transport, contract,
  model-mediated routing and fresh-session stability for the parent path.
  Codex does not expose richer adapter/model identity or separate
  Feynman/Athena selection traces, so those role-specific host details remain
  conditional. No duplicate retrieval layer or wrapper skill was added, and
  the historical Ollama fallback remains out of scope. A 2026-08-10 bounded
  re-probe independently confirmed the local `wiki-evidence/v1` packet (five
  evidence items, four source IDs, no gaps); its fresh host-mediated call was
  selected once but cancelled before return and is therefore recorded as
  `NOT_ASSESSED/BLOCKED`, not as new acceptance evidence. The latest
  approval-confirmed local export independently returned five evidence items
  across three distinct source IDs with no gaps; the contract validator
  passed and immutable Wiki sources remained unchanged. Its fresh host retry
  again selected one `wiki.query` call but was cancelled before a packet
  returned, so it remains `NOT_ASSESSED/BLOCKED`. The newest
  approval-confirmed local rerun used the bounded biomaterial memristor
  synthesis query and returned five evidence items across four distinct
  source IDs with no gaps (`hybrid`, `[bm25, lexical_fallback]`). The Wiki
  contract validator again reported immutable sources unchanged and no live
  knowledge changes; only packet metadata and repository-relative provenance
  were retained.
  The latest approval-confirmed MCP retry failed before returning a packet
  with `KeyError: 'edges'` while loading the Wiki NetworkX graph index;
  contract validation still passed and sources remained immutable. This is
  `NOT_ASSESSED/BLOCKED` runtime/index evidence, not a successful export.
  A fresh OpenCode model-execution attempt on a synthetic skill was rejected
  by the host privacy guard before execution; direct OpenCode behavior remains
  `NOT_ASSESSED`, while no-model catalog and precedence evidence remains valid.
- **#13** — historical v1 rationalization remains provenance only; current skill-system work is governed by #38/#35.
- **#24** — control-plane quality hardening is accepted through PR #30
  (`c559f9a`). Franky authority is explicitly scoped to the control plane,
  retained skill metadata/contracts are discriminative, scoped `AGENTS.md`
  guidance is present for agents/skills/workflows, and a small static
  contrastive routing fixture distinguishes metadata evidence from behavioral
  runtime selection. Hosted CI passed; behavioral selection remains an
  explicit runtime limitation.
- **#31** — semantic v1 completed through PR #32 and the #10 pilot.
  Native host hooks remain NOT_ASSESSED as recorded below.
  Fresh orientation, event-driven selective reorientation,
  authority ordering, failure reclassification, acceptance-before-learning,
  bounded evolution observation, and logical-session continuation guidance are
  now part of the canonical operating surface. The #10 pilot returned
  `NO ACTION` for evolution observation and produced no natural reorientation
  event. No session manager, checkpoint
  store, evolution database, or new skill/workflow was added. Native AGENTS
  timing, automatic closeout, compaction, parent-resume, and adapter
  selection remain NOT_ASSESSED and do not block the semantic v1 disposition.
- **#9** — NOT_PLANNED for the current horizon. Historical AgentMemory
  evidence remains non-canonical; activation requires a new measured
  continuity need and no mandatory memory layer or auto-promotion path exists.
- **#12** — NOT_PLANNED for the current horizon. Portability remains a future
  trigger under #4 until an authorized secondary-harness task exists.

### Phase A backlog reconciliation — 2026-08-25

- **#59** and **#61** are completed for their bounded semantic v1 contracts;
  native Argus/Athena dispatch and skill loading remain NOT_ASSESSED.
- **#62** remains open with one blocker: no demonstrated second repository
  consuming the portable lifecycle procedure. PRs #78–#84 prove the complete
  single-repository work-unit chain.
- **#9**, **#12**, and **#17** are NOT_PLANNED/superseded until a real
  activation consumer appears. Phase B/C Issues were not changed.

## Planning state

`documentation/plans/` now contains backlog/activation-aware PLANs for open architecture Issues that previously lacked them. A PLAN file does not imply execution readiness. Status and activation gates are authoritative for readiness, and each PLAN must be revised near execution against current repository/runtime evidence.

Issue #94 has a review-bound Archify pilot under `documentation/archify/`.
The surface is derived and revision-pinned, cataloged as reference-only/
explicit-only, and does not establish native dispatch, skill loading, or host
permission enforcement.

Issue #17 is NOT_PLANNED/superseded for the current horizon; historical PR #3
is not an active proof fixture. #2 and #5 are accepted for their deterministic
contracts; host-level runtime acceptance remains explicitly `NOT_ASSESSED`
under #56/#8.

## Anti-overengineering state

The current design intentionally preserves semantic distinctions while delaying machinery:

- no custom goal graph database;
- no one-Issue-per-task policy;
- no workflow-per-persona/tool;
- no active machine workflow without a proven persisted-state consumer;
- no mandatory memory layer;
- no model-router platform before representative tasks;
- no project lifecycle adapter unless real project evidence requires it;
- no plugin/harness abstraction before stable behavior exists;
- #13/#21 cleanup rules are now active for this control-plane baseline; each
  retained abstraction has a named consumer and historical proof-only records
  remain read-only provenance.

Simplification should remove duplicate machinery or unclear ownership, not collapse distinctions that preserve provenance, authority, validation, or review independence.

## Known execution gap

The bounded #2 helper has now been rerun against the current repository/runtime
baseline and the read-only Graph Engineering pilot remains hash-stable. The
remaining gap is host-observable parent-resume/adapter behavior; neither
should be inferred from deterministic tests, the project validator, or the
bounded independent review.
