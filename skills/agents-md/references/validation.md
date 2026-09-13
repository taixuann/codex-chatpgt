# Validation

Run deterministic checks first, then only the behavioral cases that can change
the decision:

1. frontmatter, paths, references, and size;
2. root/CWD chain and override precedence;
3. reachable Skill roots and same-name collisions;
4. stale authority markers and broken relative links;
5. representative setup, maintain, audit, and no-write outcomes;
6. realistic AGENTS × Skill coexistence from supported CWDs.

Use `audit.py --self-test` for the local deterministic smoke. Its report binds
the root, CWD, selected sources, reachable roots, content hashes, and a
fingerprint. It does not claim host loading or behavioral adherence.

Use these result states:

- `PASS`: the requested filesystem invariant and report contract were observed;
- `FAIL`: an observed invariant is wrong;
- `NOT_ASSESSED`: the host does not expose the required runtime signal.

For model or host qualification, keep discovery, explicit invocation,
implicit activation, Skill loading, process trace, artifact delta, and final
behavior as separate fields. A model's answer cannot prove Skill selection.
Record before/after snapshots for the operation workspace only; exclude
temporary runtime caches. Do not treat a clean static report as proof that
Codex loaded or followed the chain.

Independent review, when required by the owning Issue, must use a fresh exact
revision and return findings plus limitations. It is not replaced by the
author's self-review or by a caller-provided green flag.
