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
