---
name: scientific-peer-review
description: Review a supplied scientific claim, method, or manuscript for claim-to-evidence and provenance alignment using explicit criteria. Use only for conditional scientific review. Do not synthesize mechanisms or decide scientific truth.
metadata:
  last_reviewed: '2026-08-29'
  review_interval_days: 90
---

# Scientific peer review

**Trigger:** A bounded scientific artifact is supplied with an explicit rubric
and evidence packet, and an independent check of claim support, methods,
uncertainty, reproducibility, figures, tables, or citations is requested.

**Inputs:** `athena.review.v1` with `review_class: scientific_evidence`, exact
revision, locked method/reporting criteria, claim/evidence references, scope,
exclusions, and authority denial.

**Procedure:** Apply the shared `references/athena-review-kernel.md`; map each
claim to supplied evidence and provenance; inspect methods, uncertainty,
reproducibility, and reporting consistency; record unsupported or partial
claims; and hand the bounded result to the parent/Feynman.

**Output:** `athena.review-result.v1`. Use `partial`, `unfulfilled`, or
`not_assessed` where evidence does not establish a claim. Recommend only a
parent decision; never state a definitive mechanism or scientific truth.

**Boundary:** Read-only and conditional. No data/result mutation, literature
synthesis beyond supplied evidence, criterion rewriting, final scientific
acceptance, or direct routing/spawning.

**Stop:** Escalate `scientific_claim_exceeds_evidence`, conflicting authority,
or critical evidence absence with a narrow human question.

**Validation:** Run scientific unsupported-claim, missing-evidence, provenance,
and producer-persuasion fixtures; host-level scientific judgment remains
`NOT_ASSESSED` unless directly observed.
