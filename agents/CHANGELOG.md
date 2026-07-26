# Franky agent change log

Append-only record of governed agent adapter changes.

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
