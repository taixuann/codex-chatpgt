# Minimal role shapes

Use the smallest standalone adapter that expresses a real runtime boundary.

```toml
name = "example-role"
description = "Route bounded work here when this role's context or permission boundary is required; do not use it for ordinary parent work or reusable procedures."
model = "gpt-5.6-luna"
model_reasoning_effort = "medium"
sandbox_mode = "read-only"
developer_instructions = """
Own only the bounded responsibility supplied by the parent. State the
allowed inputs, authority, capabilities, mutation limits, stop conditions,
and return shape. Use existing skills for procedures; never invent a missing
capability or self-accept a consequential result.
"""
```

For a project-scoped adapter, keep the same fields and bind it to the project
through the host's supported configuration. Do not add a role solely to hold
workflow prose, a personality, or a volatile catalog.
