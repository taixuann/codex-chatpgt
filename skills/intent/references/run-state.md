# Intent run state

`intentctl` writes one bounded `intent_run` YAML document. Its stable fields are
`schema_version`, `origin`, `workspace`, `depth`, `profile`, `stages`,
`evidence`, `claims`, `decisions`, `unknowns`, `contradictions`, `blockers`,
`orientation`, `handoff`, and `trust`.

Stage requiredness comes only from `requirement-matrix.yaml`; stage statuses are
`passed`, `skipped_with_reason`, `not_applicable`, `blocked`, or `failed`.
Confirmed claims require evidence IDs, and every evidence/claim reference must
resolve. `intentctl readiness` is the machine gate; semantic judgment remains
in the root procedure and behavioral review.
