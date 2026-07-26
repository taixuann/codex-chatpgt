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

Do not write global adapters or change credentials, MCP configuration, or
models without explicit approval.
