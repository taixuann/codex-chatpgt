---
id: PLAN-ARW-SKILL-CATALOG-QUALITY-20260813-001
issue: 50
status: accepted-canonical-main
scope: skill-catalog-routing-quality
updated: 2026-08-13
---

# Objective

Reconcile the live Codex skill catalog before any runtime migration. Keep
canonical active skills separate from adapted, explicit-only, reference-only,
merged, retired, vendor, and local-overlay material; make admission depend on
capability/utility evidence rather than package shape alone.

## Accepted implementation

- `manifests/skill-catalog.yaml` inventories all 50 Git-tracked packages and
  the 10 ignored local overlays visible in the current skill root.
- Every tracked package has exactly one of `KEEP`, `ADAPT`, `EXPLICIT_ONLY`,
  `REFERENCE_ONLY`, `MERGE`, or `RETIRE`.
- Six bounded governance procedures are `canonical_active`; each declares
  structural, behavioral, and utility status plus evidence paths.
- `skills/control-plane-audit/scripts/validate_skill_catalog.py` rejects
  missing/duplicate dispositions, unproven canonical admission, and stale
  evidence paths. It reports model-mediated runtime routing as
  `NOT_ASSESSED`.
- CI runs the catalog gate beside the existing structural, interface, and
  static routing checks.

## Workflow boundary audit

The eight files under `workflows/feynman/` are retained as documented
project/domain extensions from the architecture reconciliation plan; they are
not generic skill-discovery or control-plane dispatchers, and no active
control-plane skill routes through them. The repository has no retained
`workflows/franky/` runtime tree. Ordinary execution remains Issue/PLAN/PR/CI
plus bounded skills and deterministic tools.

## Boundaries

The catalog is admission metadata, not a universal registry or routing engine.
Issue/PLAN, `OPERATING-WORKFLOW.md`, and scoped instructions remain authority.
Antigravity/runtime migration is deliberately excluded.

## Validation

- Focused catalog tests: PASS (3 tests).
- Catalog validator: PASS (50 tracked packages, 6 canonical active).
- Model-mediated runtime selection and real-skill utility lift: `NOT_ASSESSED`.


## Canonical-main acceptance

Accepted after Issue #35 reconciliation PR #53 merged into `main` at
`e1e05c096bb0912a9a3759f349ad97e3a5424e7d`. Control-plane validation run
#163 passed against the reconciled source. Behavioral runtime selection and
real-skill utility lift remain `NOT_ASSESSED` and are owned by Issue #38.
