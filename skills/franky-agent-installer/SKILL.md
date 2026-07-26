---
name: franky-agent-installer
description: Install or update Codex custom-agent TOML with scope, schema, model, sandbox, collision, dependency, and approval checks. Use for custom-agent lifecycle work.
---

# Franky agent installer

Treat custom-agent files as runtime adapters, not as the canonical role
registry.

1. Decide personal scope (`~/.codex/agents/`) versus project scope
   (`.codex/agents/`). Prefer project scope for AI Labs-specific roles.
2. Require `name`, `description`, `model`, `model_reasoning_effort`,
   `sandbox_mode`, and `developer_instructions` for AI Labs runtime adapters.
3. Check filename/name consistency, duplicate names, sandbox boundaries, and
   subagent restrictions before writing.
4. Preserve the canonical semantic role in `ai-labs/ops/agents/agents.yaml`;
   do not silently rename or replace it.
5. Validate candidate files with `scripts/validate_agent_toml.py` and report a
   reversible installation plan.

Use the optional `templates/agent.toml` as the adapter template. Copy it to the
target scope, replace the identity and role-specific instructions, then validate
the instantiated file; never inspect an arbitrary installed agent as a template.
The template defaults to configurable medium-tier `gpt-5.4-mini` with medium
reasoning. Routine operator work should not use `xhigh`.

Copy `templates/agent.toml`, set `name` to the filename stem, fill the required
runtime fields, and run `scripts/validate_agent_toml.py <path>`. Report the
source template, destination, validation result, and rollback before an
approved write.

Do not write global adapters or change credentials, MCP configuration, or
models without explicit approval.
