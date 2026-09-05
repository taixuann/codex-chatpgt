# CREATE

Use this reference when a request may justify a new reusable skill. Start with
the capability, not a file.

## Decision sequence

`REQUEST → NECESSITY → DISCOVERY → SOURCE SELECTION → CLONE → BASELINE
REPRODUCTION → ADAPT → DESCRIPTION → STRUCTURE → ROUTING → BEHAVIOR → REVIEW`

1. State the repeated capability and concrete user examples.
2. Check whether the need belongs in `AGENTS.md`, an existing skill, a
   deterministic script, a native Codex feature, or a project-local procedure.
3. Inspect local, project-local, installed/global, and maintained upstream
   candidates. Check equivalence, sibling overlap, composition, ownership, and
   global versus local placement.
4. Prefer `USE_EXISTING`, `UPDATE_EXISTING`, `CLONE_AND_ADAPT`, `MERGE`,
   `LOCALIZE`, `DISABLE_IMPLICIT`, `RETIRE`, or `REJECT` over new content.
5. If a maintained baseline exists, copy it unchanged first, record repository,
   ref, path, license, and hashes, then make the smallest adaptation. Use
   `CREATE_FROM_SCRATCH_WITH_JUSTIFICATION` only when no suitable baseline
   exists and record why.
6. Validate the description, structure, resource necessity, routing, behavior,
   and provenance before asking for independent review.

Project/domain-specific skills default to `<repo>/.agents/skills/`; global
placement needs demonstrated cross-project reuse. Creating a skill is never a
substitute for first checking an existing reference or simpler owner.
