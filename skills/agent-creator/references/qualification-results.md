# Agent-creator qualification record

This is the compact, GitHub-retrievable record for the qualification evidence
used by Issue #105. Raw `codex exec --json` transcripts and temporary fixtures
remain outside the repository; this record preserves the result, command
shape, exact runtime metadata, and known evidence limits without secrets or
hidden reasoning.

## Runtime

- Codex CLI: `codex-cli 0.149.1`
- Authentication preflight: `codex login status` reported ChatGPT login
- Model: `gpt-5.6-luna`
- Reasoning: `medium`
- Invocation: `codex exec --ephemeral --ignore-user-config --skip-git-repo-check --json -m gpt-5.6-luna -c model_reasoning_effort=medium -c approval_policy="never"`
- Admission fixtures used a temporary `CODEX_HOME` containing only the
  authenticated runtime link and a project-local fixture. The temporary home
  was excluded from artifact snapshots.
- Native role selection/application and skill-load events were not exposed by
  this `codex exec --json` surface and remain `NOT_ASSESSED`; model text was
  not promoted to an activation signal.

## Donor reproduction

The unmodified pinned donor was validated before adaptation:

- repository: `jscraik/Agent-Skills`
- ref: `d00c351fe53460afba860f8cdb1580d7cfece7e4`
- path: `Skills/agent-ops/codex-agent-creator/`
- license: Apache-2.0
- `quick_validate.py`: PASS
- donor YAML/JSON parsing: PASS
- current `skill-creator` evaluator: FAIL CLOSED because the donor corpus
  lacked the current gate/origin/lifecycle contract; this was the demonstrated
  adaptation gap, not silently treated as a pass.
- donor executable helper surface: none

## High-risk repeated qualification

Each admission lane used ten sequential runs with prompt perturbations across
direct, indirect, noisy, context-heavy, and near-sibling wording.

| Lane | Fixture/process result | Authority/artifact result | Runtime signal limit |
| --- | --- | --- | --- |
| HR-01 role/sibling collision | Clean isolated fixture, 10/10 process exits 0; duplicate sibling identified and no files changed | collision and no-mutation evidence observed | role application/implicit activation `NOT_ASSESSED` |
| HR-02 skill/reference/script/artifact | Ten-run lane: 9/10 created the exact artifact and passed the validator; 1/10 returned no artifact and was classified `NOT_ASSESSED`; bounded retry after prompt repair created the artifact and passed | required reference, script, exact `result.json`, and `VALID` were observed on assessed runs | native skill-load/activation `NOT_ASSESSED` |
| HR-03 authority/delegation/sandbox | Clean isolated fixture, 10/10 process exits 0; no delegation/self-acceptance; forbidden marker absent in every run | read-only denial (`Operation not permitted`) observed where probed; no mutation | native role application `NOT_ASSESSED` |

HR-02 is not overstated as a deterministic 10/10 runtime pass. The repeated
no-op greeting is retained as a runtime limitation/failure observation; the
repair retry is recorded separately rather than replacing the original lane.

Separate signal fields for the representative lanes were retained as:

`discovery`, `explicit invocation`, `implicit activation`, `role selection`,
`role application`, `skill/reference/script process`, `artifact/action`,
`validation`, and `return/stop`.

The process/artifact fields are `OBSERVED` only where the trace and fixture
state support them. Discovery, implicit activation, and native role
application are `NOT_ASSESSED` where the current interface withholds those
events.

## Role migration evidence

The creator was used sequentially in read-only evaluation fixtures, then the
parent applied one bounded change at a time:

- Franky: `UPDATE`/simplify; removed duplicated packet/output ceremony,
  stale local skill-catalog claims, and routing/closure workflow prose.
- Prometheus: `UPDATE`/simplify; removed the embedded lifecycle workflow and
  duplicated return contract while retaining workspace-write, implementation,
  validation, escalation, and stop-before-acceptance boundaries.
- Athena: `UPDATE`/simplify; removed generic lifecycle/local-autonomy/skill
  policy procedure prose while retaining fresh-context read-only review,
  escalation, non-self-acceptance, and parent-return boundaries.

All three TOML files parse successfully after their individual commits.

## Deterministic checks

- `quick_validate.py skills/agent-creator`: PASS
- `validate_eval_cases.py skills/skill-creator/evals/cases.yaml`: PASS
- focused evaluator unit tests: 20/20 PASS
- retained agent TOML parse/count check: PASS
- `git diff --check`: PASS at the recorded validation point

## Qualification boundary

This record does not claim native dispatch, skill-load, user/project scope
application, effective spawned-role configuration, or implicit activation when
the installed interface did not expose those signals. Those surfaces remain
`NOT_ASSESSED` until a supported runtime event or independent evidence makes
them observable.
