---
name: franky-workflow-factory
description: Design staged, role-aware workflow packages with reusable skill matching, deterministic flaw detection, bounded repair, and approval-bound promotion.
---

# Franky workflow factory

Generate proposals for workflows owned by registered roles without executing
the domain work. The factory may coordinate workflow, skill, agent, and
registry proposals, but final application must use the existing lifecycle
pipelines after one exact package approval.

Operations:

- `qualify_request`: normalize intent, mode, role targets, and references.
- `audit_request`: inventory roles, skills, collisions, and protected paths.
- `generate_package`: write a proposal package under
  `/Users/tai/.codex/workflows/temp/<request-id>/`.
- `repair_and_validate`: apply only deterministic repairs, record each repair,
  and re-run the audit.
- `promote_approved_package`: route approved artifacts to their existing
  lifecycle workflows; never bypass their validators.

The structured request may contain `purpose`, `roles`, `mode`, `references`,
and optional `capabilities`. Natural-language intent is preserved in the
manifest, while runnable workflow proposals require explicit capability
contracts. Unknown roles, scope crossings, unresolved critical flaws, and
missing required resources remain non-runnable.

Every generated workflow step must contain `id`, `skill`, `operation`,
`inputs`, `outputs`, `validation`, `approval_gate`, and `on_failure`.
Generated workflows are executor-agnostic and use `return_to_human` for
ambiguity or failure.
