---
goal_id: CHG-20260731-001
version: 1
status: applied-locally
approved: true
review_surface: plannotator
---

# Plan: Replace primary Lavish plan review with Plannotator and Markdown contracts

## Objective

Make the existing workflow easier to understand before and after execution by
using readable Markdown plans and Plannotator review, while preserving the
workflow's ordering, approval, and validation semantics.

## Desired outcome

- Plannotator opens from the Codex Stop hook for plan review.
- Lavish no longer opens automatically at session start.
- New goal plans expose logic, inputs, outputs, acceptance, stop conditions,
  execution results, and final review in plain Markdown.
- Existing visual artifacts remain available as optional presentation history.

## Current state

- Plannotator v0.25.1 is installed at `/Users/tai/.local/bin/plannotator`.
- The installer verified the binary SHA256 checksum.
- The local GitHub CLI token is invalid, so signed provenance was not checked.
- The worktree contains unrelated existing user changes; they are out of scope.

## Constraints

- Do not remove existing `.lavish` files.
- Do not change workflow ordering or approval semantics.
- Do not commit or push automatically.
- Keep runtime configuration changes limited to the Plannotator hook transition.

## Execution plan

### Step 1 — Install and bind the review surface

**Inputs:** Plannotator installer, Codex `hooks.json`, Codex `config.toml`.

**Actions:** Install the core binary and add the Codex Stop hook.

**Outputs:** `/Users/tai/.local/bin/plannotator` and a Stop-hook entry.

**Acceptance:** `plannotator --help` works; the Stop hook points to the
Plannotator binary.

### Step 2 — Remove the competing automatic launch

**Depends on:** Step 1.

**Actions:** Remove only the `SessionStart -> lavish-axi` hook.

**Outputs:** Codex starts without opening Lavish automatically.

**Acceptance:** `hooks.json` contains no Lavish SessionStart hook and retains
the Plannotator Stop hook.

### Step 3 — Change the plan contract

**Depends on:** Step 2.

**Actions:** Update the goal-session initializer, plan template, and executor
documentation to use `PLAN.md` as the canonical review input.

**Outputs:** New plans include explicit execution logic and evidence sections.

**Acceptance:** Goal-session tests and workflow layout validation pass.

## Planned changes

| Path | Action | Reason |
|---|---|---|
| `/Users/tai/.codex/hooks.json` | modify | Stop launching Lavish; retain Plannotator review |
| goal-session initializers | modify | Generate readable execution contracts |
| executor documentation | modify | Pass `PLAN.md`, not `.lavish/*.html` |

## Validation commands

```bash
/Users/tai/.local/bin/plannotator --version
python3 -m json.tool /Users/tai/.codex/hooks.json
python3 /Users/tai/ai-labs/ops/skills/shared.session/goal-session/tests/test_init_goal_session.py
python3 /Users/tai/.codex/ops/scripts/validate_franky_canonical_layout.py
```

## Stop conditions

- Plannotator cannot start or review a Markdown plan.
- The Stop hook prevents normal Codex completion behavior.
- Generated plans still require HTML to understand their execution logic.
- Any unrelated runtime or workflow behavior changes.

## Execution result

**Status:** implemented and validated locally.

## Completed

- Installed Plannotator `v0.25.1`.
- Added the Codex `Stop` hook for Plannotator.
- Removed the automatic Lavish `SessionStart` hook.
- Updated plan-generation contracts to use readable Markdown.
- Launched this plan directly in Plannotator for review.

## Validation evidence

| Check | Result |
|---|---|
| Plannotator version | passed: `0.25.1` |
| Installer checksum | passed: SHA256 verified |
| Codex hooks JSON | passed |
| Canonical goal-session initializer | passed |
| Franky workflow layout | passed |
| Signed provenance | not checked: local `gh` token invalid |

## Final review

**Status:** approved by user to proceed.

**Decision:** Markdown `PLAN.md` is canonical; Plannotator is the primary
human review surface; Lavish remains optional presentation history.
