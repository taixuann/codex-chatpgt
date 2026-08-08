---
name: franky-workflow-factory
description: Design staged, role-aware workflow packages with proposal-first routing, deterministic flaw detection, bounded repair, and approval-bound lifecycle handoff.
namespace: franky
qualified_name: franky.workflow-factory
folder: franky-workflow-factory
scope: franky
---

# Franky workflow factory

The factory is proposal-first. It stages workflow packages and hands approved
artifacts back to the existing lifecycle pipelines. It never launches agents,
never spawns subagents, and never performs recursive delegation.

The parent runtime delegates once into Franky, and Franky enters
`WF-FRANKY-CANONICAL` with `factory_operation` selected for staged workflow
package design.

Operations:

- `qualify_request`: normalize intent, mode, role targets, and references.
- `audit_request`: inventory roles, skills, collisions, and protected paths.
- `generate_package`: write a proposal package under
  `/Users/tai/.codex/workflows/temp/<request-id>/`.
- `repair_and_validate`: apply only deterministic repairs, record each repair,
  and re-run the audit.
- `promote_approved_package`: route approved artifacts to their existing
  lifecycle workflows; never bypass their validators or launch agents.

The structured request may contain `purpose`, `roles`, `mode`, `references`,
and optional `capabilities`. Natural-language intent is preserved in the
manifest, while runnable workflow proposals require explicit capability
contracts. Unknown roles, scope crossings, unresolved critical flaws, and
missing required resources remain non-runnable.

For any existing skill selected by a proposal, run the Franky-adapted quality
gates before the package is considered runnable:

- required gates: package structure and security scan;
- advisory gates: bundled eval/test evidence and review-age metadata.

Structural or security failures block the package. Missing evals or review
metadata produce warnings so existing skills remain compatible. The validator
does not install, publish, push, or modify the inspected skill.

Every generated workflow step must contain `id`, `skill`, `operation`,
`inputs`, `outputs`, `validation`, `approval_gate`, and `on_failure`.
Generated workflows are executor-agnostic, keep role boundaries explicit, and
use `return_to_human` for ambiguity or failure.
