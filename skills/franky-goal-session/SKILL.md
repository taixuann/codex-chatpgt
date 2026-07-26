---
name: franky-goal-session
description: Create or update a measurable Franky maintenance goal package with scope, acceptance evidence, task tracking, walkthroughs, and promotion metadata. Use for governed multi-step Codex work that must be linked into AI Labs sessions.
---

# Franky goal session

Use this skill for governed, multi-step operator work. Do not create a goal for
a simple read-only check unless the user requests durable tracking.

Use the lifecycle `qualify -> select role -> load role/ontology -> draft ->
validate -> human review/approval -> materialize -> execute -> revise`.
`materialize` and `revise` are explicit workflow operations; they are not a
permission to mutate a project or bypass a human gate.

1. Restate one concrete outcome, evidence threshold, scope, non-goals, and stop
   condition.
2. Resolve exactly one role with `scripts/resolve_role.py`, then load its role
   reference and `references/ontology.yaml`.
3. Draft and materialize `GOAL-YYYYMMDD-NNN` under
   `/Users/tai/ai-labs/ops/sessions/` from `references/templates/`. The
   compatibility files in `ops/templates/` are pointers, not sources.
4. Keep approved goal fields immutable. Put routine progress in `TASKS.md` and
   `walkthroughs/RUN-*.md`; revisions are immutable snapshots under
   `revisions/` with a validated `current.yaml` pointer.
5. Record Codex-first artifacts and intended AI Labs destinations in
   `PROMOTION.yaml`, and carry a workflow-run envelope for every governed run.
6. Validate package, role, ontology, metadata, and revision state with the
   bundled scripts before execution or handoff.

Read [the package schema](references/goal-package.schema.yaml), [the lifecycle
contract](references/lifecycle.md), and [the shared ontology](references/ontology.yaml)
when creating or revising a package. Role-specific constraints are in
`references/roles/`.

Validation commands:

```text
python3 /Users/tai/.codex/skills/franky-goal-session/scripts/validate_metadata.py
python3 /Users/tai/.codex/skills/franky-goal-session/scripts/validate_metadata.py \
  --ontology /Users/tai/.codex/skills/franky-goal-session/references/ontology.yaml \
  --roles /Users/tai/.codex/skills/franky-goal-session/references/roles
python3 /Users/tai/.codex/skills/franky-maintenance/scripts/validate_skill_interfaces.py \
  /Users/tai/.codex/skills
```

Human approval is required before configuration, link, destructive, external,
or publication changes. A goal package records intent and evidence; it does
not grant mutation authority.
