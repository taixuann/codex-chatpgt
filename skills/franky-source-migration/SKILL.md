---
name: franky-source-migration
description: Audit and normalize Claude Code, OpenCode, or Antigravity artifacts into Codex when an explicit migration is requested; inventory, map collisions, and prepare approval-gated changes. Do not edit source tools or silently deploy.
metadata:
  last_reviewed: 2026-08-09
  review_interval_days: 90
---

# Franky source migration

## Contract

- **Trigger:** an explicitly named external agent-tool source must be migrated into Codex.
- **Inputs:** source root, artifact types, target Codex scope, compatibility constraints, and approval owner.
- **Output:** inventory, normalized mapping, collision findings, and bounded migration proposal.
- **Boundary:** source files remain read-only; no silent multi-platform sync or deployment.
- **Stop:** stop on ambiguous source identity, collision, unsupported runtime semantics, or missing approval.
- **Validation:** run source detection/inventory and migration validators before any apply step.

Use this skill as the source-adapter and merge-analysis capability inside the
Franky maintenance workflow. Keep the work inside the Codex control plane;
never edit the source tool's files.

## Operating contract

1. Detect the source tool from explicit user scope and recognizable files. Do
   not infer a source from a filename alone when multiple tools are present.
2. Inventory before writing. Record source root, artifact path, artifact type,
   active/inactive status, content hash, and provenance.
3. Normalize compatible artifacts into the canonical categories: instruction,
   skill, agent, command, hook, MCP, or manual-review item.
4. Compare normalized targets against existing Codex files. Never overwrite a
   collision; propose keep, merge, rename, or manual-review outcomes.
5. Exclude `.system`, credentials, sessions, memories, linked projects,
   unrelated source repositories, and runtime databases.
6. Produce an exact migration manifest and digest. Apply only the manifest
   bound to the top-level Franky approval gate.
7. Validate generated artifacts and report unsupported behavior explicitly.

## Source handling

Read the relevant source reference before inspecting that source:

- Claude Code: [references/claude-code.md](references/claude-code.md)
- OpenCode: [references/opencode.md](references/opencode.md)
- Antigravity: [references/antigravity.md](references/antigravity.md)

Use `scripts/detect_sources.py` for deterministic source discovery and
`scripts/inventory_sources.py` for a read-only artifact inventory. Use
`scripts/validate_migration.py` on the final manifest before local finalization.

## Merge policy

- Prefer a new Codex skill package when the source artifact is reusable and
  self-contained.
- Preserve source provenance in the manifest and generated package notes.
- Convert only semantics that can be represented safely in Codex.
- Mark provider-specific hooks, extensions, plugins, and ambiguous agent
  behavior as `manual_review`; do not silently approximate them.
- Keep migration reports scoped by source root and use concise rows for added,
  review-required, and not-added artifacts.
