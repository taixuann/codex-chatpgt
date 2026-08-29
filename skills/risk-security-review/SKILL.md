---
name: risk-security-review
description: Review a bounded permission, integration, untrusted-input, or dependency risk against explicit security criteria and supplied evidence. Use for consequential security review. Do not harden code, change permissions, or accept the risk.
metadata:
  last_reviewed: '2026-08-29'
  review_interval_days: 90
---

# Risk and security review

**Trigger:** A parent supplies a bounded security-relevant artifact or runtime
authority change and requests an independent trust-boundary, authorization,
dependency, or excessive-agency review.

**Inputs:** `athena.review.v1` with `review_class: risk_security`, exact target
revision, locked security criteria, supplied threat/evidence references,
scope/exclusions, and denied mutation/final-acceptance authority.

**Procedure:** Apply the shared `references/athena-review-kernel.md`; identify
trust boundaries and assets from supplied material; check authorization,
untrusted inputs, secrets, dependency/supply-chain exposure, and excessive
agency; anchor findings and report unreviewed surfaces.

**Output:** `athena.review-result.v1` with severity-ranked findings and a
parent-only recommendation. Suggested actions are descriptions, never patches.

**Boundary:** Read-only. Do not implement hardening, modify permissions,
secrets, dependencies, policy, canonical state, or review criteria; do not
spawn repair agents or provide final acceptance.

**Stop:** Escalate `authority_or_policy_change`, `critical_evidence_missing`,
or conflicting authority with a bounded human question.

**Validation:** Run trust-boundary, missing-evidence, denied-mutation, and
excessive-agency fixtures. Native runtime enforcement remains `NOT_ASSESSED`.
