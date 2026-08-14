# Franky agent change log

Append-only record of governed agent adapter changes.

```yaml
- agent: franky-agent-first-hardening
  version: 1.1.0
  goal_id: ISSUE-57
  workflow_id: FRANKY-HARDENING-AUDIT-V1
  reason: Harden the Issue #56 Franky task/result boundary with done criteria, ordered evidence, impact-bound routing, non-self review enforcement, and explicit runtime limitation reporting without introducing a workflow engine.
  changed_paths:
    - agents/franky.toml
    - agents/AGENTS.md
    - documentation/OPERATING-WORKFLOW.md
    - ops/schemas/franky-task.schema.yaml
    - ops/schemas/franky-result.schema.yaml
  validation:
    - 37 ops/scripts unit tests
    - validate_franky_contracts.py
    - evaluate_franky_agent.py
    - Athena independent read-only re-review: conditional pass; no remaining High/Medium/Low findings
    - Codex 0.147.0-alpha.6.5 parser PASS; actual dispatch, skills.config behavior, and host mutation escalation NOT_ASSESSED/BLOCKED
    - Athena independent re-review: conditional pass; no remaining concrete findings
  approval:
    - Issue #57 audit scope and completion criteria
  change_commit: 81a1470; branch codex/issue-57-franky-hardening
  rollback:
    - Revert the Issue #57 hardening commit and restore the Issue #56 contract surfaces.
```

```yaml
- agent: franky-agent-first-contract
  version: 1.0.0
  goal_id: ISSUE-56
  workflow_id: FRANKY-TASK-RESULT-V1
  reason: Add the bounded Franky task/result boundary, approved capability repertoire reference, one-call closure contract, explicit mutation escalation, and non-recursive acceptance-ready return semantics while preserving Issue #38 skill-quality ownership.
  changed_paths:
    - agents/franky.toml
    - agents/feynman.toml
    - agents/prometheus.toml
    - agents/athena.toml
    - agents/argus.toml
    - agents/AGENTS.md
    - agents/README.md
    - manifests/agent-capability-repertoires.yaml
  validation:
    - validate_agent_toml.py for all active adapters
    - validate_franky_contracts.py
    - evaluate_franky_agent.py
    - Athena independent read-only re-review: conditional pass; no High/Critical findings after bounded repairs
    - codex 0.147.0-alpha.6.5 parser probe; live model behavior NOT_ASSESSED/BLOCKED by DNS
  approval:
    - Issue #56 scope and refinement comments
  change_commit: not-created; working tree preserved for human review
  rollback:
    - Restore the prior adapter TOMLs and remove the Issue #56 repertoire/contract surfaces after review.
```

```yaml
- agent: codex-first-routing
  version: 1.1.0
  goal_id: CHG-20260808-001
  workflow_id: WF-FRANKY-CANONICAL
  reason: Add Argus exploration and Athena independent review adapters while preserving canonical Feynman, Prometheus, and Franky boundaries; migrate defaults to observed GPT-5.6 routing tiers.
  changed_paths:
    - agents/argus.toml
    - agents/athena.toml
    - agents/feynman.toml
    - agents/prometheus.toml
    - agents/franky.toml
    - agents/templates/agent.toml
    - agents/AGENTS.md
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
    - agents/franky.toml
    - agents/README.md
    - agents/CHANGELOG.md
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
    - agents/franky.toml
    - agents/feynman.toml
    - agents/prometheus.toml
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
