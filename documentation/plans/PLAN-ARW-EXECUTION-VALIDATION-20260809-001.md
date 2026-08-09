---
id: PLAN-ARW-EXECUTION-VALIDATION-20260809-001
issue: 5
status: accepted
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

## Execution and closure record — 2026-08-09

The real bounded change is PR #33 / commit `edf446c`, which introduced the
allowlisted context packet helper and its task-contract/CI consumers. The
change-impact classification and proportional frontier are:

| Impact class | Observed surface | Closure result |
| --- | --- | --- |
| interface | helper packet shape and task-contract example | helper tests, fixture, and CI consumer checked |
| behavior | traversal, absolute-path, sensitive-path, symlink, UTF-8, and no-write boundaries | rejection/no-write tests pass |
| structure | helper, focused tests, schema example, workflow step, README/operating guidance | all changed paths are in the PR diff and allowlist |
| authority | operating guidance and context PLAN references | CURRENT/CLOUD/PLAN references reconciled in later review commits |

The direct frontier stopped at the helper, its tests/fixture/CI, and the
documentation consumers because downstream project contracts were unchanged.
No graph, memory, project, or new skill/workflow surface was added.

Closure evidence:

- syntactic closure: agent/skill validators, focused suites, allowlist, and
  `git diff --check` pass;
- semantic closure: references to the helper, task fixture, CI step, and
  current PLAN resolve without unexplained stale local references;
- whole-diff closure: the PR contains only the eight paths listed by
  `git show --name-only edf446c`;
- failure classification: an induced unsafe raw-file request failed as an
  input/scope violation, not an implementation failure; the bounded repair
  restored `preserve` and revalidated successfully;
- stop condition: no further frontier expansion was justified once consumers
  and contracts were checked; host-level parent-resume/adapter observation
  remains an explicit uncertainty rather than a retry target.

The independent review in the #6 PLAN found no material correctness blocker
for this bounded slice and returned `CONDITIONAL-PASS`. The bounded
execution/closure boundary is therefore accepted for #5. Host-level
parent-resume and adapter observation remain open under #2/#6 and do not
expand this execution slice's acceptance boundary.

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
