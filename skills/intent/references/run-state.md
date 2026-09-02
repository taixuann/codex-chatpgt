# Intent run state

`intentctl` writes one bounded `intent_run` YAML document. Its stable fields are
`schema_version`, `origin`, `workspace`, `depth`, `profile`, `stages`,
`evidence`, `claims`, `decisions`, `relationships`, `unknowns`,
`contradictions`, `blockers`, `intent`, `orientation`, `handoff`, and `trust`.

`intent` is the canonical boundary projection (`objective`, `why`,
`success_criteria`, `scope`, and `out_of_scope`) consumed by the plan bridge.
The fresh-context command derives recovery coverage from these fields,
workspace anchor, evidence, relationships, decisions, unknowns, and trust; it
does not trust caller-supplied boolean scores.

Stage requiredness comes only from `requirement-matrix.yaml`; stage statuses are
`passed`, `skipped_with_reason`, `not_applicable`, `blocked`, or `failed`.
Confirmed claims require evidence IDs, and every evidence/claim reference must
resolve. `intentctl readiness` is the machine gate; semantic judgment remains
in the root procedure and behavioral review.
