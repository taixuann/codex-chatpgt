---
name: instruction-maintenance
description: Audit or update scoped AGENTS.md when repository behavior or instruction locality must change; preserve precedence and keep rules near their owner. Do not use for architecture documentation or one-off prompt text.
metadata:
  last_reviewed: 2026-08-09
  review_interval_days: 90
---

# Franky guidance manager

## Contract

- **Trigger:** durable repository behavior needs a scoped instruction change.
- **Inputs:** target path, applicable instruction chain, desired invariant, and precedence constraints.
- **Output:** minimal guidance diff plus before/after scope and precedence evidence.
- **Boundary:** architecture history belongs in documentation; do not make persona language global without a real behavior rule.
- **Stop:** stop on ambiguous ownership, conflicting parent guidance, or protected scope.
- **Validation:** inspect the resolved chain and run the guidance validator when available.

Keep durable guidance small and close to the files it governs.

1. Discover the active instruction chain before proposing a change.
2. Put repository conventions in the nearest applicable `AGENTS.md`; keep
   global guidance personal and minimal.
3. Separate routing notes from mandatory execution policy.
4. Do not make a framework's lifecycle apply to unrelated repositories or
   ordinary tasks.
5. Report the before/after instruction scope and any precedence changes.

Require explicit approval before changing global guidance or adding an
override. Never hide instructions in a skill description to bypass scope.
