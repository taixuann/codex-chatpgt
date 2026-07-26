---
name: franky-external-handoff
description: Prepare bounded handoffs to external executors or systems with explicit scope, approval gates, required evidence, rollback expectations, and no implicit execution. Use when Franky must hand work outside Codex.
---

# Franky external handoff

Prepare a handoff package; do not execute the external action implicitly.

1. State the goal, selected workflow, exact paths, and allowed operations.
2. Separate read-only discovery from mutation steps.
3. List prerequisites, approval gates, validation commands, rollback, and
   unresolved risks.
4. Name the expected evidence artifact and where it will be recorded.
5. Return a handoff that another authorized executor can follow without
   inventing scope.

Do not include credentials or ask an executor to bypass approvals, sandboxing,
or workspace boundaries.
