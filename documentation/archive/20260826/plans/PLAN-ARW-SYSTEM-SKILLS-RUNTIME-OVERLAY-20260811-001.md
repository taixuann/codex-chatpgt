---
id: PLAN-ARW-SYSTEM-SKILLS-RUNTIME-OVERLAY-20260811-001
title: Runtime skill overlay reconciliation
status: completed
owner: Franky
issue: 35
updated: 2026-08-11
---

# Runtime skill overlay reconciliation

This supplement materializes the final runtime-overlay phase of Issue #35. It
supersedes the earlier compatibility-name statements for the live local
runtime while preserving the older plan as historical evidence.

## Accepted topology

The global discovery root is `/Users/tai/.codex/skills`.

### Active top-level surface

These sixteen packages remain directly discoverable:

```text
control-plane-audit
define-goal
defuddle
docling-document-processing
external-handoff
gh-address-comments
instruction-maintenance
json-canvas
obsidian-bases
obsidian-cli
obsidian-markdown
opencode-executor
project-bootstrap
ragflow-markdown-retrieval
runtime-adapter-management
shared-session-closeout
```

### Feynman namespace

The namespaced Feynman procedures remain available under `skills/feynman/`:

```text
feynman-document-refine
feynman-paper-ingestion
feynman-research-run
feynman-research-state-update
feynman-scientific-rag
feynman-wiki-promotion
```

The older top-level Feynman copies and duplicate shared namespace entries were
archived. The retained namespaced paper-ingestion, RAG, and Wiki procedures use
explicit workspace paths rather than legacy absolute paths.

### Protected system surface

The six `.system` packages remain unchanged and are excluded from local
cleanup: `skill-creator`, `skill-installer`, `plugin-creator`, `openai-docs`,
`imagegen`, and `review-agent`.

### Explicit-only surface

Portability-gated or low-frequency packages are stored outside the global
discovery root under `ops/on-demand-skills/`:

```text
franky-cron-installer
franky-promotion
franky-source-migration
install-project-link
```

They remain source-controlled and directly invokable by path, but are not
ordinary global skill candidates.

## Retired/archive surface

Twenty-nine legacy, duplicate, test-only, cache-only, or unreferenced runtime
entries were moved—not deleted—to the dated reversible archive:

`/Users/tai/.codex/skill-archive/20260811-system-skill-cleanup`

The archive manifest records each original path, disposition, and SHA-256
fingerprint. No `.system` package or unrelated project documentation was
mutated.

## Verification

- 32 unique skill IDs remain across active, namespaced, on-demand, and system
  surfaces; no duplicate frontmatter IDs were found.
- Active interface validation: 6 tracked packages pass.
- On-demand interface validation: 4 tracked packages pass.
- Recursive structural/security quality scan: 0 blocked packages; packages
  without bundled evals retain advisory warnings only.
- Static routing fixture: 6 active tracked packages, 7 contrastive cases;
  runtime model selection remains outside this static evidence.
- The repository allowlist admits `ops/on-demand-skills/**` explicitly and
  continues to reject noncanonical plan paths.

The final capability map is published in Issue #35 and remains bounded by the
documented host-observability gates for real-skill utility lift, catalog-wide
co-loaded routing, dynamic security, and direct OpenCode behavior.
