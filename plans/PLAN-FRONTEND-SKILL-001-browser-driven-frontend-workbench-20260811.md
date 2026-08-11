---
id: PLAN-FRONTEND-SKILL-001-20260811
issue: 44
status: execution-ready
repository: taixuann/codex-chatpgt
created: 2026-08-11
scope: frontend/browser skill evaluation and synthesis
---

# FRONTEND-SKILL-001 — Browser-driven frontend workbench skill

## Objective

Determine whether Codex needs one durable frontend workbench skill, based on exact inspection and bounded real-world evaluation of a small set of external frontend/browser Agent Skills.

The target is a reliable frontend working procedure, not a collection of fashionable skill folders.

## Starting state

- `skills/` currently has no dedicated frontend/browser design skill.
- `workspace-tools` Issue #19 exposes a real failure mode: behavior/state tests passed while the browser experience remained database-first, plot-poor and visually weak.
- the control plane already prefers thin skills that teach procedure rather than duplicate executable implementation.
- external skill catalogues are evidence sources, not canonical policy.

## Primary source catalogue

- https://github.com/finfin/awesome-frontend-skills

Inspect the exact linked repositories/SKILL.md files before using any recommendation from the catalogue.

## Candidate set

Keep the evaluation small.

### Engineering candidate

`addyosmani/agent-skills` → `frontend-ui-engineering`

Evaluate for:

- component responsibility;
- responsive-layout discipline;
- accessibility;
- state/UI separation;
- design-system restraint;
- frontend architecture without framework churn.

### Design candidate

Choose one strongest candidate after exact-source inspection, preferably:

- `pbakaus/impeccable` → `frontend-design`, or
- Anthropic's current frontend-design skill if its source/license/procedure is stronger.

Evaluate primarily for anti-pattern detection:

- generic AI/SaaS visual language;
- weak hierarchy;
- spacing/typography inconsistency;
- card/gradient/glow overuse;
- poor information density;
- layout decisions detached from user tasks.

### Browser/testing candidate

Evaluate one primary browser skill and at most one complementary testing skill:

- `microsoft/playwright-cli` → `playwright-cli` preferred for browser interaction;
- `anthropics/skills` → `webapp-testing` or another maintained Playwright best-practice skill only if it adds distinct procedure.

The resulting control-plane skill must invoke/use existing browser capabilities rather than reimplement browser automation.

## Evaluation harness

Use `taixuann/workspace-tools` Issue #19 as the representative real task.

For each candidate procedure, ask whether it materially improves:

1. detection of the missing plot-first hierarchy;
2. layout inspection at 1280×800, 1440×900 and 1920×1080;
3. detection of overflow, nested scrolling, blank-space imbalance and poor density;
4. browser screenshot/ARIA/interaction validation;
5. accessibility/focus/keyboard review;
6. separation of product task, architecture and visual style;
7. bounded repair rather than framework rewrite.

Do not use synthetic toy UI alone as evidence.

## Candidate classification

For each inspected skill, record a compact table:

| Candidate | Useful procedure | Duplicate | Framework-specific | Risk | Adopt/adapt/reject |
|---|---|---|---|---|---|

Avoid long reviews. The goal is to decide what survives synthesis.

## Skill creation gate

Create `skills/frontend-workbench/SKILL.md` only if the evaluation finds a stable distinct procedure not already covered by existing global/browser capabilities.

A valid outcome is:

```text
NO_NEW_SKILL
external/browser capabilities already sufficient
```

If a skill is created, it must stay concise and procedural.

## Target procedure

Expected kernel:

```text
ORIENT
- identify primary user task
- inspect current architecture/state contracts

BASELINE
- run/open the real UI
- capture canonical viewports
- inspect console/network if relevant

CRITIQUE
- hierarchy: is the primary task visually primary?
- layout: overflow, whitespace, alignment, density, resize
- state: selection/filter/loading/error/read-only
- accessibility: focus/keyboard/semantic state
- aesthetics: compare against chosen references without architecture drift

IMPLEMENT BOUNDED SLICE
- preserve state/data contracts
- avoid framework migration unless capability evidence requires it

REOPEN BROWSER
- interact, resize, compare screenshot/ARIA
- inspect real content and long-label/error states

REPAIR
- bounded iteration only

VALIDATE
- deterministic tests + browser evidence + project consume-back where applicable

REPORT
- changed behavior/presentation
- evidence
- unresolved defects
- architectural deviations, if any
```

## Required principles

The skill should encode:

- browser-first evidence for non-trivial UI work;
- primary-user-task hierarchy before visual polish;
- responsive layout checked at declared viewports;
- tests do not substitute for looking at the rendered UI;
- semantic state must survive styling;
- external frontend references are selective inputs, not reasons to switch frameworks;
- dense technical/research tools may appropriately prioritize information density over marketing aesthetics;
- accessibility and keyboard/focus checks are normal validation, not optional garnish;
- reuse existing component systems where useful;
- avoid giant card dashboards, gradients/glow and decorative AI surfaces unless a project explicitly requires them.

## What the skill must NOT contain

- React/Vue/Next-specific implementation recipes unless clearly marked as optional external references;
- duplicate Playwright executable code or bundled browser runtime;
- a universal design system;
- hundreds of arbitrary typography/color presets;
- one-off workspace-tools/PDA semantics;
- automatic package installation;
- a mandate to use Open MCT, Tabler, shadcn, Tailwind or any frontend stack;
- generic instructions to “make it beautiful” without task evidence.

## Provenance requirements

If adapting external text/procedure:

- record repository + exact path/ref/commit where practical;
- record license;
- paraphrase/synthesize rather than copying large blocks;
- retain attribution where required;
- keep a compact references section in the resulting skill or adjacent provenance note.

## Validation

If `frontend-workbench` is created:

1. validate skill structure with current repository skill validation;
2. run one bounded dashboard task using the skill;
3. compare with prior/no-skill workflow where possible;
4. verify it causes browser inspection and catches at least one meaningful UI defect before completion;
5. verify it does not introduce architecture/framework scope drift;
6. independently review the skill for duplication and verbosity.

## Acceptance mapping

| AC | Evidence |
|---|---|
| AC-01 exact candidate inspection | source/ref notes |
| AC-02 overlap classification | evaluation table |
| AC-03 real task evaluation | workspace-tools #19 evidence |
| AC-04 browser-driven procedure | run trace / handoff evidence |
| AC-05 one-or-zero skill | repository diff |
| AC-06 framework neutrality | skill review |
| AC-07 responsive/a11y steps | skill contents + representative run |
| AC-08 provenance/license | references/provenance section |
| AC-09 no-skill valid outcome | explicit final decision if applicable |

## Review focus

Challenge:

- creating several overlapping frontend skills;
- copying awesome-list descriptions instead of source procedures;
- adding browser instructions that Codex cannot actually execute;
- framework-specific advice masquerading as universal frontend policy;
- skill content too long to be reliably applied;
- style taste replacing user-task reasoning;
- no measured benefit on a real UI task.

## Completion condition

Close when the frontend procedure has been evaluated in real work and the repository contains either one validated `frontend-workbench` skill or an explicit evidence-backed decision to create none.