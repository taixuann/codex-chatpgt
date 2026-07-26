---
name: franky-project-linker
description: Create and verify reversible links from a framework workspace to selected shared Codex skills while enforcing workspace boundaries and avoiding linked project contents. Use for framework skill-link setup.
---

# Franky project linker

Use explicit source and target paths supplied by the user or promotion
manifest. Do not infer broad workspace targets.

1. Verify the source is an approved Codex skill directory.
2. Verify the target framework is a trusted workspace and the target does not
   already contain an unrelated file or directory.
3. Refuse links into `.system`, credentials, project data, or broad roots.
4. Create only an approved symlink or copy and record its previous state.
5. Re-read the resulting link and report a rollback command.

Use `scripts/audit_link.py` for report-only checks before any write.
