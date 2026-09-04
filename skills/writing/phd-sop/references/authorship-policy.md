# Authorship, AI-assistance, detector, and watermark boundary

Resolve the most specific target-program/application policy before drafting or rewriting.

## Policy states

- `UNKNOWN`
- `DRAFTING_ALLOWED`
- `EDITING_ONLY`
- `BRAINSTORMING_ONLY`
- `PROHIBITED`
- `DISCLOSURE_REQUIRED`

Program/application-specific policy overrides generic institutional guidance. Do not infer a permissive policy from silence.

## Operation mapping

| Policy | Draft | Rewrite substantive prose | Diagnose / score | Brainstorm |
| --- | --- | --- | --- | --- |
| DRAFTING_ALLOWED | yes | yes | yes | yes |
| EDITING_ONLY | no new substantive content | line/clarity edits only | yes | yes |
| BRAINSTORMING_ONLY | no | no | yes | yes |
| PROHIBITED | no | no | no application-text authorship | policy-safe general guidance only |
| DISCLOSURE_REQUIRED | only within stated policy | only within stated policy | yes | yes |
| UNKNOWN | unresolved when material | unresolved when material | yes | yes |

## Three different concepts

1. **Generator watermark**: signal embedded during generation/sampling. A prose linter cannot establish or reliably remove it.
2. **AI-text detector/stylometry**: probabilistic authorship inference. It is not a writing-quality metric and can be biased or unstable.
3. **AI-ish prose patterns**: genericity, formulaic transitions, manufactured reflection, symmetry, or voice drift. These are editing signals only, not authorship proof.

Do not produce an AI-likeness/humanity score. Do not optimize perplexity, burstiness, punctuation, or detector scores. Do not intentionally insert errors or awkwardness. Do not "native-speakerize" a non-native writer merely to avoid suspicion.

The defense for application integrity is provenance: user facts, explicit chronology/ownership, user-originated or approved voice samples, policy compliance, and a final text the applicant can explain and defend.
