# Provenance and component audit

## Primary baseline

- Repository: `openai/codex`
- Ref: `dee21ec1bc26cdf9f3c4d77a17706cd19dcf05de`
- Source path: `codex-rs/skills/src/assets/samples/skill-creator/`
- Maintained reference: https://github.com/openai/codex/tree/dee21ec1bc26cdf9f3c4d77a17706cd19dcf05de/codex-rs/skills/src/assets/samples/skill-creator/
- Runtime guidance: https://developers.openai.com/codex/skills
- Evaluation guidance: https://developers.openai.com/blog/eval-skills
- License: Apache-2.0, retained in `license.txt`
- Baseline commit: `bb288fd` in this repository

The baseline was copied before adaptation and its nine retained files matched
the pinned Git blob IDs recorded in Issue #103. The baseline remains
recoverable and the adaptation remains diffable against it.

Retained unchanged baseline blobs:

- `scripts/generate_openai_yaml.py`, `870eefcea9bd0184806b8eb305526e883d2f7241`
- `scripts/quick_validate.py`, `e27023ece4bd259ef36560e19995eec7b6a345bf`
- `license.txt`, `d645695673349e3947e8e5ae42332d0ac3164cd7`

Bounded adaptations retain the recoverable baseline blob and change only the
approved #121 contract surface:

- Upstream baseline marker: `scripts/init_skill.py`, `2ed2fa3125c720fcce60a29f3dd82d04b14d9fa0`
- `scripts/init_skill.py`, baseline blob `2ed2fa3125c720fcce60a29f3dd82d04b14d9fa0`:
  runtime metadata is omitted by default and generated only for explicit
  interface overrides.
- `scripts/validate_eval_cases.py`: action evidence is recomputed from the
  runtime record before comparison; the baseline remains recoverable from
  commit `bb288fd`.

## Component disposition

| Component | Disposition | Reason |
| --- | --- | --- |
| SKILL.md | ADAPT_TO_121 | Four peer actions; EVALUATE is shared and MAINTAIN is retired. |
| workflows/create.md | ADD_FROM_REVIEWED_BASELINE | Canonical CREATE procedure for new owned skills. |
| workflows/update.md | ADD_FROM_REVIEWED_BASELINE | Canonical UPDATE procedure for pinned existing targets. |
| workflows/install.md | OPERATIONAL | Faithful materialization path with pinned source, canonical source/selected/installed digests, exact per-file receipt, ownership, and safe uninstall evidence; redesign routes to CREATE or UPDATE. |
| workflows/audit.md | ROUTE_ONLY | Read-only assessment path; no mutation or acceptance. |
| architecture.md, authoring.md, discovery.md | ADD_FROM_REVIEWED_BASELINE | Ownership, package shape, and placement constraints. |
| source-strategy.md, review.md, validation.md | ADD_FROM_REVIEWED_BASELINE | Source identity, review independence, and deterministic checks. |
| evaluation.md, test-environment.md, qualification.md | ADD_FROM_REVIEWED_BASELINE | Evaluation partitions, runtime boundaries, and terminal evidence. |
| routing.md | ADAPT_TO_121 | Explicit four-action routing and fail-closed ambiguity cases. |
| provenance.md | SELF_ONLY | Records the exact source and adaptation decisions for this package. |
| initializer and validator scripts | ADAPT_WITH_BASELINE | The initializer now avoids unsupported runtime metadata by default; the evaluator now fail-closes on incomplete action evidence. Both changes are bounded to #121 and retain the upstream baseline identity above. |
| license.txt | KEEP_UNCHANGED | Required attribution and license terms. |
| evals/cases.yaml and evaluator scripts | ADAPT | Action routing, paired evaluation, held-out cases, and qualification gates. |

The prior MAINTAIN peer action and old mode-specific references were removed
because Issue #121 defines UPDATE as the owned mutation path and EVALUATE as a
shared capability. Legacy source and donor material remains provenance
evidence, not an installation target.

## Bounded external donors

Anthropic anthropics/skills at
41bbe19d1a1a7eaab5e7bb9050a417e5c6cffc8f, path skills/skill-creator/,
Apache-2.0, was inspected as reference only. No Anthropic files or
Claude-specific runtime assumptions are copied.

SkillNet and Microsoft SkillOpt were consulted only for bounded evaluation
ideas such as coexistence, executability, rejected edits, and held-out
validation. They are not runtime dependencies.
