---
id: PLAN-ARW-MODEL-ROUTING-20260809-001
issue: 8
status: deferred
activation_gate: representative-runtime-tasks-from-2-5-6
scope: model-reasoning-routing
---

# Objective

Normalize model and reasoning routing from actual runtime evidence while keeping role, model, and reasoning effort separate.

# Activation gate

Do not optimize routing until #2/#5/#6 provide real exploration, execution, validation, and review tasks. Revise model names/runtime assumptions at activation time.

# Execution phases

1. Inventory actual model/reasoning controls exposed by the current Codex runtime.
2. Use real tasks from #2/#5/#6 as probes, not synthetic benchmark-only prompts.
3. Record accepted, ignored, inherited, rejected, and fallback behavior.
4. Classify task routing by risk, ambiguity, validation strength, expected cost, and independence needs.
5. Define portable capability/reasoning tiers before mapping temporary model names.
6. Test escalation and graceful fallback when requested controls are unavailable.

# Validation

- runtime controls are observed rather than assumed;
- at least exploration, bounded implementation, and review receive evidence-backed routing;
- role/model/reasoning remain independent;
- unsupported controls fail visibly/predictably;
- no provider abstraction platform is added.

# Stop conditions

Stop if representative tasks are not yet available, if routing differences are not material, or if a simple table/policy is sufficient and no router implementation is needed.

# Definition of done

A small portable routing policy is justified by real runtime evidence and remains simpler than fixed persona-model assignments or a generalized routing framework.
