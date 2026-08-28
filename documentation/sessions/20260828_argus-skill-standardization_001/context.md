---
kind: codex.session-artifact.v1
artifact: context
session_id: 20260828_argus-skill-standardization_001
status: observed
provenance: {source_commit: 8ed22d5ba77732d72f4d094a2312dcaf8448c3b7, observed_at: '2026-08-28T08:45:00+07:00', recorded_by: franky}
upstream: [references.yaml]
downstream: [spec.md, plan.md]
---

# Context

Issue #90 requests a strict, profile-aware, read-only Argus reconnaissance
surface. The clean canonical main worktree is `/private/tmp/codex-consolidation-20260826` at `8ed22d5`, aligned with `origin/main`; the stale checkout was not touched.

## Audited overlap dispositions

| Capability | Purpose/trigger/procedure/output/side effects | Overlap and disposition |
|---|---|---|
| `context-engineering` | Curates context for coding sessions; may recommend rules/spec/source loading; no file mutation by itself | Useful source for focused loading, but too broad and implementation-oriented for Argus; `REFERENCE_ONLY` |
| `source-driven-development` | Verifies framework facts against official docs and cites implementation decisions | Source qualification is useful, but implementation/citation workflow is outside Argus; `REFERENCE_ONLY` |
| `planning-and-task-breakdown` | Produces implementation plans/tasks and dependency slices | Direct role conflict with Argus planning boundary; `EXPLICIT_ONLY` and never co-load for reconnaissance |
| `scientific-evidence-synthesis` | Classifies and calibrates scientific claims | Feynman-owned interpretation; `EXPLICIT_ONLY`, not an Argus skill |
| `session-packet-management` | Provenance-linked session records and packet validation | Retain as shared lifecycle capability; `KEEP`, not duplicated by Argus |
| `shared-session-closeout` | Maps accepted outcomes to durable records | Lifecycle-only; `KEEP` for callers, not an Argus profile |

The three new profiles share one internal kernel and explicitly reject planning,
implementation, scientific interpretation, review, mutation, indexing, and
session ownership. No context-mapping, dependency-tracing, handoff-generation,
or evidence-packet visible skills were created.

## Adaptation ledger

| Profile | Retained | Modified | Removed/rejected | Added |
|---|---|---|---|---|
| codebase-reconnaissance | bounded acquire-codebase orientation/structure ideas from `github/awesome-copilot` | narrowed to read-only paths, impact, and structure-health | rejected broad docs generation and mutation | shared kernel and bounded handoff |
| research-source-discovery | source-map and evidence-depth ideas from `d-init-d/d-research-skill` | constrained to discovery, provenance, license, and saturation | rejected direct vendoring and scientific conclusion | explicit corpus dedup/version and gap stop |
| reference-state-reconnaissance | minimal authority/artifact/relationship concepts from Cantara KCP | limited to current-state comparison | rejected wholesale KCP protocol/import | freshness/supersession and bounded packet |

The `jovd83/codebase-context` material is comparison-only; no source was
copied. All rejected material remains reference-only rationale, not hidden
implementation.

## Source and runtime limitations

The GitHub API and network were unavailable in this runtime. Existing local
records provide an exact immutable `github/awesome-copilot` reference
(`797cf9f830cc216aa66bb509543c8c93b3ba47d1`, MIT); the parent supplied exact
d-init, Cantara, and jovd83 comparison revisions and licenses recorded in
`references.yaml`. No external content was vendored. Native discovery, profile
dispatch, skill loading, and host permission enforcement remain `NOT_ASSESSED`.
