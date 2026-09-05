# EVALUATE

Use this reference for readiness or quality review. Deterministic checks come
first; a polished output cannot compensate for skipped process evidence.

## Seven gates

| Gate | Required evidence |
| --- | --- |
| `G1_STRUCTURE` | frontmatter, name/path, placeholders, references/resources, portability |
| `G2_PROVENANCE` | exact source/ref/path, license, adaptation diff, donor boundary |
| `G3_ROUTING` | positive, ambiguous/noisy, adjacent-negative, sibling-negative, and explicit opt-out cases |
| `G4_BEHAVIOR` | requested process and disposition are observable, including no unauthorized side effect |
| `G5_COEXISTENCE` | sibling collision, duplicate capability, and global/local ownership checks |
| `G6_EFFICIENCY` | with/without comparison, context/command/resource cost, and necessity evidence |
| `G7_INDEPENDENT_REVIEW` | fresh-context review of the exact revision with findings and limits, bound by an attestation rather than a caller flag |

Routing reports separate activation precision and recall:

```text
TP = positive activated       FN = positive not activated
FP = negative activated       TN = negative not activated
precision = TP / (TP + FP)    recall = TP / (TP + FN)
```

For substantive updates, compare baseline and candidate on matching complete
must-pass, regression, and held-out cases. Accept only when all must-pass cases
remain passing, held-out performance is non-zero and non-regressing, regression
failures do not increase, and no required gate is `NOT_ASSESSED`. A polished
answer or caller-supplied review flag is not evidence of execution or
independent review. Use a structured result with the exact case, condition,
expected/observed outcome, trace/load signal, cost fields, and raw limitation;
qualitative review must not be reduced to an ungrounded prose score.
