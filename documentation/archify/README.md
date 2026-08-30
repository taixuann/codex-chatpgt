# Archify pilot (Issue #94)

This directory is a derived, revision-pinned observation surface. Repository
contracts, Git history, Issues, plans, pull requests, CI, and human acceptance
remain authoritative. The artifacts do not replace those sources and do not
claim runtime causality, risk, mergeability, or scientific acceptance.

## Pinned source and generation

The pilot used the external MIT-licensed repository
[`tt-a1i/archify`](https://github.com/tt-a1i/archify) at
`f58298be408d62385407ca26bc5a7b612f68be2b` (`2.16.0-dev.0`) in a temporary
checkout. No upstream source was vendored. With that checkout as `archify/`,
the replayable commands are:

```text
node archify/bin/archify.mjs validate architecture documentation/archify/control-plane.architecture.json --quality showcase --json --repo-root /Users/tai/.codex
node archify/bin/archify.mjs validate workflow documentation/archify/operation-workflow.workflow.json --quality showcase --json
node archify/bin/archify.mjs deliver architecture documentation/archify/control-plane.architecture.json documentation/archify/control-plane.architecture.html --quality showcase --json --repo-root /Users/tai/.codex
node archify/bin/archify.mjs deliver workflow documentation/archify/operation-workflow.workflow.json documentation/archify/operation-workflow.workflow.html --quality showcase --json
node archify/bin/archify.mjs compare architecture documentation/archify/architecture-delta.base.architecture.json documentation/archify/architecture-delta.head.architecture.json documentation/archify/architecture-delta.html --receipt documentation/archify/architecture-delta.receipt.json --quality showcase --json --repo-root /Users/tai/.codex
```

## Pilot artifacts

- `control-plane.architecture.*` maps role, contract, validator, and evidence
  boundaries from the current checkout at `0ef8efd...`.
- `operation-workflow.workflow.*` maps the Issue-first lifecycle, bounded
  repair loop, independent review, acceptance, and reconciliation.
- `architecture-delta.*` compares the real parent/head pair
  `8ed22d5...` → `042d013...`. It records four added components, two removed,
  one moved, six added connections, and two removed connections. The facts are
  derived from the revision-pinned Architecture IR and the corresponding Git
  diff; they do not infer runtime behavior or merge risk.
- `provenance.yaml` binds source, version, license, hashes, admission, network
  behavior, and explicit runtime limits.
- `visual-review.md` records the separate screenshot inspection. The packaged
  automated visual-check receipts are retained, but remain non-passing because
  Chrome aborted on this host.

The catalog disposition is `REFERENCE_ONLY`/`EXPLICIT_ONLY` for the external
reference surface; no `skills/` package or implicit routing entry was added.
See `manifests/skill-catalog.yaml` for the explicit catalog record.

## Removal and disablement

Archify is documentation-only in this pilot. Removing `documentation/archify/`
and the temporary checkout leaves the existing validators, tests, and ordinary
control-plane workflows unchanged. The validation record documents this
absence-of-imports boundary; native dispatch, loading, and host permission
enforcement remain `NOT_ASSESSED`.
