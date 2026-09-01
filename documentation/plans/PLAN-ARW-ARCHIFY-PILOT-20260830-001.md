---
id: PLAN-ARW-ARCHIFY-PILOT-20260830-001
issue: https://github.com/taixuann/codex-chatpgt/issues/94
status: review_ready
updated: 2026-08-30
source_commit: 0ef8efd66261d4bbfe563b39c6846315467d577d
---

# Issue #94 — Archify qualification and pilot

## Decision boundary

Qualify `tt-a1i/archify` as an external, explicit-only visual observation
capability. Repository contracts, Git history, and source files remain
canonical. Pilot outputs are derived artifacts and must be removable without
changing ordinary control-plane validation. No Archify agent, workflow engine,
vendored upstream tree, automatic regeneration, or runtime promotion is in
scope.

## Work units

1. Pin upstream provenance, inspect runtime/update behavior, and record MIT
   licensing, Node requirement, network/update-check boundary, and removal
   path.
2. Author and deliver three typed pilot surfaces from current repository
   evidence: control-plane architecture, Issue-first Operation Workflow, and
   the Before/Delta/After view for commit `042d01392cb1915b47d75c101d58091badff7068`
   (parent `8ed22d5ba77732d72f4d094a2312dcaf8448c3b7`).
3. Preserve source/revision provenance, validate every IR and delivery, run
   separate visual inspection, compare delta facts with `git diff`, and record
   an explicit `EXPLICIT_ONLY` admission decision unless utility evidence
   justifies stronger admission.
4. Run repository validators/tests, prove Archify removal/disablement leaves
   the control plane operable, obtain independent review on the final commit,
   repair only material findings, and open one review-ready PR without merge.

## Acceptance-criteria map

| AC | Implementation evidence | Validation evidence |
|---|---|---|
| AC-01 | `documentation/architecture/archify/provenance.yaml` pins upstream commit/ref and MIT license | upstream `git ls-remote`, provenance review |
| AC-02 | provenance records Node >=18, local CLI, no required network, optional update checker behavior | `doctor`, source inspection, checker run |
| AC-03 | external temporary checkout + committed derived artifacts only; no runtime dependency | remove/disable proof and control-plane suite |
| AC-04 | no upstream source copied into this repository | changed-file inventory and allowlist |
| AC-05 | `control-plane.architecture.json` + delivered HTML | Archify validate/deliver + source evidence receipt |
| AC-06 | `operation-workflow.workflow.json` + delivered HTML | Archify validate/deliver |
| AC-07 | authored edges/nodes each carry evidence or explanatory labels | provenance audit and independent review |
| AC-08 | architecture sources use exact Git revisions and line anchors | Archify repository-evidence receipt |
| AC-09 | receipts for all three sources/deliveries | Archify validate/deliver/check |
| AC-10 | separate screenshot/image inspection record; automated receipt remains pending | visual-check output plus human inspection record |
| AC-11 | base/head architecture sources and compare artifact for `042d013` | compare receipt and revision-pinned inputs |
| AC-12 | delta fact table maps every add/remove/change to `git diff` | scripted diff comparison and review |
| AC-13 | artifact limitations explicitly deny runtime/risk/merge inference | provenance/readme and independent review |
| AC-14 | `provenance.yaml` records catalog disposition `EXPLICIT_ONLY` | catalog/decision validation |
| AC-15 | no stronger admission without measured utility evidence | admission rationale and issue review |
| AC-16 | canonical documentation update records derived/non-canonical boundary | `CURRENT.md`/`DECISIONS.md` reconciliation if semantics are accepted |

## Stop conditions

Stop and report rather than inventing topology, weakening provenance, vendoring
the upstream tree, claiming visual PASS from automation, or promoting the
capability without independent review. Native dispatch, skill loading, host
permissions, and runtime enforcement remain `NOT_ASSESSED` unless directly
observed.

## Review disposition

Independent Athena re-review passed on repaired candidate tree
`55c456970dd9d5eb306e32f1ca1d385de4d2b30d`. The review record is
`documentation/architecture/archify/athena-review.yaml`; the subsequent commit only adds
that durable evidence record and does not alter the reviewed pilot artifacts.
