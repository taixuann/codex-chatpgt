---
name: franky-goal-session
description: Create or update a measurable Franky maintenance goal package with scope, acceptance evidence, task tracking, walkthroughs, and promotion metadata. Use for governed multi-step Codex work that must be linked into AI Labs sessions.
---

# Franky goal session

Use this skill for governed, multi-step operator work. Do not create a goal for
a simple read-only check unless the user requests durable tracking.

1. Restate one concrete outcome, evidence threshold, scope, non-goals, and stop
   condition.
2. Create or continue `GOAL-YYYYMMDD-NNN` under
   `/Users/tai/ai-labs/ops/sessions/` using the existing goal templates.
3. Keep `GOAL.md` stable after approval; update routine progress in `TASKS.md`
   and `walkthroughs/RUN-*.md`.
4. Record Codex-first artifacts and their intended AI Labs destinations in
   `PROMOTION.yaml`.
5. Validate required files and metadata with `scripts/validate_goal_package.py`.

Human approval is required before configuration, link, destructive, external,
or publication changes. A goal package records intent and evidence; it does
not grant mutation authority.
