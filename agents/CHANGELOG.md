# Franky agent change log

Append-only record of governed agent adapter changes.

```yaml
- agent: codex-first-routing
  version: 1.1.0
  goal_id: CHG-20260808-001
  workflow_id: WF-FRANKY-CANONICAL
  reason: Add Argus exploration and Athena independent review adapters while preserving canonical Feynman, Prometheus, and Franky boundaries; migrate defaults to observed GPT-5.6 routing tiers.
  changed_paths:
    - /Users/tai/.codex/agents/argus.toml
    - /Users/tai/.codex/agents/athena.toml
    - /Users/tai/.codex/agents/feynman.toml
    - /Users/tai/.codex/agents/prometheus.toml
    - /Users/tai/.codex/agents/franky.toml
    - /Users/tai/.codex/agents/templates/agent.toml
    - /Users/tai/.codex/agents/AGENTS.md
  validation:
    - validate_agent_toml.py for all active adapters and inert template
    - canonical Franky layout validator
    - git diff --check
  approval:
    - user approved agent setup after referenced architecture update
  change_commit: not-created; working tree preserved for human review
  rollback:
    - Restore prior adapter TOML files and the prior template path from the change record.
```

```yaml
- agent: franky
  version: 1.0.0
  goal_id: GOAL-20260726-002
  workflow_id: WF-FRANKY-MAINTENANCE
  reason: Establish the workflow-first Franky adapter and versioned control-plane boundary.
  changed_paths:
    - /Users/tai/.codex/agents/franky.toml
    - /Users/tai/.codex/agents/README.md
    - /Users/tai/.codex/agents/CHANGELOG.md
  validation:
    - validate_agent_toml.py
    - workflow layout validator
    - full Franky workflow validation
  approval:
    - implementation plan approved by human
  change_commit: c7d6553
  rollback:
    - Revert the local change commit after approval.
```

```yaml
- agent: franky
  version: 1.0.1
  goal_id: CHG-20260726-002
  workflow_id: WF-FRANKY-MAINTENANCE
  reason: Set all local runtime adapters to the approved medium-cost baseline and add deterministic input/output/cache validation.
  changed_paths:
    - /Users/tai/.codex/agents/franky.toml
    - /Users/tai/.codex/agents/feynman.toml
    - /Users/tai/.codex/agents/prometheus.toml
  validation:
    - validate_agent_toml.py
    - validate_io_cache.py
    - workflow validators
  approval:
    - implementation request approved by human
  change_commit: 51ffe273c5caffc0ed22327dd9fa54327bdbd17e
  rollback:
    - Restore the previous adapter model and reasoning settings after approval.
```
