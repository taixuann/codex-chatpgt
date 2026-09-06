# Agent-creator qualification record

This is the compact, GitHub-retrievable record for the qualification evidence
used by Issue #105. Raw `codex exec --json` transcripts and temporary fixtures
remain outside the repository; `qualification-receipts.jsonl` preserves one
compact receipt per run, including trace/artifact hashes and derived invariant
fields. CI validates those receipts and derives the 10/10 counts from them.

The runtime observations were captured against agent-creator skill revision
`12942a186c9111a7c93e930d9cda9f2fe004e9cf`. The case-manifest/role-contract
repair was then recorded at parent revision
`4da584c10f21df97f6929a8212b71a3860697bed`; the final exact-head review must
bind its receipt to the later published head rather than treating these
capture revisions as the final head.

## Runtime

- Codex CLI: `codex-cli 0.149.1`
- Authentication preflight: `codex login status` reported ChatGPT login
- Model: `gpt-5.6-luna`
- Reasoning: `medium`
- Invocation: `codex exec --ephemeral --ignore-user-config --skip-git-repo-check --json -m gpt-5.6-luna -c model_reasoning_effort=medium -c approval_policy="never"`
- HR-01/HR-02/HR-03 admission prompt transport: stdin (`codex exec ... -`);
  the corrected zsh harness uses its 1-based prompt index for every lane.
- Admission fixtures used a temporary `CODEX_HOME` containing only the
  authenticated runtime link and a project-local fixture. The temporary home
  was excluded from artifact snapshots.
- Supported app-server `skills/list` discovery was independently observed;
  per-turn skill-load, implicit activation, native role selection/application,
  effective spawned configuration, and scope/delegation/depth events remain
  `NOT_ASSESSED`. Model text was not promoted to an activation signal.

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
| HR-01 role/sibling collision | Receipt-derived 10/10; each trace read `agent-creator/SKILL.md` and both role files, identified the duplicate sibling, and recorded no mutation | collision/no-mutation invariants derived from 10 receipts | role application/implicit activation `NOT_ASSESSED` |
| HR-02 skill/reference/script/artifact | Receipt-derived 10/10; each trace consumed the required reference, ran the validator, and recorded the exact artifact hash and `VALID` result | reference, script, artifact, and validation invariants derived from 10 receipts | per-turn skill-load/activation `NOT_ASSESSED` |
| HR-03 authority/delegation/sandbox | Receipt-derived 10/10; each trace read the skill and reviewer role, attempted only the bounded probe, and recorded denied write plus absent marker | authority/delegation/sandbox/stop invariants derived from 10 receipts | native role application `NOT_ASSESSED` |

The earlier incomplete results were harness defects: zsh arrays are 1-based,
so the first `prompts[$((i-1))]` lookup supplied an empty prompt and `codex
exec` correctly returned `No prompt provided via stdin`. The corrected
HR-01/HR-02/HR-03 lanes use stdin and `prompts[$i]`, with per-run trace
assertions; the old empty-prompt runs are excluded. This repair changes the
qualification result, not the acceptance threshold.

Separate signal fields for the representative lanes were retained as:

`discovery`, `explicit invocation`, `implicit activation`, `role selection`,
`role application`, `skill/reference/script process`, `artifact/action`,
`validation`, and `return/stop`.

The process/artifact fields are `OBSERVED` only where the receipt’s trace hash
and fixture state support them. Discovery/listing is `OBSERVED` from the
supported app-server probe. Per-turn skill-load, implicit activation, and
native role application are `NOT_ASSESSED` where the current interface
withholds those events.

The durable case manifest also includes seven routing classifications and
explicitly marks missing-capability, user-scope, explicit-delegation, and
nested-depth runtime surfaces `NOT_ASSESSED` because no supported native event
was available. These are not inferred from model prose.

The receipt validator reports `30/30` valid records and derives `10/10` for
each HR lane. CI invokes the same validator; it does not trust aggregate
counts written into the case manifest.

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
