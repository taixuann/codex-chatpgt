# EVALUATE

Use this shared capability for readiness or quality review of any target skill.
It is consumed by CREATE, INSTALL, UPDATE, and AUDIT; it is not a peer action
and does not own the skill-creator self-evaluation harness.

## Evaluation design

Start with real-task selection: choose requests that exercise the changed
behavior, its highest-risk boundary, adjacent preserved behavior, and the
expected failure path. Define the portfolio before running it and keep the
baseline and candidate comparable.

Use complete partitions with distinct purposes:

- `must_pass`: required normal paths and protected invariants;
- `regression`: previously observed failures and changed boundaries;
- `held_out`: cases not used to tune routing or wording.

Cover the workflow's branches and checkpoints, not only its final prose:
selection, inputs, state transitions, tool boundaries, normal completion,
failure/recovery, side effects, artifacts, and terminal handoff. For
stochastic behavior, use repeated trials or semantic checkpoints and compare
forbidden actions and outcome classes rather than byte-identical prose.

Batch the portfolio before repair. Classify each result as `EXPECTED_CHANGE`,
`IMPROVEMENT`, `UNCHANGED`, `REGRESSION`, `NOT_COMPARABLE`, or
`NOT_ASSESSED`; repair the earliest invalidated owner and rerun the same
candidate evidence. Do not tune one case and silently change the comparison
set.

State whether each evaluation is persistent or creation-only. Runtime package
files, generated artifacts, reports, raw traces, baselines, and temporary
fixtures have different lifetimes; evaluate the intended lifetime and reject
decorative or orphan resources.

The report must preserve the exact case, condition, expected and observed
outcome, process trace, artifact delta, cost fields, failure classification,
and raw limitation. A qualitative score or caller-supplied review flag is not
execution evidence. Keep activation, explicit invocation, implicit load, and
behavior/artifact evidence as separate fields.

## Routing metrics

For routing portfolios, report activation separately from task quality:

```text
TP = positive activated       FN = positive not activated
FP = negative activated       TN = negative not activated
precision = TP / (TP + FP)    recall = TP / (TP + FN)
```

Keep description-tuning cases separate from held-out cases. Use isolated
`.agents/skills` fixtures and require an explicit host load signal. Without
one, report `NOT_ASSESSED` rather than inferring activation from prose.

## Runtime result semantics

Run CREATE and UPDATE cases in an isolated writable fixture. The agent must
perform the requested operation, and the harness must grade resulting
files/resources plus the structured process trace. A disposition alone is not
behavioral proof.

Runtime qualification starts with one provider/auth preflight. An unavailable
runtime, missing authentication, or unreachable provider skips model cases
with a classified `NOT_ASSESSED` result; it must not launch every case against
an empty per-case `CODEX_HOME`. Use staged execution (`smoke`, `lifecycle`,
then `full`) so a failed smoke does not spend the full corpus budget.

Use this status boundary:

- `PASS`: expected outcome, required process trace, and artifact contract are observed.
- `FAIL`: runtime evidence exists but the outcome, trace, or artifact contract is wrong or incomplete.
- `NOT_ASSESSED`: the host/runtime is unavailable, times out, exits before producing evidence, or withholds a required structured signal.

Record before/after snapshots for the operation workspace only. Exclude the
temporary `CODEX_HOME` so caches cannot masquerade as skill artifacts.
Efficiency evidence records command count, tool calls, token usage when
exposed, and changed-resource count; wall-clock time is diagnostic, not the
admission metric. Paired cases require complete baseline and candidate
outcome/process/artifact evidence plus a resource-vector comparison.

Persist raw process/tool events, before and after snapshots, and the final
structured report for every assessed case. The comparator must recompute
process observation, trace markers, changed paths, artifact contracts, and
necessity evidence from those raw records; summary booleans are valid only
when they match the recomputation.

## Self-evaluation boundary

The skill-creator-specific G0-G7 gate model, 26-case corpus, action probes,
and validator schema belong to `evals/cases.yaml` and
`scripts/validate_eval_cases.py`. They are a self-evaluation implementation,
not generic evaluation guidance. `EVALUATE` remains a shared capability even
when a self-evaluation case has `kind: EVALUATE`.
