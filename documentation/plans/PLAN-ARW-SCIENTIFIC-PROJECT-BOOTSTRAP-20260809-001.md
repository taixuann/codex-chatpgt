---
id: PLAN-ARW-SCIENTIFIC-PROJECT-BOOTSTRAP-20260809-001
issue: 19
status: review-ready
repository: taixuann/codex-chatpgt
branch: codex/issue19-adaptive-bootstrap-v1
created: 2026-08-09
---

# Objective

Prove the smallest reusable capability for file-first project bootstrap and coherent multi-file artifact authoring, with a scientific project as the primary bounded case.

The implementation must remain an execution/capability slice. It must not create a fourth workflow family, duplicate project inheritance (#10), duplicate Research/Knowledge semantics (#16), or invent a second Goal/PLAN graph (#17).

# Starting State

The control plane already has:

- a canonical general operating workflow;
- proposed System Configuration and Change semantics (#15);
- proposed Research and Knowledge semantics (#16);
- Goal/PLAN linking semantics (#17);
- global-to-project inheritance proof tracked by #10;
- external-skill qualification tracked by #14;
- existing project-linking / workflow-maintenance skills that must be inspected for overlap before any new skill is created.

The missing behavior is not another project workflow. The missing behavior is a bounded procedure that can take a file-oriented project request, inspect a new or existing project, choose the minimum useful file/artifact surface, select existing capabilities, and materialize related artifacts without assuming the project is primarily software.

## Implemented behavior

The bounded behavior is implemented in
`ops/scripts/bootstrap_file_project.py`. It validates an artifact map,
performs a dry-run by default, and materializes only declared files under an
explicit output root when `--apply` is supplied. It rejects traversal,
control-plane paths, non-external unresolved links, duplicate paths, unsafe
raw-data writes, and invalid create/update/preserve intents. Focused tests in
`ops/scripts/tests/test_bootstrap_file_project.py` exercise adaptive
materialization, dry-run, CLI apply, and failure-to-preserve repair behavior.

No new global skill, workflow, schema, or project knowledge plane was created.
The observed procedure remains small enough to live as a deterministic control
plane tool plus ordinary instructions.

## Execution record — 2026-08-09

The authoritative Issue #19 body was read before this execution. Existing
capabilities were checked for overlap: `franky-project-linker`,
`franky-install-project-link`, `franky-workflow-organizer`,
`franky-workflow-factory`, and file/document refinement capabilities. The
#14 external-skill plan contains no qualified project-bootstrap or
file-workbench candidate that should replace this bounded behavior. No new
skill, workflow, schema, or project knowledge plane was introduced.

A bounded existing-project scientific fixture was exercised with an artifact map
containing orientation, project profile, metadata guidance, processed-data and
analysis boundaries, results guidance, external Wiki/OpenScience references,
and one pre-existing immutable raw file. Dry-run produced no files; apply
produced exactly the six declared new files and preserved the raw file. The
raw SHA-256 was unchanged. Optional `samples`,
`figures`, `manuscript`, `tools`, `workflows`, `skills`, and `agents` surfaces
were not created or copied.

For the #5 execution/validation lens, an intentional `create` request for the
raw file failed with exit 1 and the bounded repair restored `preserve`; a clean
fixture then applied successfully. The independent review of the actual diff
found malformed non-mapping artifact entries could escape the intended
`BootstrapError` boundary. The repair validates artifact entries before path
collection and adds a regression test; the focused suite now passes six tests.

### Acceptance status

| Criterion | Status | Result |
| --- | --- | --- |
| AC-01 | pass | Existing-project execution plus greenfield dry-run/apply test coverage |
| AC-02 | pass | Only declared project modules materialized; no empty optional scaffold |
| AC-03 | pass | Existing local capabilities inspected; no new skill created |
| AC-04 | pass | Multi-file artifact map carries purpose, format, dependencies, and links |
| AC-05 | pass | Raw file preserve boundary and unchanged hash verified |
| AC-06 | pass | Wiki/OpenScience represented only as external references |
| AC-07 | pass | No global agent/workflow definitions copied into the fixture |
| AC-08 | pass | Research workflow is referenced externally; no #16 lifecycle duplicated |
| AC-09 | pass | No-skill packaging decision follows one observed deterministic contract |
| AC-10 | conditional-pass | Human-readable minimal surface is demonstrated; maintainer acceptance remains pending |

This slice provides bounded evidence for #5's implement/validate/repair loop,
#6's review gate, #15's proactive system-change path, and #17's existing
Issue/PLAN relationship without adding a graph registry or relationship file.
The next genuinely ready step is review/acceptance of this #19 implementation,
then a separately scoped #15 follow-up if the maintainer accepts the slice.

# Requirements

1. Support both greenfield and brownfield project setup.
2. Treat files/artifacts as first-class project outputs rather than assuming code is the common denominator.
3. Parse multi-artifact requirements and preserve dependencies/cross-links.
4. Use adaptive project modules rather than a static exhaustive scaffold.
5. Preserve scientific provenance where data/experiments exist.
6. Keep Wiki / Personal Wiki / OpenScience external to the project and referenced rather than copied.
7. Reuse existing global/built-in/external capabilities before creating project-local or new global skills.
8. Make an evidence-backed decision whether the capability should remain ordinary instructions/procedure, become one combined skill, or become two distinct skills (`project-bootstrap` and `file-workbench`).

# Non-goals

- No universal scientific ontology.
- No project registry database.
- No custom graph engine.
- No one-skill-per-file-format design.
- No static full folder tree for every project.
- No migration of all existing projects.
- No redesign of Wiki/OpenScience/RAG.
- No replacement of #10, #16, or #17 contracts.
- No broad Franky cleanup; that remains #13.

# Architecture / Design

## Capability boundary

Conceptually test two responsibilities:

```text
PROJECT REQUEST
      ↓
BOOTSTRAP / ORIENT
      ↓
project type + current state + requirements
      ↓
CAPABILITY SELECTION
      ↓
ARTIFACT MAP
      ↓
FILE MATERIALIZATION / UPDATE
      ↓
STRUCTURE + LINK + PROVENANCE VALIDATION
      ↓
HANDOFF TO NORMAL PROJECT WORKFLOW
```

Do not pre-commit to two separate skills. The proof must determine whether bootstrap and artifact authoring have sufficiently distinct triggers, inputs/outputs, side effects, and reusable procedures to warrant separation.

## Adaptive project surface

Candidate always-considered core:

```text
README.md
AGENTS.md
project.yaml
documentation/
```

Even these are not blindly created for brownfield projects if equivalent accepted surfaces already exist.

Optional scientific/file-oriented modules:

```text
research/
samples/
experiments/
figures/
manuscript/
tools/
```

Selection rules:

- `research/` only when project-local scientific reasoning state is useful;
- `samples/` only when stable sample identity must connect multiple measurements/experiments;
- `experiments/` only when the project has experimental/computational work units;
- `figures/` only when project-level synthesis figures exist beyond local analysis results;
- `manuscript/` only when academic output is an actual project deliverable;
- `tools/` only for project-specific reusable tooling that does not belong near one experiment and is not yet globally reusable.

## Scientific provenance spine

For applicable experiment/work units:

```text
metadata/
data/raw/
data/processed/
analysis/
results/
```

Rules:

- `data/raw/` is immutable/read-only by policy;
- processing never overwrites raw inputs;
- local analysis/result outputs stay near the experiment when that improves provenance;
- project-level publication figures may synthesize multiple experiment results;
- stable cross-project procedures are candidates for global skill/tool extraction only after repeated evidence.

## Knowledge boundary

```text
SHARED WIKI / OPENSClENCE
      ↑ reference / retrieve
PROJECT
      ↓ produces project evidence/results
```

The project may store pointers/configuration describing knowledge sources, but must not duplicate Literature Wiki, Personal Wiki, OpenScience, or retrieval corpora into its own folder merely for convenience.

# Execution Strategy

## Phase 0 — Inventory and overlap audit

Before implementation:

1. inspect existing local skills related to project linking, goal/session setup, external handoff, documentation, and workflow creation;
2. inspect #14-qualified external candidates relevant to spec/context/project/documentation scaffolding;
3. compare triggers, outputs, side effects, and reuse potential;
4. explicitly identify whether current behavior can be achieved by adapting/generalizing an existing skill instead of adding a new one.

Deliverable: capability-overlap matrix and a provisional `reuse / adapt / new / no-skill` recommendation.

## Phase 1 — Select one bounded scientific/file-oriented case

Prefer one real project when local access is available. If execution must start without that project, use a deliberately small fixture that captures realistic needs rather than a synthetic exhaustive template.

Capture:

- project objective;
- new vs existing state;
- requested artifacts;
- existing conventions/files;
- project-local scientific modules actually needed;
- external Wiki/OpenScience references;
- validation requirements.

## Phase 2 — Build an artifact map before writing files

Represent only enough structure to make materialization deterministic and reviewable, for example:

```yaml
artifacts:
  - path: README.md
    purpose: orientation
    format: markdown
  - path: project.yaml
    purpose: project profile
    format: yaml
  - path: experiments/electrical-iv/metadata/README.md
    purpose: measurement metadata guidance
    format: markdown
```

Do not establish a universal schema unless the proof demonstrates repeated fields worth stabilizing.

For each material artifact, know at least:

- path;
- purpose;
- format;
- create/update intent;
- dependencies/links where material;
- authority/lifecycle if ambiguity could cause misuse.

## Phase 3 — Materialize the smallest justified structure

Greenfield:

- create only modules justified by requirements;
- avoid empty placeholder directories unless a tool requires them.

Brownfield:

- inspect before changing;
- preserve naming/conventions by default;
- add missing control/project surfaces only where useful;
- do not reorganize unrelated files as part of bootstrap.

## Phase 4 — Validate file-first behavior

Run deterministic checks where practical:

- requested artifact existence;
- no accidental overwrite of protected/raw inputs;
- no broken relative links/known references;
- no duplicate global skill/workflow definitions copied into project;
- no copied Wiki/OpenScience tree;
- no unjustified empty module scaffold;
- project files remain navigable by a human without relying on hidden agent memory.

## Phase 5 — Decide skill packaging

Evaluate observed behavior against three outcomes:

### Outcome A — no new skill
Use if ordinary operating instructions plus existing capabilities reproduce the behavior reliably.

### Outcome B — one combined skill
Use if bootstrap + artifact authoring form one stable trigger/procedure with low internal branching and shared validation.

### Outcome C — two skills
Use only if evidence shows distinct contracts, for example:

- `project-bootstrap`: project orientation, capability selection, project-surface decisions;
- `file-workbench`: reusable multi-file artifact planning/materialization across projects that already exist.

Do not split by conceptual elegance alone.

## Phase 6 — Exercise inheritance/research boundaries, not reimplement them

When #10 is ready, run the resulting capability on one real project to test global-to-project inheritance.

When the chosen case is scientific, let #16 own research semantics such as claims/hypotheses/knowledge promotion. This PLAN may create requested files for those concepts, but must not define their scientific lifecycle independently.

# Files / Components Expected to Change

Potential, not guaranteed:

```text
skills/<existing-skill>/...
```

Implemented in this slice:

```text
ops/scripts/bootstrap_file_project.py
ops/scripts/tests/test_bootstrap_file_project.py
```

or, only if earned by evidence:

```text
skills/project-bootstrap/
skills/file-workbench/
```

Possible validation/support surfaces:

```text
skills/.../scripts/
ops/schemas/            only if a stable contract is actually proven
documentation/CURRENT.md
```

A representative project itself should remain outside the control-plane repository unless it is intentionally a bounded fixture.

# Contracts

## Bootstrap input

At minimum, execution must know or infer:

```yaml
project:
  name:
  purpose:
  mode: new|existing
requirements: []
expected_outputs: []
```

Additional fields are optional and should be derived only when useful.

## Artifact contract

Do not freeze a formal schema during Phase 0. The proof should first determine which fields recur in real multi-file requests. Candidate semantics are:

```yaml
path:
purpose:
format:
intent: create|update|preserve
links: []
depends_on: []
authority:
```

# Validation Plan

Map Issue #19 acceptance criteria as follows:

- AC-01: demonstrate one live mode plus bounded coverage of the other.
- AC-02: before/after tree proves adaptive module selection.
- AC-03: overlap inventory documents built-in/local/external reuse check.
- AC-04: artifact map traces request -> produced files; the deterministic
  materializer consumes the map directly.
- AC-05: raw-data protection rejects writes and accepts explicit preserve intent.
- AC-06: project tree and references prove Wiki/OpenScience are not copied.
- AC-07: project diff contains no duplicate global agent/workflow definitions.
- AC-08: research semantics reference #16 rather than redefining promotion/lifecycle rules.
- AC-09: packaging decision remains no-skill because one deterministic tool and
  ordinary instructions cover the observed trigger/procedure.
- AC-10: final review explicitly removes any file/folder/capability that has no distinct purpose.

# Failure Modes

1. **Static-template creep** — the proof starts creating every optional module by default.
   - Repair: return to requirement -> module justification mapping.

2. **Code-first drift** — software conventions (`src/`, package scaffolds, notebook trees) become universal defaults.
   - Repair: treat code/notebooks as optional artifacts selected by project need.

3. **Research-workflow duplication** — bootstrap starts defining claim/evidence/hypothesis semantics.
   - Repair: preserve files as materialization targets and defer semantics to #16.

4. **Inheritance duplication** — project gets copied global roles/workflows/skills.
   - Repair: reference/inherit; defer inheritance proof to #10.

5. **Skill proliferation** — one skill per format/project type appears.
   - Repair: keep format handling inside artifact materialization unless a distinct reusable procedure is proven.

6. **Scientific ontology creep** — project profile/sample metadata grows into a universal schema before evidence.
   - Repair: keep project-selected fields and promote only repeated stable contracts.

7. **Wiki duplication** — OpenScience or Wiki trees are copied into the project.
   - Repair: store references/configuration only.

# Risks and Trade-offs

- A minimal adaptive bootstrap is slightly less uniform than a static cookiecutter, but avoids unused surfaces and makes project structure reflect real work.
- File-first design favors human navigability and mixed scientific work, but may need optional code-oriented extensions for software-heavy projects.
- Keeping Wiki/OpenScience external preserves authority and reuse, but requires explicit source references so projects remain understandable when moved.
- Deferring skill split decisions avoids premature abstraction, at the cost of one extra proof/review step.

# Rollback / Reversibility

- New project files should be additive and reviewable before acceptance.
- Existing project content must not be destructively reorganized without an explicit project-specific migration plan.
- Any newly created skill can remain project-local or be removed if the proof shows ordinary instructions/existing skills are sufficient.
- No database or global registry migration is permitted in this slice, so rollback remains file-level.

# Acceptance Mapping

Issue #19 AC-01 through AC-10 are all addressed by Phases 0–6. A passing implementation must include both behavioral evidence and a complexity review; simply generating the candidate folder tree is not sufficient.

# Review Focus

1. Is the result genuinely file-first?
2. Did the adaptive structure instantiate only what the project needs?
3. Are raw evidence, transformations, results, and project-level outputs distinguishable where scientifically necessary?
4. Are Wiki/OpenScience correctly external?
5. Did existing skills get inspected before any new skill was added?
6. Does the result duplicate any ownership from #10, #16, or #17?
7. Is one/two/no-skill packaging justified by observed contracts rather than aesthetic symmetry?

# Open Questions

Resolve from evidence rather than up front:

- Does `project.yaml` earn a stable common schema, or should it remain a light project-specific profile?
- Are `project-bootstrap` and `file-workbench` actually separate reusable procedures?
- Should sample identity be represented by files, a project registry, or existing project conventions in the first real scientific pilot?
- Which existing Franky project-linking/setup skills should be generalized, retained, or later retired under #13?

# Execution Handoff

Activation gate:

1. run Phase 0 overlap/external-skill inventory first;
2. select one bounded file-oriented scientific project/fixture;
3. create a focused execution branch from current `main`;
4. revise this PLAN against the actual project and available external skills;
5. implement the smallest behavior needed for that case;
6. validate and review before deciding global skill packaging.

This PLAN now records the bounded implementation slice. It does not authorize
broad project scaffolding, migration, or creation of a reusable skill without a
second project demonstrating an independent stable contract.
