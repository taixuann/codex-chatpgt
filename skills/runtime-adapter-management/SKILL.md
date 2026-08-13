---
name: runtime-adapter-management
description: Validate and install a Codex agent profile when an approved control-plane change adds or updates a runtime adapter; check schema, scope, collision, sandbox, dependencies, and approval. Do not use for role design or ordinary task delegation.
metadata:
  last_reviewed: 2026-08-09
  review_interval_days: 90
---

# Runtime adapter management

## Contract

- **Trigger:** an approved runtime-adapter installation or update is requested.
- **Inputs:** target TOML, destination scope, canonical role mapping, and approval context.
- **Output:** validated adapter, collision/dependency findings, and exact deployment paths.
- **Boundary:** adapters implement canonical roles; they do not rename roles or decide task routing.
- **Stop:** stop on role collision, unsafe sandbox, missing approval, or protected destination.
- **Validation:** run `validate_agent_toml.py` and confirm filename/name, required fields, and write scope.

Treat custom-agent files as runtime adapters, not as the canonical role
registry.

1. Decide personal scope (`~/.codex/agents/`) versus project scope
   (`.codex/agents/`). Prefer project scope for repository-specific adapters.
2. Require the adapter contract fields (`name`, `description`, `model`,
   `model_reasoning_effort`, `sandbox_mode`, and `developer_instructions`)
   for the selected runtime; do not hardcode a model or runtime in the skill.
3. Check filename/name consistency, duplicate names, sandbox boundaries, and
   subagent restrictions before writing.
4. Preserve the canonical semantic role in the authoritative role registry;
   do not silently rename or replace it.
5. Validate candidate files with `scripts/validate_agent_toml.py` and report a
   reversible installation plan.

Use the optional `templates/agent.toml` as the adapter template. Copy it to the
target scope, replace the identity and role-specific instructions, then validate
the instantiated file; never inspect an arbitrary installed agent as a template.
The template contains placeholders only. The caller supplies a supported model
and reasoning setting from the selected runtime/task contract; the skill does
not define model-routing policy.

Copy `templates/agent.toml`, set `name` to the filename stem, fill the required
runtime fields, and run `scripts/validate_agent_toml.py <path>`. Report the
source template, destination, validation result, and rollback before an
approved write.

Do not write global adapters or change credentials, MCP configuration, or
models without explicit approval.
