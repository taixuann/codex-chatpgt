---
name: agent-creator
description: Create, update, simplify, merge, localize, retire, or evaluate a Codex custom-agent role when a distinct role, context, permission, model, or delegation boundary is required; use skill-creator for reusable procedures and AGENTS.md for persistent guidance.
metadata:
  source: jscraik/Agent-Skills@d00c351fe53460afba860f8cdb1580d7cfece7e4
  license: Apache-2.0
---

# Agent creator

Use this skill for a custom Codex agent role or its standalone TOML adapter.
An agent is a thin role/configuration shell around existing skills, tools,
context, and permissions. It is not a second skill catalog or a workflow
engine.

## Do not use

- Use `skill-creator` when the request is a reusable procedure or new skill.
- Use `AGENTS.md` or the later workspace-guidance owner for persistent project
  instructions.
- Use the later issue-execution owner for Issue lifecycle work.
- Use the later athena-review owner for a reusable review procedure.
- Do not create a role for a title, personality, or ordinary implementation
  task without a real isolation or configuration boundary.

## G0 necessity

Before editing, inspect the existing user and project agents and compare the
request against these owners:

1. native Codex behavior;
2. persistent `AGENTS.md` guidance;
3. a deterministic script or built-in tool;
4. an existing project or user skill;
5. a maintained upstream or plugin candidate;
6. a sibling, merge, or localize option;
7. ordinary parent instructions.

Record each alternative as `CHECKED`, `NOT_AVAILABLE`, or `NOT_RELEVANT`.
Only `CHECKED` alternatives need substantive evidence. Do not claim that an
unavailable catalog, plugin, or upstream candidate was inspected. Select the
smallest owner that explains the required independent context, judgment,
permission, model, tool, capability restriction, delegation, or return
boundary. If the difference is only procedure, return `NEEDS_SKILL`; if it is
only durable guidance, return `NEEDS_AGENTS_GUIDANCE`.

## Lifecycle

Support the requested mode without expanding it:

- `CREATE`: inspect collisions, choose `CREATE_ROLE`, `CLONE_AND_ADAPT`,
  `REUSE_EXISTING`, `NEEDS_SKILL`, `NEEDS_AGENTS_GUIDANCE`, or `BLOCKED`.
- `UPDATE`: change an existing role only for a demonstrated defect; return
  `UPDATE_ROLE`, preserve its authority, and verify the changed behavior.
- `MAINTAIN`: choose `UNCHANGED`, `SIMPLIFY_ROLE`, `MERGE_ROLES`,
  `LOCALIZE_ROLE`, `PROMOTE_USER_ROLE`, `RETIRE_ROLE`, `REJECT_AGENT`, or
  `BLOCKED` after checking provenance, collision, placement, resource use,
  runtime assumptions, and quality.

Use these explicit dispositions rather than hiding the decision behind a
generic mode label: `UPDATE_ROLE` is the repair outcome, `SIMPLIFY_ROLE` is
the bounded deletion/simplification outcome, `MERGE_ROLES` and
`LOCALIZE_ROLE` preserve the corresponding relationship, `PROMOTE_USER_ROLE`
handles a demonstrated user-scope move, `RETIRE_ROLE` removes an obsolete
role, and `REJECT_AGENT` records that a role is not warranted.
- `EVALUATE`: report criterion-level evidence and limitations; do not silently
  repair, self-accept, or promote canonical state.

Where a source is copied, record its repository, ref, path, license, blob
identity, and the adaptation boundary before changing it. Prefer a maintained
source over a rewrite; use `CREATE_FROM_SCRATCH_WITH_JUSTIFICATION` only when
no suitable source exists.

## Role contract

Keep `name`, `description`, and `developer_instructions` valid for standalone
role files. Make `description` a short routing surface: positive trigger,
reason to choose this role, and a negative boundary from `worker`, `explorer`,
retained siblings, ordinary parent work, and skills. Keep volatile catalogs
out of it.

Keep developer instructions separate from routing description. They should
state responsibility, authority, inputs, capability policy, delegation
limits, mutation/runtime expectations, stop conditions, and return shape.
Put reusable procedures in skills or references, not in the role shell. A
role cannot grant a skill or permission its parent does not expose; an absent
procedure is `NEEDS_SKILL`, not an invented capability.

## Qualification

Run deterministic structure and schema checks first, then test description,
developer instructions, capability binding, sibling collision, delegation,
scope, and runtime application independently. Keep these signals separate:

`discovery`, `explicit invocation`, `implicit activation`, `role selection`,
`role application`, `skill/reference/script process`, `artifact/action`,
`validation`, and `return/stop`.

Use `OBSERVED`, `FAIL`, `NOT_ASSESSED`, or `BLOCKED` for each signal. A valid
TOML file or plausible answer is not runtime proof. Do not weaken sandbox,
authority, depth, approval, or validation settings to make a case pass. Use
the repository-approved qualification lane recorded in
`references/runtime-qualification.md` and the qualification case manifest;
record the concrete model, reasoning effort, repetitions, and exact
limitations. The current lane is policy evidence, not a permanent skill
invariant.

Read the focused references only when needed:

- [role-contract.md](references/role-contract.md) for current fields and
  layer boundaries;
- [role-config-examples.md](references/role-config-examples.md) for minimal
  standalone and project-scope shapes;
- [runtime-qualification.md](references/runtime-qualification.md) for
  observable evidence and NOT_ASSESSED boundaries;
- [qualification-cases.yaml](references/qualification-cases.yaml) for the
  bounded routing and high-risk cases;
- [qualification-results.md](references/qualification-results.md) for the
  durable exact-run qualification summary;
- [qualification-receipts.jsonl](references/qualification-receipts.jsonl) for
  compact per-run evidence; validate it with
  `scripts/validate_qualification_receipts.py` rather than trusting summary
  counts;
- [qualification-evidence.jsonl](references/qualification-evidence.jsonl) for
  the compact durable binding that the validator recomputes for each receipt;
- [qualification-prompts.jsonl](references/qualification-prompts.jsonl) for
  the exact prompt variant IDs and hashes used by each partition;
- [qualification-exclusions.jsonl](references/qualification-exclusions.jsonl)
  for hashed, rejected-attempt provenance; excluded runs never count as
  behavioral passes;
- [provenance.md](references/provenance.md) for the pinned clone and file
  disposition record.

Return the target, disposition, changed paths, evidence, validation,
rollback, unresolved limitations, and the exact authority boundary. The
parent remains responsible for final acceptance and durable promotion.
