# Adaptive intent depth

Start at `light`, use `focused` for the normal bounded investigation, and use
`deep` only when the evidence warrants it.

Promote light to focused when source claims contradict evidence, multiple
relevant surfaces or an active related Issue/PR appear, or acceptance/scope
cannot be recovered cheaply. Promote focused to deep for material cross-repo
ownership, architecture-contract conflict, substantial stale/superseded state,
high-consequence work, or repeated fresh-context recovery failure.

Do not use arbitrary file-count, token-count, or time thresholds.
