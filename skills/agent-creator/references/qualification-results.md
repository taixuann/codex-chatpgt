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

The current receipt set was derived at the exact evidence head
`7ee44f4` (full SHA in Git history) from authorized runs using
`gpt-5.6-luna` with medium reasoning. Each receipt is bound to durable source
evidence and the validator recomputes its digest and derives lane counts.
Evidence-only updates may advance the PR head only through the explicit
allowlists. This runtime evidence is separate from the final exact-head Athena
review.

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
  was excluded from artifact snapshots; the HR sandbox remained
  `workspace-write`.
- Supported app-server `skills/list` API discovery was independently observed
  and recorded in `qualification-discovery.json`. The default probe had no
  matching repository skill, while the supported explicit
  `skills/extraRoots/set` probe found the canonical repository skill;
  per-turn skill-load, implicit activation, effective spawned configuration,
  project scope, sandbox enforcement, and nested-depth enforcement remain
  `NOT_ASSESSED`. The fresh exact-head role-spawn probe observed child
  metadata, parent/child linkage, synthetic role identity, and completion;
  user scope was observed separately. Model text was not promoted to an
  activation signal.

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
| HR-01 role/sibling collision | Receipt-derived 10/10; each run has matching, recomputable before/after fixture manifests and the trace read `agent-creator/SKILL.md` plus both role files | deterministic normalized-boundary comparison and recomputable no-mutation manifests derived from 10 receipts; model prose is not used as collision proof | role selection/application/implicit activation `NOT_ASSESSED` |
| HR-02 skill/reference/script/artifact | Receipt-derived 10/10; each isolated run produced and hashed its own `fixture-N/result.json`, consumed the reference, ran the validator, and recorded `VALID` | per-run reference, script, artifact, and validation invariants derived from 10 receipts | per-turn skill-load/activation `NOT_ASSESSED` |
| HR-03 authority/delegation/sandbox | Receipt-derived 10/10 records; the marker was absent, but the workspace-write host did not deny the write probe, so the process result is `NOT_ASSESSED` | no marker was observed after the model's cleanup, but no denial event was available; delegation and self-acceptance remain runtime `NOT_ASSESSED` | sandbox denial and native role application `NOT_ASSESSED` |

Some traces recorded host sandbox denials while the model tried to inspect
protected or out-of-fixture paths. Those denials are retained in receipt event
metadata and explicitly classified as `DENIED_BY_HOST_SANDBOX`; the validator
does not silently ignore them. The HR-03 write probe itself was not denied by
the workspace-write host, so that signal remains `NOT_ASSESSED`.

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
evidence and fixture state support them. The default app-server listing probe
returned no repository match, while the supported explicit extra-root probe
returned `agent-creator`; both outcomes are retained in
`qualification-discovery.json`. Per-turn skill-load, implicit activation, and
native role application are `NOT_ASSESSED` where the current interface
withholds those events.

The durable case manifest also includes seven routing classifications and
explicitly marks missing-capability, user-scope, explicit-delegation, and
nested-depth runtime surfaces `NOT_ASSESSED` because no supported native event
was available. These are not inferred from model prose.

The exact-head receipt validator reports `30/30` valid records, derives
`10/10` for each HR lane, and validates the nine-row exclusion ledger. CI
invokes the same validator; it does not trust aggregate counts written into
the case manifest or unbound hash-shaped receipt fields. A forged all-zero
hash receipt is rejected by the focused regression test.

After the native qualification-infrastructure repair, HR-01 was rerun with a
v4 prompt manifest that requires a command-level `SKILL.md` read, and HR-03
was rerun as a complete ten-run source after an earlier five-row source was
rejected. HR-02 retained its v2 prompt manifest. The final durable receipt set
is derived at `7ee44f4` and validates 30/30 records. HR-03 records ten
`NOT_ASSESSED` process results because the workspace-write probe did not expose
a host denial; no such gap is converted to PASS.

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
- `validate_qualification_receipts.py`: PASS, `30/30`; each HR lane has ten
  valid receipt records, with HR-03 process evidence explicitly
  `NOT_ASSESSED`; 9 excluded attempts validated from the durable ledger
- `validate_eval_cases.py skills/skill-creator/evals/cases.yaml`: PASS
- focused evaluator unit tests: PASS
- retained agent TOML parse/count check: PASS
- `git diff --check`: PASS at the recorded validation point

## Qualification boundary

