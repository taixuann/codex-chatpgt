---
id: PLAN-ARW-PROJECT-INHERITANCE-20260809-001
issue: 10
status: conditional-pass
blocked_by: [runtime-observability]
activation_gate: core-contracts-reviewed
scope: one-real-project-pilot
---

# Objective

Prove that one real project can inherit the shared control-plane semantics while adding only genuine project-specific context, rules, lifecycle differences, validation, and local procedures.

# Activation gate

Execute after #2/#5/#6 establish the core behavior the pilot is meant to exercise. Revisit the pilot choice at activation time; Graph Engineering is a candidate, not a hardcoded requirement.

# Execution phases

1. Select one real project and one bounded real task.
2. Inventory its actual instruction chain, CURRENT/DECISIONS/PLAN state, files, and validation.
3. Apply shared context/execution/validation/review semantics without copying global agents/skills/workflows.
4. Record every project override and ask whether it is truly required.
5. Add a lifecycle adapter only if a material state/gate/order difference is demonstrated.
6. Add a project-specific skill only if a stable local procedure cannot be represented as global capability + project context.
7. Record evidence for #7/#8/#9/#13 instead of solving all extensions here.

## Pilot execution record — 2026-08-09

Graph Engineering was exercised as the selected real-project pilot in
read-only mode. The bounded path used the current #2 helper against an
explicit allowlist, then ran the project validator and compared selected
project/instruction hashes before and after. The packet contained 3 canonical
and 4 repository-evidence entries, with no conflicts or uncertainties. The
validator passed with 12 pages, 21 Canvas nodes, and 6 edges; no project file
changed.

Observed dispositions:

- global instructions were sufficient for the read-only pilot; no project
  AGENTS override was needed;
- no lifecycle adapter, project-specific skill, or project agent was needed;
- no subagent spawn added value for this small known scope, so direct parent
  inspection was preferred;
- no noisy/stale/conflicted context event occurred during the bounded run;
- no omitted affected surface was found by the closure/reconciliation check;
- evolution observation returned `NO ACTION`: no repeated friction or
  material cross-project pattern was observed in this single pilot.

This is conditional integration evidence, not proof of hidden host behavior:
automatic AGENTS loading timing, parent resume, skill selection, and closeout
invocation remain unobservable. The pilot therefore does not activate #8/#9,
#11, or #15 by itself.

# Validation

- one real task completes or fails transparently;
- project-specific surface remains minimal;
- no duplicated global definitions;
- project output passes project validation;
- any adapter/skill has evidence-backed necessity;
- local/project contents are not copied into the control-plane repo.

# Stop conditions

Stop and simplify if the shared lifecycle is already sufficient; that is a successful outcome and should not trigger adapter creation.

# Definition of done

One project demonstrates useful inheritance with minimal override and produces concrete evidence about routing, validation, continuity, and duplication for later issues.
