# Intent readiness gates

The canonical operating workflow/task contract owns the durable transition and
six gates. Intent supplies bounded evidence and a readiness recommendation:

1. `G1_ORIGIN` — source is exactly a user request or GitHub Issue.
2. `G2_CONTEXT` — workspace and relevant current state are anchored.
3. `G3_EVIDENCE` — material claims are classified and traceable.
4. `G4_AUTHORITY` — user decisions are resolved or explicitly blocked.
5. `G5_BOUNDARY` — objective, scope, exclusions, and success are understood.
6. `G6_HANDOFF` — the bounded packet is sufficient for a fresh planner.

Intent must not independently promote lifecycle state. The workflow may use its
recommendation as `PLAN_READY` evidence only after deterministic blockers are
clear. Blockers include missing
required stages, invalid skip reasons, naked confirmed claims, unresolved
contradictions or authority blockers, missing handoff/recovery evidence, and
unacceptable freshness or integrity signals.
