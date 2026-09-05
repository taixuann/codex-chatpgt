# Provenance and component audit

## Primary baseline

- Repository: `openai/codex`
- Ref: `dee21ec1bc26cdf9f3c4d77a17706cd19dcf05de`
- Source path: `codex-rs/skills/src/assets/samples/skill-creator/`
- License: Apache-2.0, retained in `license.txt`
- Baseline commit: `bb288fd` in this repository

The baseline was copied before adaptation and its nine files matched the
pinned Git blob IDs recorded in Issue #103. The baseline is therefore
recoverable and the adaptation remains diffable against it.

## Secondary donor

Anthropic `anthropics/skills` at
`41bbe19d1a1a7eaab5e7bb9050a417e5c6cffc8f`, path `skills/skill-creator/`,
Apache-2.0, was inspected as reference only. No Anthropic files or
Claude-specific runtime assumptions are copied. Its bounded ideas are
represented by the compact trigger/behavior case set and independent-review
boundary required here; the OpenAI baseline remains dominant.

## Component disposition

| Component | Disposition | Reason |
| --- | --- | --- |
| `SKILL.md` | KEEP_WITH_SMALL_ADAPTATION | Add lifecycle, placement, and review boundaries. |
| `scripts/*` | KEEP_UNCHANGED | Upstream deterministic initializer, metadata generator, and validator. |
| `references/openai_yaml.md` | KEEP_UNCHANGED | Documents the retained UI/policy file. |
| `agents/openai.yaml` | KEEP_WITH_SMALL_ADAPTATION | UI identity plus explicit-only policy is useful for this catalog; implicit routing remains unproven. |
| `assets/*` | KEEP_UNCHANGED | Upstream UI assets used by the retained metadata. |
| `license.txt` | KEEP_UNCHANGED | Required attribution and license terms. |
| `references/lifecycle.md` | ADD | Small mode-specific procedure not present in the baseline. |
| `references/provenance.md` | ADD | Makes source, donor, and component decisions auditable. |
| `evals/cases.yaml` | ADD | Compact rerunnable coverage for routing and lifecycle behavior. |
| `scripts/validate_eval_cases.py` | ADD | Deterministically checks that required cases remain present. |