This record does not claim native dispatch, skill-load, user/project scope
application, effective spawned-role configuration, or implicit activation when
the installed interface did not expose those signals. Those surfaces remain
`NOT_ASSESSED` until a supported runtime event or independent evidence makes
them observable.

## Prior Athena exact-head review

- Reviewer: Chandrasekhar (`01a07d88-674c-7833-8e47-4e29185a3af4`)
- Context: fresh, independent, read-only
- Target: `15f6685888bf402b1a6e67ba3bcb595484990a55`
- Base: `5a64d615d5c7440e9d3e8faaad2eb4865092154e`
- PR/Issue state: PR #106 OPEN/DRAFT/MERGEABLE; Issue #105 OPEN
- Verdict: `insufficient_evidence` (non-binding; no repair, acceptance, merge,
  auto-merge, or Issue close)
- Reproduced: clean exact-head checkout, base ancestry, `git diff --check`,
  receipt validator `30/30` with each HR lane `10/10`, focused agent tests
  `18/18`, TOML parsing, and two exact-head CI success checks.
- Findings: durable receipts are internally recomputable but raw
  `codex exec --json` authenticity lacks an external immutable anchor; native
  skill discovery/load, implicit activation, role selection/application,
  effective configuration, scope, delegation, and nested-depth signals remain
  `NOT_ASSESSED`. No FAIL was reported.

The final exact-head Athena receipt is recorded in the Draft PR discussion,
because publishing a receipt into this repository necessarily creates a new
Git revision. The PR discussion receipt is the acceptance record for the final
head and is not treated as a source-code qualification signal.

## Final qualification repair attempt

The continuation repair added a fail-closed native receipt validator. Native
receipts now bind the full capture SHA, production probe path, and probe-script
SHA-256; non-ancestor captures and changed probe scripts are rejected by
focused tests. The exclusion ledger contains nine rows, including the
`PROCESS_FAILURE` record for the prior HR-02 wrong-root reference attempt;
its raw trace remains outside Git at
`/private/tmp/agent-creator-admission-clean/HR-02-stdin-10/run-3.jsonl` with
trace SHA-256
`b52184223e1cf0ef7a1776d39543b8836ec24da85200090649d60ee24086ff55`.

The exact-head synthetic App Server captures at the native evidence head used
Codex Desktop/0.149.1 with `gpt-5.6-luna` and medium reasoning. The role-spawn
probe used the 240-second fallback and observed child metadata, role identity,
parent relation, and completion. Ordinary and forbidden-delegation probes
observed zero native spawn events and completion. User scope identity was
observed, project scope identity was `NOT_ASSESSED`, and nested-depth
enforcement remained `NOT_ASSESSED`; no model prose was promoted to runtime
evidence.

The production routing matrix used the actual current `agent-creator`
description and retained role descriptions: seven classes × three variants
(21 rows), all observed at a 60-second per-case timeout. Four
missing-capability variants were also observed after variant-1 wording was
clarified. A prior variant-1 wrong-owner result and retry are retained as
development evidence; they are not counted as passes. The current 30-run HR
receipts are recomputable and contain no obsolete protocol labels. The
nine-row exclusion ledger retains prior non-admitted provenance and does not
count excluded attempts as behavioral passes.

These exact-head limitations are deliberate. The role adapters contain no
legacy Franky task/result protocol; the negative role-contract test preserves
that boundary.

## Canonical donor reproduction

The rerunnable `scripts/verify_upstream_baseline.py` helper reproduced the
unmodified pinned donor before adaptation. Its compact receipt is
`qualification-baseline.json` and records the exact commit, eight expected
blob identities, Apache-2.0 license, parse result, structural validation, and
the current evaluator's expected fail-closed result. The donor's structural
validator passes; the current evaluator rejects its obsolete corpus contract,
which is the recorded adaptation gap rather than a false baseline pass.

## Native App Server qualification probe

The synthetic-only `scripts/probe_runtime_agents.py` helper was rerun against
Codex Desktop/CLI `0.149.1` with requested model `gpt-5.6-luna` and requested
reasoning `medium`. The durable receipts are
`qualification-discovery.json` and `qualification-native-runtime.json`.

The probe intentionally contains no real repository role prose or private
control-plane content. The fresh role-spawn, no-delegation,
forbidden-delegation, depth, and user/project-scope receipts are split and
validated independently. Role spawn and completion were observed; native
spawn-count zero was observed for the two no-delegation attempts; project
scope, nested-depth enforcement, per-turn skill-load, and implicit activation
remain `NOT_ASSESSED`. The probe does not promote model text to a runtime
signal.
