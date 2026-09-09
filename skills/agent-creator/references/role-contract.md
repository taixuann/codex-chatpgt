# Role contract

A standalone custom agent is a configuration layer for a spawned session, not
a replacement for the parent. Current native fields are `name`, `description`,
and `developer_instructions`; optional fields are supported session settings
such as `model`, `model_reasoning_effort`, `sandbox_mode`, `mcp_servers`, and
`skills.config` when the installed runtime accepts them.

Use the current Codex source and runtime as authority. The Issue #105 audit
anchor is `openai/codex@ac192cd7937b0d73edc6dffe009940ae53782dd4`. The installed
CLI used for this work is recorded in `provenance.md`; upstream drift must be
reported rather than guessed.

## Ownership boundaries

- `AGENTS.md` owns persistent operating and delegation guidance.
- An agent owns one bounded role, context, model, tool, permission, or return
  boundary.
- A skill owns reusable procedure and expertise.
- A tool or MCP server owns an external action/context surface.

Do not put a skill's step-by-step workflow, a volatile installed-skill list,
or a general lifecycle engine in `developer_instructions`.

## Description

Evaluate `description` independently from `developer_instructions`. It must
front-load when the parent should select the role, why the role is distinct,
and when a built-in or sibling role, skill, or parent behavior is preferable.
Test direct, indirect, noisy, context-heavy, adjacent-negative, built-in
sibling, custom sibling, and mixed-responsibility prompts.

## Developer instructions

Check these dimensions without requiring ceremonial headings:

1. responsibility and authority;
2. input and task contract;
3. skill/tool policy;
4. delegation and depth limits;
5. mutation and runtime expectations;
6. stop/escalation conditions;
7. return contract;
8. no procedure duplication, stale catalog, or global-policy leakage.

## Capabilities and scope

Role-side capability entries may restrict supported capabilities. They are not
evidence that a role can grant a missing skill or override parent authority.
Prove user scope (`~/.codex/agents`) and project scope (`.codex/agents`)
separately. If the host does not expose a required discovery, application,
or enforcement signal, mark that signal `NOT_ASSESSED`.
