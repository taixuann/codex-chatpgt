---
name: skill-creator-v2
description: Create, update, evaluate, or audit reusable agent skills with evidence-backed workflow design, provenance, routing, and validation. Use for skill lifecycle work; do not use for ordinary code changes, one-off instructions, or unrelated repository maintenance.
metadata:
  prototype: issue-121
  source_baseline: skill-creator
---

# Skill Creator v2

Create, update, evaluate, or audit reusable Codex skills without weakening
scope, provenance, routing, validation, or evidence boundaries.

This is an isolated Issue #121 prototype. It is not installed in the active
skill catalog and must not be copied into `skills/` during this prototype.
The peer `evaluate` workflow below is preserved only as historical evidence of
the superseded prototype architecture; the active package uses shared EVALUATE
capability under `skills/skill-creator/`.

## Action surface

Use exactly one explicit action:

- `create` — admit a justified new reusable capability through the full
  upstream-first creation lifecycle. This may mutate the target package.
- `update` — make a bounded evidence-backed change to an existing skill and
  compare baseline with candidate. This may mutate the target package.
- `evaluate` — assess effectiveness and quality with proportional evidence.
  Read-only by default; recommendations do not apply repairs.
- `audit` — assess holistic system fitness, ownership, placement, freshness,
  overlap, cost, and evidence. Read-only by default; return one disposition,
  never silently apply it.

`validate` is an internal mechanical primitive, not a user-facing action.

An unknown explicit action fails closed and reports the valid actions above.
Without an explicit action, route only when lifecycle intent is unambiguous;
otherwise resolve the smallest ambiguity that changes the action. Never guess a
mutating action from an ambiguous request.

## Shared invariants

- Preserve the user's goal, scope, authorization, and existing package content.
- Check whether native behavior, `AGENTS.md`, an existing skill, a script,
  tool, plugin, or project-local procedure is the better owner before creating
  or changing a skill.
- Prefer an existing or maintained baseline. Clone it unchanged first, record
  source/ref/path/license, then adapt only the demonstrated gap.
- Keep package resources minimal and derive each file from a workflow need.
- Use progressive disclosure: load one action workflow and only the shared
  references it needs.
- Separate structural validation, behavioral evaluation, and holistic audit.
- Report `PASS`, `FAIL`, and `NOT_ASSESSED` honestly; unavailable runtime or
  activation signals never become inferred success.
- Keep creation intent and scratch evidence in the Issue/session location, not
  in the final runtime package.
- Stop on ambiguous ownership, unresolved provenance/license, unsafe or
  unauthorized mutation, missing observable qualification criteria, or a
  suitable existing owner.

## Progressive disclosure

Read the selected workflow before acting:

- [CREATE](workflows/create.md)
- [UPDATE](workflows/update.md)
- [EVALUATE](workflows/evaluate.md)
- [AUDIT](workflows/audit.md)

When source, donor, license, placement, or adaptation claims matter, read
[provenance](references/provenance.md). When trigger, collision, or sibling
boundaries matter, read [routing](references/routing.md).

## Qualification boundary

CREATE and UPDATE must validate affected structure and run proportional
evaluation before qualification. CREATE also requires an inspectable
`intent.md`, necessity/owner reasoning, source anchors, initial cases, a
manual probe, cleanup proof, and a compact receipt. EVALUATE and AUDIT may
recommend changes, but repairs belong to an explicitly authorized UPDATE.

This prototype may be compared with the unchanged `skill-creator`; it must not
replace, register, globally activate, merge, or close Issue #121.
