# EVALUATE

Use this reference for readiness or quality review. Deterministic checks come
first; a polished output cannot compensate for skipped process evidence.

## Eight gates

| Gate | Required evidence |
| --- | --- |
| `G0_NECESSITY` | native/AGENTS/script/existing-skill comparison and justified disposition |
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
expected/observed outcome, trace/load signal, artifact delta, cost fields, and
raw limitation; qualitative review must not be reduced to an ungrounded prose
score. Every case also declares `origin.type` and `origin.source` so regressions
remain attributable.

## Runtime result semantics

Run CREATE and UPDATE cases in an isolated writable fixture. The agent must
perform the requested operation, and the harness must grade the resulting
files/resources plus the structured process trace. A disposition alone is not
behavioral proof.

Use the following status boundary:

- `PASS`: expected outcome, required process trace, and artifact contract are
  all observed.
- `FAIL`: runtime evidence exists but the outcome, trace, or artifact contract
  is wrong or incomplete.
- `NOT_ASSESSED`: the host/runtime is unavailable, times out, exits before
  producing evidence, or withholds a required structured signal.

Aggregate each case into its declared `gate` (and optional additional `gates`)
from the case file. Any observed failure makes that gate `FAIL`; an incomplete
or unavailable case makes it `NOT_ASSESSED`. Do not replace case-owned gate
aggregation with hard-coded case sets.

Record before/after snapshots for the operation workspace only. Exclude the
temporary `CODEX_HOME` so plugin synchronization and runtime caches cannot
masquerade as skill artifacts. Efficiency evidence records command count, tool
calls, token usage when exposed, and changed-resource count; wall-clock time is
diagnostic, not the admission metric. Paired efficiency cases require complete
baseline and candidate outcome/process/artifact evidence, an observed outcome
or artifact delta, and a resource-vector comparison; missing corpus or evidence
fails closed.

Persist the raw process/tool events, before snapshot, after snapshot, and final
structured report for every assessed case. The comparator must recompute
activation, process observation, trace markers, changed paths, artifact
contracts, and necessity evidence from those raw records; summary booleans are
only valid when they match the recomputation.
