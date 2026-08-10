---
id: PLAN-ARW-PORTABILITY-20260809-001
issue: 12
status: deferred
activation_gate: stable-codex-first-semantics-plus-project-proof
scope: portable-semantics-and-harness-adapters
---

# Objective

Extract stable control-plane semantics from the proven Codex-first implementation and map them to thin harness adapters without creating a second orchestration platform.

# Activation gate

Require completed core behavior (#2/#5/#6), project proof (#10), and enough routing evidence to distinguish canonical semantics from temporary Codex runtime details.

## Current evidence boundary — 2026-08-10

OpenCode catalog probes provide adapter-level path, ID, and precedence
observations, but the external OpenCode overlay still contains
`franky-workflow-manager` and `franky-install-workflow` entries. This
repository does not own that overlay, and no mutation is authorized by this
PLAN. Cross-runtime workflow retirement, activation, permission enforcement,
and behavioral equivalence therefore remain deferred until a separately
authorized #12 portability slice has an owner and a representative task.

# Execution phases

1. Inventory which current contracts are semantic vs Codex-specific.
2. Freeze the smallest canonical contracts for role boundaries, capability routing, task handoff, validation/review, context, and model/reasoning tiers.
3. Map those contracts to Codex as one adapter.
4. Select one secondary harness only if there is an actual use case.
5. Reuse one canonical source for skill/agent definitions; avoid independently editable copies.
6. Run one representative task through both mappings and document unsupported differences.
7. Keep packaging/distribution mechanics separate from capability semantics.

# Validation

- same semantic task survives both adapters;
- unsupported features are explicit;
- no duplicate canonical source trees;
- adapter layer is thinner than the system it adapts;
- runtime-specific config does not leak into global architecture unnecessarily.

# Stop conditions

Stop/defer if semantics are still changing, a second harness has no real user/task, or portability requires speculative abstraction rather than tested mapping.

# Definition of done

One stable canonical semantic surface is mapped to Codex and one justified secondary harness with transparent differences and no duplicated source of truth.
