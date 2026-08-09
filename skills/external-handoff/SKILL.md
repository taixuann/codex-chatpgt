---
name: external-handoff
description: Prepare bounded role-neutral handoffs to external executors with explicit scope, evidence, approval gates, and rollback.
---

# External handoff

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
   and preserve its stdout/stderr as handoff evidence.

Never include credentials, ask an executor to bypass sandboxing, or expand
scope because a handoff is inconvenient.
