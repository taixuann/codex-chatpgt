# Skill package guidance

Skills are reusable agent-facing capabilities, not personas, workflows, or
deterministic commands disguised as procedures.

A skill may describe a capability and its bounded procedure only. It must not
define an agent, select a persona, encode a lifecycle/workflow, own project
logic, or silently mutate canonical policy. Agent identity belongs to the
canonical role registry and its adapters; lifecycle and gates belong to the
operating workflow and task contracts.

The checked-in admission surface is `../manifests/skill-catalog.yaml`. A
package may be structurally valid and still be noncanonical. Only packages in
its `canonical_active` list are canonical active capabilities; all other
tracked packages require explicit/on-demand use or remain reference, merge,
or retired material.

## Admission and routing

- Keep a skill only when the trigger recurs, is discriminative, and benefits
  from a stable procedure, boundary, or judgment that the parent should not
  rediscover each run.
- Prefer `<object>-<operation>` names. A persona prefix is allowed only when
  the permission or runtime boundary is materially part of the capability.
- Treat frontmatter `description` as routing metadata. It must state the
  action, object, use condition, and a negative boundary when neighbors could
  match the same request.
- Keep discovery descriptions concise and bounded. Do not encode a phase
  lifecycle, persona selection, delegation policy, or universal execution
  sequence in a skill.
- Route by capability first, then decide whether a role/agent is useful. Do
  not choose a persona and force a task into its skill list.
- Skills outside the tracked control-plane allowlist (system, plugin, or
  personal runtime packages) are not silently promoted into this repository.

## Procedure contract

Every retained skill should make its trigger, inputs/context, procedure,
output, side effects, stop/escalation condition, and validation expectation
easy to find. Keep provider-specific detail progressive and colocate
deterministic helpers with the capability unless they earn an independent
consumer.

Do not add a registry, universal frontmatter schema, routing service, or
scorecard merely to make packages look uniform. Retire or merge a package
before polishing it when an existing task contract, built-in capability, or
deterministic validator already owns the behavior.

GitHub Issues/Plans and `documentation/OPERATING-WORKFLOW.md` own durable
execution state and lifecycle. A skill may provide procedure and validation,
but it must not become a second workflow engine.
