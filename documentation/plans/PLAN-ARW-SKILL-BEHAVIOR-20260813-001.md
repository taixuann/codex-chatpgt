---
id: PLAN-ARW-SKILL-BEHAVIOR-20260813-001
issue: 38
status: runtime-evidence-blocked
repository: taixuann/codex-chatpgt
created: 2026-08-13
scope: behavioral skill quality after canonical-main reconciliation
---

# Behavioral skill quality

## Objective

Measure whether the six canonical skill candidates and selected `ADAPT`
packages improve task routing and task outcomes under the real Codex host.
Structural catalog evidence is not behavioral acceptance.

## Implemented harness boundary

- `manifests/skill-evidence.yaml` is the separate evidence envelope; it is not
  catalog telemetry and does not promote packages.
- `skills/control-plane/control-plane-audit/scripts/run_skill_evaluation.py` runs bounded,
  read-only `codex exec --json` observations and aggregates routing, utility,
  efficiency, interference, and regression records.
- `skills/control-plane/control-plane-audit/scripts/fixtures/skill-quality-benchmark.yaml`
  contains 84 co-loaded cases: 10 per canonical skill plus adjacent-negative,
  nearest-neighbor, contextual, and expected-none coverage.
- The harness creates temporary evaluation homes. WITH-SKILL enables only the
  six candidates in that temporary home; WITHOUT-SKILL exposes no ordinary
  skills. The checked-in catalog and descriptions are never rewritten.
- `validate_skill_evidence.py` enforces the evidence dimensions and the
  `OBSERVE -> PROPOSE -> REVIEW -> ACCEPT -> UPDATE` regression boundary.

## Invocation policy

`skills/**/<package>/agents/openai.yaml` carries the host policy field
`policy.allow_implicit_invocation`.

- all non-`KEEP` dispositions are disabled;
- `KEEP` candidates remain disabled while catalog behavioral evidence is
  `NOT_ASSESSED`;
- a `KEEP` package may become implicit-enabled only with behavioral `PASS`;
- no automatic description rewrite, router, graph database, or optimizer is
  introduced.

## Required runtime evidence

1. Run the co-loaded benchmark with at least three repeats and capture host
   selection events, model/reasoning provenance, token/tool/time usage, and
   precision, recall, false-positive, none-accuracy, and confusion metrics.
2. Run paired WITH-SKILL/WITHOUT-SKILL cases using the same model/context and
   score correctness, scope, artifacts, validation, side effects, thrashing,
   tokens, latency, and cost where observable.
3. Run the first ADAPT tournament for:
   `debugging-and-error-recovery`, `code-simplification`, and
   `test-driven-development`.
4. Harvest routing failures as observations. Promote a regression fixture only
   after human review and acceptance.

## Current evidence

The authorized ChatGPT-only probe now completes bounded read-only turns in an
isolated project-local `.agents/skills` tree. The initial 12-record utility
sample completed 7 records and timed out 5 at the 45-second bound. Procedure
loads were observed for all six canonical skills through command traces; the
host did not expose a dedicated selection event, and model self-report remains
separate from host evidence. Two WITH/WITHOUT pairs completed on both sides
and were redundancy candidates; no load-bearing or harmful result was
observed. The evidence manifest therefore remains `NOT_ASSESSED`: this is a
partial, timeout-affected utility sample, not catalog-wide routing acceptance.

## Dependency gate

Do not promote this evidence into canonical-main admission until
`codex/system-skill-consolidation` has been reconciled and merged into `main`
under Issue #35. Antigravity migration is outside this plan.
