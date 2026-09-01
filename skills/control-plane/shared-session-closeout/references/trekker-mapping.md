# Trekker mapping

Trekker is optional local task state, not the source of truth.

- AI Labs goal → Trekker epic.
- `TASKS.md` item → Trekker task or subtask.
- `PLAN.md` dependency → Trekker dependency.
- Walkthrough evidence → Trekker comment or history note.
- Completed goal → completed epic only after canonical validation passes.

Do not copy credentials, raw session transcripts, or linked project contents
into Trekker. Treat `.trekker/trekker.db` as runtime data and exclude it from
the Codex control-plane Git allowlist unless a project explicitly approves it.
