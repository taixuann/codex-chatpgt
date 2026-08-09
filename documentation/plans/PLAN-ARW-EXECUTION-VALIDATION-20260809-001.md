---
id: PLAN-ARW-EXECUTION-VALIDATION-20260809-001
issue: 5
status: execution-ready
blocked_by: []
activation_gate: issue-2-reviewed-conditional
scope: bounded-execution-validation
---

# Objective

Prove one bounded implementation path from explicit scope/acceptance through execution, deterministic validation, bounded repair, and parent synthesis.

# Activation gate

#2 is now implemented in PR #33 (`edf446c`) with a bounded allowlist,
deterministic packet shape, task-contract fixture, and explicit host-runtime
limitations. This PLAN is activated for one downstream vertical slice. The
runtime limitation remains an acceptance uncertainty, not a reason to invent a
second context subsystem.

# Starting evidence

Use the accepted output shape from #2 rather than inventing a new execution
contract. Prefer existing task-contract/schema/runtime behavior where
sufficient. The representative task is the merged #2 implementation surface:
helper, task fixture, CI step, README pointer, workflow guidance, tests, and
this PLAN's activation reconciliation.

# Execution phases

1. Select one representative small engineering change with objective acceptance criteria.
2. Freeze scope, expected output, stop/escalation conditions, and validation checks.
3. Execute directly or delegate only if isolation/parallelism is useful.
4. Run deterministic validation mapped to acceptance criteria.
5. Exercise one real or safely induced failed check when practical; diagnose -> bounded repair -> revalidate.
6. Return unresolved architecture/scope changes to parent rather than widening work.
7. Decide whether any reusable validation skill/script/lifecycle clause actually earned packaging.

# Validation

- scope diff remains bounded;
- AC-to-evidence mapping is explicit;
- deterministic checks are separated from qualitative review;
- bounded repair stops on repeated/speculative failure;
- existing repo checks remain passing.

# Packaging bias

Implementation should remain normal agent behavior unless a stable reusable procedure is demonstrated. Prefer scripts/tools for deterministic checks. Do not create `implementation`/`validation` skills for symmetry.

# Stop conditions

Stop and escalate if the task requires architecture redesign, repeated repair fails, validation is not objective enough, or #2 contracts prove incompatible.

# Definition of done

One real bounded change is executed and validated with traceable evidence, including a bounded repair path where practical, without new ceremony that does not improve reliability.
