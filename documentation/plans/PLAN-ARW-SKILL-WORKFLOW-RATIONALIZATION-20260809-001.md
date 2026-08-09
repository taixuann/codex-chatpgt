---
id: PLAN-ARW-SKILL-WORKFLOW-RATIONALIZATION-20260809-001
issue: 13
status: blocked
blocked_by: [2, 5, 6, 10]
activation_gate: core-plus-project-evidence
scope: skill-workflow-rationalization
---

# Objective

Audit and rationalize the existing skill/workflow surface using real runtime/project evidence while preserving distinct useful procedures, permissions, validation, and rollback guarantees.

# Activation gate

Execute only after #2/#5/#6/#10 provide enough evidence to distinguish stable capability from legacy wrapper, decorative workflow, or still-unproven behavior. Consume #14 external-skill evidence where relevant.

# Execution phases

1. Inventory every current skill/workflow: trigger, purpose, consumers, scripts/assets, mutation boundary, observed use.
2. Compare against built-in/official/external alternatives from #14.
3. Classify each as KEEP / GENERALIZE / MERGE / REPLACE / RETIRE / DEFER.
4. Challenge both over-complexity and over-aggressive cleanup.
5. Change only items with enough evidence; leave uncertain components DEFERRED.
6. Validate all changed references, deployment paths, behavior, and rollback.
7. Reconcile only accepted architectural outcomes to CURRENT/DECISIONS.

# Validation

- complete inventory exists;
- every changed component has evidence-backed disposition;
- retained skill descriptions are discriminative;
- retained workflows have real state/gate/runtime value;
- deterministic work remains scripts/tools where appropriate;
- no broad rename/refactor occurs solely for aesthetics;
- required capability is not lost during simplification.

# Stop conditions

Defer any component when evidence is insufficient. Do not optimize for minimum file count. Stop broad cleanup if migration risk exceeds demonstrated value.

# Definition of done

The active surface is smaller or more coherent, with every change justified by observed use/overlap and no loss of meaningful procedure, permission, validation, or recovery behavior.
