---
name: install-project-link
description: Audit or create a reversible project link when an approved control-plane operation connects an existing external project; verify target, collision, scope, and rollback. Do not inspect or modify linked project contents.
metadata:
  last_reviewed: 2026-08-09
  review_interval_days: 90
---

# Install project link

## Contract

- **Trigger:** an approved workspace-to-project link operation is requested.
- **Inputs:** source, target, owner, link mode, and approval/rollback boundary.
- **Output:** audit result or reversible link with exact target and provenance.
- **Boundary:** links are pointers only; never traverse, copy, or mutate linked project contents.
- **Stop:** stop on collision, symlink escape, protected target, or ambiguous ownership.
- **Validation:** run `audit_link.py`, then the focused tests before any approved create operation.

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

Read the nearest applicable `AGENTS.md` plus the colocated script/test
contracts for any additional file-map or parameter guidance. Do not treat an
external workspace's path as portable package authority.
