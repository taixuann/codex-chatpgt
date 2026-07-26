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
