# Authorship, AI-assistance, detector, and watermark boundary

Resolve the most specific target-program/application policy before drafting, rewriting, or reviewing application text when that policy governs AI assistance.

## Policy model

Do not collapse permission and disclosure into one enum.

### Assistance level

- `UNKNOWN`
- `DRAFTING_ALLOWED`
- `EDITING_ONLY`
- `BRAINSTORMING_ONLY`
- `PROHIBITED`

### Disclosure obligation

- `UNKNOWN`
- `NOT_REQUIRED`
- `REQUIRED`

### Attestation obligation

- `UNKNOWN`
- `NONE`
- `REQUIRED`

Also record the exact allowed/prohibited operations from the source policy when wording is more specific than these coarse labels.

Program/application-specific policy overrides generic institutional guidance. Do not infer a permissive policy from silence.

## Operation rules

- `DRAFTING_ALLOWED`: substantive drafting is permitted only to the extent the actual policy says so.
- `EDITING_ONLY`: do not author new substantive claims, stories, or paragraphs; preserve user-authored content and restrict edits to the allowed scope.
- `BRAINSTORMING_ONLY`: organize questions/ideas or provide general feedback; do not compose final application prose.
- `PROHIBITED`: do not use the capability on application text beyond policy-safe general guidance.
- `UNKNOWN`: surface unresolved policy status when it materially affects the requested operation.
- `disclosure=REQUIRED`: surface the obligation; do not imply it was satisfied.
- `attestation=REQUIRED`: do not help create a false attestation or silently proceed when the requested operation conflicts with it.

A policy may, for example, allow editing **and** require disclosure. Those facts must coexist rather than one overwriting the other.

## Three different concepts

1. **Generator watermark**: signal embedded during generation/sampling. A prose linter cannot establish or reliably remove it.
2. **AI-text detector/stylometry**: probabilistic authorship inference. It is not a writing-quality metric and can be biased or unstable.
3. **AI-ish prose patterns**: genericity, formulaic transitions, manufactured reflection, symmetry, or voice drift. These are editing signals only, not authorship proof.

Do not produce an AI-likeness/humanity score. Do not optimize perplexity, burstiness, punctuation, or detector scores. Do not intentionally insert errors or awkwardness. Do not "native-speakerize" a non-native writer merely to avoid suspicion.

The defense for application integrity is provenance: user facts, explicit chronology/ownership, user-originated or approved voice samples, policy compliance, and a final text the applicant can explain and defend.
