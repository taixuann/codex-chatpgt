# Workflow package guidance

`documentation/OPERATING-WORKFLOW.md` is the canonical human-readable
semantic lifecycle. A machine workflow is a specialized contract only when a
named consumer needs persisted state, ordered transitions, approval gates,
recovery, or deterministic lifecycle validation.

For every retained workflow, keep the entry condition, consumer, state,
transitions, gates, failure/recovery behavior, exit condition, and validation
explicit. Keep workflows executor-agnostic: model, provider, backend, and
persona routing belong elsewhere.

The Franky tree is the specialized governed control-plane family. Its
`franky.yaml` entrypoint is canonical only within `franky_control_plane`; it
must point back to the global semantic lifecycle and must not claim authority
over ordinary work. Nested pipelines inherit the top-level approval boundary.

Use the Issue/PLAN/PR/CI lifecycle for ordinary repository work. Do not create
workflow YAML, a change wrapper, or a new branch merely to represent a simple
task sequence. Run the workflow, IO/cache, and allowlist validators for every
changed machine workflow and report unresolved skill references honestly.
