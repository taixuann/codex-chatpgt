# CREATE

CREATE builds a new target skill only when no suitable installable owner satisfies the request. It is a lifecycle, not file generation.

## Phase flow

0 ORIENT → 1 DEFINE → 2 DISCOVER → 3 RESEARCH → 4 RESOLVE DESIGN → 5 PLAN PACKAGE + CASES → 6 MATERIALIZE BASELINE → 7 BUILD → 8 VALIDATE + REVIEW → 9 PROBE → 10 REAL-TASK EVALUATE → 11 QUALIFY → awaiting_parent_decision

### 0–3: bind, define, discover, research

- Bind the governing Issue, repository, CWD, target placement, session, and allowed paths. Resume the existing issue-execution session; do not create a competing state store.
- Create or resume the task-scoped `intent.md` evidence note with Goal, Done when, Scope, Runtime, Placement, and the four linked architecture views. It is not a second lifecycle state store; keep lifecycle identity in issue-execution's session/task files.
- Compare native behavior, AGENTS guidance, scripts/tools, plugins, local and maintained skills, sibling ownership, and donor sources.
- Record source/ref/path/license, strongest rejected candidates, compatibility constraints, and whether the result is INSTALL_EXISTING, REFERENCE_AND_ADAPT, or CREATE_FROM_SCRATCH_WITH_JUSTIFICATION.

### 4: resolve design

Complete the Design Completeness Audit:

    Skill Architecture
    → Behavior / Action Logic
    → Workflow / State Flow
    → Artifact Architecture

Forward trace Goal → actions → states → material steps → branches/failures → artifacts → validation → cases → qualification. Reverse-trace every persistent file, script, template, and eval to a behavior or shared contract.

Run one fresh diagnostic design challenge. It is read-only and non-binding. Record human review in intent.md as APPROVED, APPROVED_WITH_CONDITIONS, REVISE_DESIGN, or a blocking outcome. A material design delta stales that approval and returns to Phase 4.

### 5–8: package, baseline, build, validate

Create Build Map and Case Map before package mutation. Each resource must name its owner, consumer, lifetime, validation, and runtime/creation-only status. Materialize the maintained baseline unchanged before adapting it.

Build only the approved package. Validate frontmatter, names, links, package closure, scripts, eval schema, source/license records, and side effects. Run a static semantic walkthrough of one normal path and one highest-risk boundary.

### 9–10: probe and evaluate

Run a small realistic manual probe before the full portfolio. Select changed behavior, adjacent high-risk behavior, boundaries, failures, and must-pass cases. Keep raw traces outside intent.md; record compact evidence pointers. Compare outcome correctness, workflow fidelity, routing, state transitions, artifacts, side effects, and cost. Batch the portfolio before repairing.

### 11: qualify and hand off

Freeze the exact candidate and report baseline/candidate revisions, Build Map, Case Map, Evidence Ledger, deviations, cleanup proof, deterministic/static/probe/evaluation results, terminal WORK and separate GOAL status, remaining NOT_ASSESSED or NOT_ASSESSED_WITH_IMPACT, technical disposition, and awaiting_parent_decision.

For taixuann/research-projects#74, the real CREATE target is .agents/skills/manuscript/ with actions init, write, review, figures, package, and publish. Consume promoted results/, never exploratory runs/; use Supervisor-Skills only as donor evidence. If the target checkout has overlapping dirty work or unavailable runtime, do not mutate it.
