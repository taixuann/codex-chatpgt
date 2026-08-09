---
name: install-project-link
description: Create and verify reversible links from the Codex workbench to approved framework paths without traversing project contents.
---

# Install project link

Create or verify a requested link only after the source and target are explicit.
Never infer a broad workspace, link into `.system`, credentials, or project
contents, and never repair a link by guessing a new target.

## Execution Steps

1. Inventory the source, target, owner, and requested link mode.
2. Run `scripts/audit_link.py` before any write and reject collisions or
   protected paths.
3. Create only the approved symlink with
   `scripts/create_project_link.py <source> <target> --workspace-root <root> --apply`.
4. Re-read the result and report a reversible rollback command. Do not
   auto-heal a moved target without explicit approval.

Refer to [AGENTS.md](file:///Users/tai/ai-labs/ops/skills/franky/install-project-link/AGENTS.md) for the complete file map and parameter guidance.
