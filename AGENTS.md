# Codex Franky workbench

This directory is the Codex-first Franky control-plane workbench. Use the two
registered entrypoint workflows under `workflows/franky/`:

- `franky-install.yaml` routes one component request to an install branch.
- `franky-maintenance.yaml` audits, updates, validates, versions, logs, and
  locally commits approved control-plane changes.

Agents must select a workflow before invoking Franky skills. The nested
pipelines are the only allowed branch implementations. Keep `.system`, logs,
sessions, caches, databases, credentials, config, and linked project contents
outside the Git allowlist. Never push automatically.
