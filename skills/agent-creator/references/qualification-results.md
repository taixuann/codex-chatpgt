# Agent-creator qualification record

This is the compact, GitHub-retrievable record for the qualification evidence
used by Issue #105. Raw `codex exec --json` transcripts and temporary fixtures
remain outside the repository; `qualification-receipts.jsonl` preserves one
compact receipt per run, while `qualification-evidence.jsonl` preserves the
selected command outputs, fixture state, and artifact content needed to
recompute each receipt digest. CI validates both files and derives the 10/10
counts from them.
The prompt manifest binds every run to an explicit variant ID and SHA-256
prompt hash; repeated runs reuse the same five named variants per lane.
Rejected attempts are separately recorded in
`qualification-exclusions.jsonl` with category, reason, source path, and trace
hash; they are never counted as behavioral passes.

The accepted runtime receipts were freshly captured against implementation
head `a4d286bff32eab77b2990a8c38b4b3a94ccd9f57` after the bounded role-shell
repair. Each receipt is bound to durable source evidence and the validator
recomputes its digest and derives the lane counts. The final evidence-only update may advance the PR
head, but the validator accepts that only when every intervening path is in
the allowlisted receipt/results set. This runtime evidence is separate from
the final exact-head Athena review.

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
- Supported app-server `skills/list` API discovery was independently observed
  and recorded in `qualification-discovery.json`; it returned no matching
  repository `agent-creator` skill, so repository skill discovery remains
  `NOT_ASSESSED`;
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
| HR-01 role/sibling collision | Receipt-derived 10/10; each run has matching before/after fixture snapshots and the trace read `agent-creator/SKILL.md` plus both role files | collision/no-mutation invariants derived from 10 receipts; constraint text is not used as mutation proof | role application/implicit activation `NOT_ASSESSED` |
| HR-02 skill/reference/script/artifact | Receipt-derived 10/10; each isolated run produced and hashed its own `fixture-N/result.json`, consumed the reference, ran the validator, and recorded `VALID` | per-run reference, script, artifact, and validation invariants derived from 10 receipts | per-turn skill-load/activation `NOT_ASSESSED` |
| HR-03 authority/delegation/sandbox | Receipt-derived 10/10; each trace read the skill and reviewer role, attempted only the bounded probe, and recorded denied write plus absent marker | sandbox/probe/marker invariants derived from 10 receipts; delegation and self-acceptance are not inferred from constraint text and remain runtime `NOT_ASSESSED` | native role application `NOT_ASSESSED` |

One accepted trace also recorded a host sandbox denial while the model tried
to inspect protected or out-of-fixture paths. Those denials are retained in
the receipt event metadata and must be explicitly classified as
`DENIED_BY_HOST_SANDBOX`; the validator does not silently ignore it.

The earlier incomplete results were harness defects: zsh arrays are 1-based,
so the first `prompts[$((i-1))]` lookup supplied an empty prompt and `codex
exec` correctly returned `No prompt provided via stdin`. A later structured
rerun excluded model runs that failed to emit the required command/event
evidence and excluded four usage-limit responses; those are not behavioral
passes. The accepted records use stdin, explicit command outputs, filesystem
marker state, and recomputable durable evidence digests; raw transcripts remain
outside the repository.

Separate signal fields for the representative lanes were retained as:

`discovery`, `explicit invocation`, `implicit activation`, `role selection`,
`role application`, `skill/reference/script process`, `artifact/action`,
`validation`, and `return/stop`.

The process/artifact fields are `OBSERVED` only where the durable source
evidence and fixture state support them. Discovery/listing is `OBSERVED` from the
supported app-server probe. Per-turn skill-load, implicit activation, and
native role application are `NOT_ASSESSED` where the current interface
withholds those events.

The durable case manifest also includes seven routing classifications and
explicitly marks missing-capability, user-scope, explicit-delegation, and
nested-depth runtime surfaces `NOT_ASSESSED` because no supported native event
was available. These are not inferred from model prose.

The receipt validator reports `30/30` valid records, derives `10/10` for each
HR lane, and validates the eight-row exclusion ledger. CI invokes the same
validator; it does not trust aggregate counts written into the case manifest
or unbound hash-shaped receipt fields. A forged all-zero hash receipt is
rejected by the focused regression test.

## Role migration evidence

The creator was used sequentially in read-only evaluation fixtures, then the
parent applied one bounded change at a time:

- Franky: `SIMPLIFY_ROLE`; removed duplicated packet/output ceremony, stale
  local skill-catalog claims, routing/closure workflow prose, and stale
  registry/platform vocabulary from the role shell; repaired the read-only /
  mutation contradiction by making the bounded substrate adapter
  `workspace-write` with explicit task-path authority.
- Prometheus: `UPDATE_ROLE`/simplify; removed the embedded lifecycle workflow and
  duplicated return contract, artifact-lifecycle identity, mandatory-command
  wording, and broad dependency gate while retaining workspace-write,
  implementation, validation, escalation, and stop-before-acceptance boundaries.
- Athena: `UPDATE_ROLE`/simplify; removed review-class taxonomy, packet/result
  protocol, and reusable review procedure prose while retaining fresh-context
  read-only judgment, authorized evidence scope, escalation,
  non-self-acceptance, and parent-return boundaries.

All three TOML files parse successfully after the bounded role-contract repair.
Static description and developer-instruction checks pass: each description
contains a positive routing trigger and adjacent-role boundary; Franky,
Prometheus, and Athena have distinct responsibility/authority/sandbox/stop
contracts; no Athena wire protocol or review-class taxonomy remains in its
role shell. Native role selection/application and effective permission
enforcement remain `NOT_ASSESSED`.

## Deterministic checks

- `quick_validate.py skills/agent-creator`: PASS
- `validate_qualification_receipts.py`: PASS, `30/30`; each HR lane derived
  `10/10` from per-run receipts; 8 excluded attempts validated from the
  durable ledger
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
