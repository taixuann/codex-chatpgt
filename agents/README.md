# Franky agent adapters

This directory contains Codex runtime adapters. The canonical semantic roles
remain defined by the AI Labs role registry; these TOML files only describe
the local runtime boundary.

## Runtime metadata

Agent TOML files intentionally contain no runtime `version` field. Versioning
belongs to workflows, goal packages, promotion artifacts, and the change log;
the adapters are runtime role boundaries validated by their schema.

## Change logging

Agent changes must be recorded in [`CHANGELOG.md`](CHANGELOG.md) with the
reason, goal ID, workflow ID, changed paths, validation evidence, approval,
rollback, and the local Git change commit SHA. Franky install and maintenance
workflows update the changelog whenever an agent adapter changes.

Empty placeholder adapters are retained only when explicitly documented and
are not treated as active runtime agents.
## Capability and runtime materialization

The approved capability repertoire is bounded by `skills/AGENTS.md` and the
active task contract. It is not a persona-owned skill namespace and does not
route tasks by itself.
Explicit named-agent invocation and automatic capability-first routing remain
separate entry modes.

Codex custom-agent files may support `skills.config`, but the current installed
runtime probe established only configuration parsing. Native per-agent skill
enable/disable and native `@franky` dispatch remain `NOT_ASSESSED` until a
model turn exposes observable child-agent/skill-selection evidence. Franky
therefore uses explicit required-capability task packets as the v1 fallback.

The repository-owned global `[agents]` baseline is the TOML block in
`agents/AGENTS.md`. Do not copy it over a user's local config without an
explicit runtime-change decision.
