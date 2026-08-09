---
name: franky-workflow-organizer
description: Design or validate a thin Franky machine workflow when lifecycle state, gates, or recovery require a persisted YAML contract; keep it executor-agnostic and validate references. Do not use for ordinary task sequencing or deterministic YAML lint alone.
metadata:
  last_reviewed: 2026-08-09
  review_interval_days: 90
---

# Franky workflow organizer

## Contract

- **Trigger:** a named consumer needs persisted workflow state, gates, transitions, recovery, or an explicit machine lifecycle.
- **Inputs:** entry condition, ordered capability steps, inputs/outputs, validation, approval gates, failure/recovery, and consumer.
- **Output:** a thin workflow proposal or validation result with referenced-skill map.
- **Boundary:** ordinary task sequencing stays in the parent/Issue/PLAN; deterministic YAML checks stay in the validator when no lifecycle judgment is needed.
- **Stop:** stop when no real state/gate/recovery consumer exists, or when the design would require model/provider fields.
- **Validation:** run `validate_workflow.py` and lifecycle/IO-cache validators; keep nested pipelines free of independent approval gates.

Translate an operator objective into a small workflow graph. Keep the workflow
about capabilities and skill contracts, not models, providers, or executors.

Each step must contain:

- `id`
- `skill`
- `operation`
- `inputs`
- `outputs`
- `validation`
- `approval_gate`
- `on_failure`

Keep steps independently verifiable. Use `return_to_human` for ambiguous,
unsafe, or failed transitions. Run `scripts/validate_workflow.py` before
proposing a workflow for promotion.
Workflow inventory, validation, and apply operations must be executable
deterministically without an LLM. LLM use is optional only for ambiguous
interpretation and never required for mechanical checks. Do not put model,
provider, or executor names in workflow YAML.

Every runnable workflow must declare `version: 1` or higher and
`invocation_policy: workflow_only`. A run must carry the workflow ID and
version, goal ID, current step ID, allowed skill, operation, input artifact
IDs, and approval record. Use `scripts/validate_run.py` to verify that the
current skill and operation match the active step.
