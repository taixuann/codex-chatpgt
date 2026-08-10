# Workflow package guidance

`documentation/OPERATING-WORKFLOW.md` is the canonical human-readable
semantic lifecycle. A machine workflow is a specialized contract only when a
named consumer needs persisted state, ordered transitions, approval gates,
recovery, or deterministic lifecycle validation.

For every retained workflow, keep the entry condition, consumer, state,
transitions, gates, failure/recovery behavior, exit condition, and validation
explicit. Keep workflows executor-agnostic: model, provider, backend, and
persona routing belong elsewhere.

No machine workflow is currently installed. A future Franky workflow may be
admitted only after a named consumer, persisted state, transitions, approval
gates, recovery/resume behavior, and deterministic validation are demonstrated.
Historical `workflows/franky/**` YAMLs were retired because those proofs were
absent; this file remains the policy boundary rather than a runtime catalog.

Use the Issue/PLAN/PR/CI lifecycle for ordinary repository work. Do not create
workflow YAML, a change wrapper, or a new branch merely to represent a simple
task sequence. If a future machine workflow is admitted, validate its state,
IO/cache, recovery and allowlist contracts and report unresolved skill
references honestly.
