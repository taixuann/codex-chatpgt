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

## Bounded external handoff — OpenCode overlay (NOT_EXECUTED)

This is a handoff contract, not authorization to mutate the external
OpenCode control plane.

```yaml
executor_scope: external OpenCode configuration owner
canonical_codex_role: Franky
workflow: issue-12-portability-overlay-audit
target_root: /Users/tai/.config/opencode
target_branch: main
observed_head: 808cda6
state: dirty_and_unresolved
approval_owner: user/maintainer
status: NOT_EXECUTED
```

### Read-only scope

Inspect only the effective catalog and the following relevant paths:

```text
/Users/tai/.config/opencode/AGENTS.md
/Users/tai/.config/opencode/skills/workflow-manager/SKILL.md
/Users/tai/.config/opencode/skills/install-workflow/SKILL.md
/Users/tai/.config/opencode/skills/ai-labs/franky.install/install-workflow/SKILL.md
```

The observed catalog contains `franky-workflow-manager` and
`franky-install-workflow`, which overlap the repository-level retired
workflow surface. The external checkout is already dirty, including modified
runtime/config files and untracked skill trees; do not reset, clean, stash,
delete, or overwrite any of that state.

### Required approval before mutation

The external executor must obtain fresh confirmation of the exact repository,
branch, and intended paths before any write. No mutation is currently allowed.
If later approved, the executor must first create a non-destructive
before-state manifest and an owner-approved rollback target; `808cda6` is not
itself a safe rollback target while the worktree is dirty.

### Expected handoff evidence

- pre/post `git status --short` and exact commit SHA;
- effective `opencode debug skill --pure` name/location manifest;
- consumer/overlap decision for each workflow skill;
- explicit keep, move-on-demand, or retire outcome;
- validation output and a reversible rollback description;
- confirmation that no credentials, project contents, or unrelated dirty files
  were read into the handoff or changed.

Until those conditions are met, cross-runtime workflow retirement remains
`NOT_ASSESSED` and this Codex repository remains the only mutation surface.

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
