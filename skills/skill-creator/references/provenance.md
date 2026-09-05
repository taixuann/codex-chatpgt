# Provenance and component audit

## Primary baseline

- Repository: `openai/codex`
- Ref: `dee21ec1bc26cdf9f3c4d77a17706cd19dcf05de`
- Source path: `codex-rs/skills/src/assets/samples/skill-creator/`
- Maintained reference: `https://github.com/openai/codex/tree/dee21ec1bc26cdf9f3c4d77a17706cd19dcf05de/codex-rs/skills/src/assets/samples/skill-creator/`
- Runtime guidance: `https://developers.openai.com/codex/skills`
- Evaluation guidance: `https://developers.openai.com/blog/eval-skills`
- License: Apache-2.0, retained in `license.txt`
- Baseline commit: `bb288fd` in this repository

The baseline was copied before adaptation and its nine files matched the
pinned Git blob IDs recorded in Issue #103. The baseline is therefore
recoverable and the adaptation remains diffable against it.

Retained unchanged baseline blobs:

- `scripts/generate_openai_yaml.py`, `870eefcea9bd0184806b8eb305526e883d2f7241`
- `scripts/init_skill.py`, `2ed2fa3125c720fcce60a29f3dd82d04b14d9fa0`
- `scripts/quick_validate.py`, `e27023ece4bd259ef36560e19995eec7b6a345bf`
- `license.txt`, `d645695673349e3947e8e5ae42332d0ac3164cd7`

## Secondary donor

Anthropic `anthropics/skills` at
`41bbe19d1a1a7eaab5e7bb9050a417e5c6cffc8f`, path `skills/skill-creator/`,
Apache-2.0, was inspected as reference only. No Anthropic files or
Claude-specific runtime assumptions are copied. Its bounded ideas are
represented by the compact trigger/behavior case set and independent-review
boundary required here; the OpenAI baseline remains dominant.
Maintained reference: `https://github.com/anthropics/skills/tree/41bbe19d1a1a7eaab5e7bb9050a417e5c6cffc8f/skills/skill-creator/`.

## Component disposition

| Component | Disposition | Reason |
| --- | --- | --- |
| `SKILL.md` | KEEP_WITH_SMALL_ADAPTATION | Add only a compact lifecycle pointer; detailed modes stay in the reference. |
| `scripts/init_skill.py`, `scripts/generate_openai_yaml.py`, `scripts/quick_validate.py` | KEEP_UNCHANGED | Upstream deterministic initializer, metadata generator, and validator. |
| `references/openai_yaml.md` | REMOVE_AS_UNNECESSARY | Its only consumer, the removed UI metadata file, is not retained. |
| `agents/openai.yaml` | REMOVE_UNPROVEN | No current runtime consumer was demonstrated; native loading and dispatch remain `NOT_ASSESSED`. |
| `assets/*` | REMOVE_AS_UNNECESSARY | These assets served only the removed UI metadata. |
| `license.txt` | KEEP_UNCHANGED | Required attribution and license terms. |
| `references/create.md`, `references/update.md`, `references/maintain.md`, `references/evaluate.md`, `references/routing.md` | ADD_FROM_REVIEWED_BASELINE | Mode-specific progressive disclosure derived from the prior lifecycle reference and bounded donor concepts. |
| `references/provenance.md` | ADD | Makes source, donor, and component decisions auditable. |
| `evals/cases.yaml` | ADAPT | Adds eight gates, including necessity, held-out/regression partitions, routing negatives, and paired cases to the existing case contract. |
| `scripts/validate_eval_cases.py` | ADAPT | Extends the existing validator with an isolated `.agents/skills` fixture, paired runs, routing metrics, and validation-gated comparison. |

The upstream UI metadata, its reference, image assets, and invocation adapter
were removed because no successful current-runtime consumer was demonstrated.
The package is selected through the repository's explicit task/PR scope; native
loading and dispatch are still `NOT_ASSESSED`, not runtime acceptance.

## Bounded external donors

The following references were inspected for gaps in the existing OpenAI clone;
their tools and runtime assumptions are not vendored:

- SkillNet, `https://github.com/zjunlp/SkillNet`: relationship checks such as
  `similar_to`, `compose_with`, and `depend_on`, plus safety/completeness/
  executability/maintainability/cost evaluation dimensions.
- Microsoft SkillOpt, `https://github.com/microsoft/SkillOpt`: bounded
  add/delete/replace edits, rejected-edit feedback, and held-out validation
  before accepting a candidate skill.

Only these bounded ideas are adapted in the internal references and evaluator;
the repository does not add SkillNet or SkillOpt as a runtime dependency.
