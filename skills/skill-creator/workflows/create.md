# CREATE

CREATE builds a new target skill only when no suitable installable owner satisfies the request. It is a lifecycle, not file generation.

## Phase flow

0 ORIENT → 1 DEFINE → 2 DISCOVER → 3 RESEARCH → 4 RESOLVE DESIGN → 5 PLAN PACKAGE + CASES → 6 MATERIALIZE BASELINE → 7 BUILD → 8 VALIDATE + REVIEW → 9 PROBE → 10 REAL-TASK EVALUATE → 11 QUALIFY → awaiting_parent_decision

### 0–3: bind, define, discover, research

- Bind the governing Issue, repository, CWD, target placement, session, and allowed paths. Resume the existing issue-execution session; do not create a competing state store.
- Create or resume the task-scoped `intent.md` evidence note with Goal, Done when, Scope, Runtime, Placement, and the four linked architecture views. It is not a second lifecycle state store; keep lifecycle identity in issue-execution's session/task files.
- Compare native behavior, AGENTS guidance, scripts/tools, plugins, local and maintained skills, sibling ownership, and donor sources.
- Record source/ref/path/license, strongest rejected candidates, compatibility constraints, and whether the result is INSTALL_EXISTING, REFERENCE_AND_ADAPT, or CREATE_FROM_SCRATCH_WITH_JUSTIFICATION. If a maintained source is an installable suitable skill, route INSTALL and do not redesign it here. Reserve CREATE for donor/reference-only material or no suitable installable owner.

### 4: resolve design

Complete the Design Completeness Audit:

    Skill Architecture
    → Behavior / Action Logic
    → Workflow / State Flow
    → Artifact Architecture

Forward trace Goal → actions → states → material steps → branches/failures → artifacts → validation → cases → qualification. Reverse-trace every persistent file, script, template, and eval to a behavior or shared contract.

Run one fresh diagnostic design challenge. It is read-only and non-binding. Record human review in intent.md as APPROVED, APPROVED_WITH_CONDITIONS, REVISE_DESIGN, or a blocking outcome. A material design delta stales that approval and returns to Phase 4.

### 5–8: package, baseline, build, validate

Create Build Map and Case Map before package mutation. Each resource must name its owner, consumer, lifetime, validation, and runtime/creation-only status.

Apply this source boundary before materializing any baseline:

1. If a maintained existing skill already satisfies the requested capability
   and is installable, stop CREATE and route to INSTALL; do not copy, adapt, or
   redesign that skill under CREATE.
2. If the source is donor/reference-only, or no suitable installable owner
   exists, bind the exact source snapshot, license, path, and hashes, then use
   `REFERENCE_AND_ADAPT` or
   `CREATE_FROM_SCRATCH_WITH_JUSTIFICATION` as appropriate.
3. A donor baseline may be materialized only as a recoverable reference for
   comparison. It is never an implicit install target and never silently
   becomes the shipped package.

Validate the routing decision before package mutation. For a suitable
installable source, stop and route to INSTALL. For donor/reference-only
material, create only the approved target package.

Build only the approved package. Validate frontmatter, names, links, package closure, scripts, eval schema, source/license records, and side effects. Run a static semantic walkthrough of one normal path and one highest-risk boundary.

### 9–10: probe and evaluate

Run a small realistic manual probe before the full portfolio. Select changed behavior, adjacent high-risk behavior, boundaries, failures, and must-pass cases. Keep raw traces outside intent.md; record compact evidence pointers. Compare outcome correctness, workflow fidelity, routing, state transitions, artifacts, side effects, and cost. Batch the portfolio before repairing.

### 11: qualify and hand off

Freeze the exact candidate and report baseline/candidate revisions, Build Map, Case Map, Evidence Ledger, deviations, cleanup proof, deterministic/static/probe/evaluation results, terminal WORK and separate GOAL status, remaining NOT_ASSESSED or NOT_ASSESSED_WITH_IMPACT, technical disposition, and awaiting_parent_decision.

When CREATE requires an external target checkout, do not mutate it if overlapping dirty work or an unavailable runtime makes the target state unsafe to establish.
