---
name: independent-artifact-review
description: Review a bounded implementation, architecture contract, or readiness artifact against locked criteria and supplied evidence. Use for consequential artifact review. Do not implement, repair, accept, or review scientific claims as final authority.
metadata:
  last_reviewed: '2026-08-29'
  review_interval_days: 90
---

# Independent artifact review

**Trigger:** A parent supplies a bounded artifact and asks whether an
implementation, architecture/contract, or readiness criterion is supported by
current evidence.

**Inputs:** `athena.review.v1` request with target/ref and revision, review
class, locked criteria sources, include/exclude scope, evidence, optional
context references, and denied mutation/final-acceptance authority.

**Procedure:** Load `references/athena-review-kernel.md`; verify target
identity and revision; inspect tests, changed scope, contracts, and supplied
evidence; evaluate each locked criterion; classify findings by severity; and
report coverage, limitations, freshness, and a parent-only recommendation.

**Output:** `athena.review-result.v1` with criterion results, evidence anchors,
findings, reviewed/unreviewed surfaces, limitations, human escalation, and a
recommendation. An implementation finding describes parent routing to
Prometheus; missing context describes parent routing to Argus.

**Boundary:** Read-only. Do not mutate artifacts, criteria, canonical state,
or manifests; do not silently fix findings, spawn agents, or emit final
acceptance.

**Stop:** Return `insufficient_evidence` for missing/ambiguous criteria,
stale revisions, inaccessible critical evidence, authority conflict, or an
unreviewed consequential surface. Use a concrete `human_review.reason_code`
when human authority is required.

**Validation:** Validate the request/result schemas and representative fixtures;
retain explicit `not_assessed` limitations for host dispatch, skill loading,
and permission behavior that cannot be observed.
