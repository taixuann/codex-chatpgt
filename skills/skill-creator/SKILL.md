---
name: skill-creator
description: Create, install, update, or audit reusable Codex skills when a repeated capability needs explicit ownership, provenance, routing, validation, and evidence; do not use for ordinary code changes or one-off instructions.
metadata:
  short-description: Governed skill lifecycle work
  last_reviewed: 2026-09-21
  review_interval_days: 90
---

# Skill Creator

Use exactly one peer action:

- CREATE — design and build a new target skill after necessity and source checks.
- INSTALL — integrate an existing source skill faithfully; route to CREATE when installation would redesign behavior.
- UPDATE — change an existing owned skill against a pinned baseline.
- AUDIT — read-only assessment of behavior, authoring, routing, ownership, provenance, or lifecycle fitness.

EVALUATE is a shared capability consumed by CREATE, UPDATE, INSTALL, and behavioral AUDIT; it is not a peer action. The former maintenance peer is retired.

## Routing

1. Existing local target plus requested mutation → workflows/update.md.
2. Existing maintained source not installed → workflows/install.md.
3. New capability or donor-only source → workflows/create.md.
4. Read-only question → workflows/audit.md.
5. Ambiguous intent, missing authority, unsafe overlap, or missing evidence → stop with clarification or NOT_ASSESSED; never guess a mutation.

## Shared invariants

- Preserve user scope, existing work, source/license identity, and parent authority.
- Check native behavior, AGENTS guidance, scripts, tools, plugins, project procedures, sibling skills, and maintained sources before adding a skill.
- Clone a suitable baseline unchanged before adapting it; donor/reference material is not an install target.
- Keep intent.md, raw traces, baselines, and reports in the Issue/session surface; do not leak creation evidence into the runtime package.
- Keep deterministic validation, behavioral evaluation, and independent review separate. Missing runtime/reviewer signals remain NOT_ASSESSED.
- Athena review is fresh, read-only, and non-binding. Issue-execution owns durable session/Git state and the awaiting_parent_decision boundary.

## Progressive disclosure

Read only the selected workflow, then its owning references:

- CREATE → workflows/create.md
- UPDATE → workflows/update.md
- INSTALL → workflows/install.md
- AUDIT → workflows/audit.md
- ownership/placement → references/discovery.md
- current/upstream source → references/source-strategy.md
- review or qualification → references/review.md and references/qualification.md
- architecture and authoring → references/architecture.md and references/authoring.md
- evaluation and runtime → references/evaluation.md and references/test-environment.md
- validation, routing, and provenance → references/validation.md, references/routing.md, and references/provenance.md

## Qualification boundary

CREATE and UPDATE require deterministic validation, a static semantic walkthrough, affected real-task evidence, regression classification, and an exact candidate handoff. Terminal technical eligibility is separate fresh WORK then GOAL review owned by issue-execution. This campaign does not claim INSTALL or AUDIT qualification, and never merges, closes, or accepts a parent Issue.
