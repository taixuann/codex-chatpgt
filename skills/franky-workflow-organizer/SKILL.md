---
name: franky-workflow-organizer
description: Design thin executor-agnostic Franky workflow contracts from ordered skill steps, explicit inputs and outputs, validation, approval gates, and failure transitions. Use when organizing an operator workflow.
---

# Franky workflow organizer

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
