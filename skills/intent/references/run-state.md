# Intent run state

`intentctl` writes one bounded `intent_run` YAML document. Its stable fields are
`schema_version`, `origin`, `workspace`, `depth`, `profile`, `stages`,
`evidence`, `claims`, `decisions`, `relationships`, `unknowns`,
`contradictions`, `blockers`, `intent`, `orientation`, `handoff`, and `trust`.

`intent` is the canonical boundary projection (`objective`, `why`,
`current_state`, `target_state`, `success_criteria`, `scope`, and
`out_of_scope`) consumed by the plan bridge. Relationships remain explicit in
the run state alongside claims and evidence.
The fresh-context command derives recovery coverage from these fields,
workspace anchor, evidence, relationships, decisions, unknowns, and trust; it
does not trust caller-supplied boolean scores.

Stage requiredness comes only from `requirement-matrix.yaml`; stage statuses are
`passed`, `skipped_with_reason`, `not_applicable`, `blocked`, or `failed`.
Confirmed claims require evidence IDs, and every evidence/claim reference must
resolve. `procedure_trace.expected` is derived from
`reference-selection.yaml` plus origin/depth and material conditions;
`procedure_trace.observed` records the bounded outputs/evidence actually
produced. It is not a claim that a model literally read file tokens, and
readiness rejects required references that remain unobserved. Each
procedure-bound evidence entry must also list the observable IDs declared by
that reference; matching a procedure name alone is insufficient.

For focused/deep handoff, `intentctl materialize` writes the canonical
`intent` mapping into the shared packet's `intent.md` frontmatter. Fresh-context
recovery and readiness read that artifact and require an exact binding to the
run-state intent, so a blank or stale plan-facing packet cannot pass G6.
Derived trust and recovery metadata are intentionally kept outside that
identity payload; updating recovery completeness therefore cannot make a
correctly materialized intent stale.

`intentctl readiness` is the capability's deterministic readiness
recommendation. The canonical operating workflow/task contract owns the
lifecycle transition to Plan; semantic judgment remains in the bounded
procedure and independent behavioral review.

For every required stage, readiness also requires at least one stage evidence
ID whose evidence entry declares the same `procedure` name. Copying expected
reference names into `procedure_trace.observed` without procedure-bound output
therefore cannot satisfy the gate.
