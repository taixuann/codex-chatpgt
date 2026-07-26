---
name: franky-maintenance
description: Audit and maintain the Franky Codex control plane across skills, agents, workflows, guidance, TOML, configuration, cron, git state, links, and registries. Use for report-first operator maintenance.
---

# Franky maintenance

Start with a read-only inventory. Inspect only the approved control-plane scope.

1. Inventory relevant skill metadata, agent TOML, workflow YAML, AGENTS.md
   files, configuration, scheduler and cron state, git state, links, and
   registries, including the AI Labs promotion branch or export state.
2. Classify findings as healthy, missing, stale, conflicting, or unsafe.
3. Run deterministic validators before model-level interpretation.
4. Produce a report with exact paths, evidence, impact, and recommended next
   action.
5. Apply changes only after human approval and record a walkthrough.
6. Treat promotion preparation as a separate report with source hashes,
   destination registry changes, branch/update scope, and rollback metadata.

Never follow or modify linked project contents. Never treat a report as
permission to mutate state.
