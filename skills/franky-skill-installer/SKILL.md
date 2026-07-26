---
name: franky-skill-installer
description: Install or update Codex skills with explicit global or project scope, dependency checks, collision protection, metadata validation, and rollback evidence. Use for skill installation or skill-package maintenance.
---

# Franky skill installer

Use the installed `skill-installer` for public GitHub skill sources and
`skill-creator` for local skill creation. Preserve source provenance.

1. Resolve the requested source and destination scope before writing.
2. Refuse to overwrite an existing package unless the user explicitly requests
   an update and a rollback path is recorded.
3. Never edit or replace `/Users/tai/.codex/skills/.system/`.
4. Validate `SKILL.md` frontmatter, `agents/openai.yaml`, dependencies, and
   package naming before installation completes.
5. Report installed paths, source/ref, validation evidence, and rollback steps.

Use top-level `franky-*` names for Franky packages. Keep audits read-only and
require approval before writes outside the active Codex workbench.
