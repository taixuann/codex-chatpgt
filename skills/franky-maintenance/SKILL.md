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
3. Run deterministic validators before model-level interpretation. For
   workflow/job contracts, run `scripts/validate_io_cache.py`; omitted cache
   policy is deterministically treated as `no-cache`.
4. Produce a report with exact paths, evidence, impact, and recommended next
   action.
5. Apply changes only after human approval. Record routine local mutations in
   `~/.codex/ops/changes/YYYY/CHG-YYYYMMDD-NNN/change.yaml`; use AI Labs
   walkthroughs only for full architectural goal packages.
6. Treat promotion preparation as a separate report with source hashes,
   destination registry changes, branch/update scope, and rollback metadata.

Never follow or modify linked project contents. Never treat a report as
permission to mutate state.

When inputs, outputs, or cache policy changes, include an overview/impact check:
identify consumers/producers and cross-component references in the selected
control-plane scope, and return unresolved references to a human.
