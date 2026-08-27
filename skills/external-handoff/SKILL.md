---
name: external-handoff
description: Prepare a bounded handoff for an external executor when work crosses a runtime or team boundary; include scope, evidence, approval, and rollback. Do not use for ordinary parent-to-worker packets or to execute the external change.
metadata:
  last_reviewed: 2026-08-09
  review_interval_days: 90
---

# External handoff

## Contract

- **Trigger:** an approved task must cross a runtime, tool, or team boundary.
- **Inputs:** objective, exact scope, evidence, constraints, approval owner, and rollback target.
- **Output:** a role-neutral handoff with acceptance and rollback conditions.
- **Boundary:** ordinary parent-to-worker delegation stays in the task contract; this skill does not execute the external action.
- **Stop:** stop when scope, authority, or rollback is ambiguous.
- **Validation:** verify every path and acceptance command is explicit and no protected data is included.

Prepare a handoff package for an external executor or bounded worker. This
skill does not execute the external action implicitly.

## Execution Steps

1. State the objective, selected role/workflow, exact paths, allowed operations,
   and explicit exclusions.
2. Separate read-only discovery from mutation steps and name the required
   approval gate before any external write.
3. List prerequisites, validation commands, rollback, unresolved risks, and
   the expected evidence returned by the executor.
4. If a non-interactive runner is explicitly approved, use the bundled runner
   with an executable plus separate argv tokens (never a shell command string)
   and preserve its stdout/stderr as handoff evidence. Shell operators,
   pipelines, redirections, and shell expansion are rejected.

Never include credentials, ask an executor to bypass sandboxing, or expand
scope because a handoff is inconvenient.
