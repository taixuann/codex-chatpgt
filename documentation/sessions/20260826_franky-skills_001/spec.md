---
kind: codex.session-artifact.v1
artifact: spec
session_id: 20260826_franky-skills_001
status: needs_review
provenance:
  source_commit: 67d21cc3bf14a4121e064d8edb3f999c830a9307-uncommitted
  observed_at: '2026-08-26T10:40:00Z'
  recorded_by: franky
upstream:
  - context.md
downstream:
  - plan.md
---

# Specification

## Objective

Audit the skill layer used by Franky, repair only demonstrated contract gaps,
and leave acceptance-ready evidence for independent review.

## Success criteria

- Every Franky-relevant skill has a clear trigger, inputs, output, boundary,
  stop condition, and validation expectation.
- Unsafe external execution guidance is explicit about argv-only invocation
  and approved repository-root scope.
- All changed skill packages pass structural, security, quality, and focused
  tests.
- Static and native-runtime evidence are reported separately.

## Boundaries

- Always: preserve canonical role boundaries and existing dirty changes.
- Ask first: staging, committing, publishing, global policy, or runtime
  permission changes.
- Never: edit linked projects, credentials, agents, manifests, ops, or remotes.
