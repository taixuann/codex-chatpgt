# Archify pilot validation

All four JSON inputs passed Archify `validate --quality showcase --json` with
the repository root supplied for architecture source checks. Both primary
deliveries passed the same nine structural/composition checks. The delta
comparison passed 28/28 checks with `completeness: complete` and
`proofLevel: revision-pinned`; the standalone HTML `check` also passed all nine
checks after the base-card readability repair.

The upstream `doctor` command passed. The packaged `visual-check` was attempted
for all three delivered HTML files and failed because Chrome DevTools aborted
with `SIGABRT`; the retained sidecars intentionally report
`visualReview: pending`. Direct headless screenshots were inspected separately,
including a full-height 1440x5000 workflow capture that reaches the terminal
reconciliation node; the findings are recorded in `visual-review.md`.

The external update checker was observed returning `silent:invalid-arguments`.
The upstream contract was inspected: it reads a bounded manifest URL and cache,
does not install or execute updates, and no telemetry path was observed. This
pilot did not enable background updates or add an implicit invocation policy.

Removal/disablement is structural: no repository source imports Archify, and
ordinary control-plane validation does not invoke it. Deleting this directory
and the temporary checkout therefore removes only the derived observation
surface. Native dispatch, skill loading, and host permission enforcement remain
`NOT_ASSESSED`.

## Acceptance-condition status

AC-01 through AC-05: source, license, pinned revision, runtime, and external
checkout provenance are recorded in `provenance.yaml`.

AC-06 through AC-08: the control-plane architecture and operation-workflow
artifacts are rendered, source-grounded, and validated at showcase quality.

AC-09 through AC-11: the real `8ed22d5...` → `042d013...` revision pair is
represented by revision-pinned Before/After IR and a complete delta receipt.

AC-12 through AC-13: deterministic checks pass; automated visual-check failure
is preserved as an explicit limitation and separate screenshot inspection is
recorded.

AC-14: catalog disposition is explicit-only/reference-only; no canonical skill
package or implicit routing was admitted.

Independent Athena review `ATHENA-ISSUE-94-20260830-002` passed on candidate
revision `72291ee...`; its durable record is `athena-review.yaml`.

AC-15: removal is bounded to the derived directory and temporary checkout.

AC-16: this README, provenance, validation, and visual-review record state the
derived/non-canonical boundary and preserve `NOT_ASSESSED` runtime limits.
