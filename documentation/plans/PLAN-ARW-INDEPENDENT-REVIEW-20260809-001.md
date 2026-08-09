---
id: PLAN-ARW-INDEPENDENT-REVIEW-20260809-001
issue: 6
status: blocked
blocked_by: [5]
activation_gate: issue-5-reviewed
scope: selective-independent-review
---

# Objective

Prove a selective independent-review gate that adds judgment beyond deterministic validation and can be skipped for low-risk work.

# Activation gate

Execute only after #5 establishes the actual execution/validation output shape. Revise this PLAN against that evidence before activation.

# Starting evidence

Consume originating Issue/PLAN acceptance criteria, actual diff/result, deterministic validation evidence, and unresolved uncertainty. Athena is a candidate reviewer only where runtime support and independence justify it.

# Execution phases

1. Define review-trigger criteria from risk, uncertainty, architecture/scientific judgment, repeated failure, and validation gaps.
2. Define bounded review input/output using the real #5 evidence shape.
3. Run one representative review where independent judgment should materially help.
4. Run or document one low-risk case where review is explicitly skipped.
5. Require findings to distinguish blocker, non-blocking improvement, and uncertainty.
6. Keep reviewer read-only and separate from remediation.
7. Decide whether review remains role/policy behavior or deserves a reusable procedure.

# Validation

- review adds information not produced by deterministic checks;
- reviewer does not silently fix evaluated work;
- findings trace to acceptance criteria/evidence;
- skip path exists for trivial/low-risk work;
- no reviewer-specific workflow tree is created.

# Stop conditions

Stop/simplify if review merely reruns tests, if independence cannot be established, or if the trigger rule invokes review mechanically for ordinary work.

# Definition of done

One consequential case demonstrates useful independent review and one low-risk case demonstrates justified skipping, with a compact reusable boundary and no duplicate execution loop.
