---
id: PLAN-ARW-ANTHROPIC-SKILLS-INTAKE-20260811-001
title: Curated Anthropic skill intake for Codex
status: implemented
owner: Franky
approved_by: user
updated: 2026-08-11
---

# Curated Anthropic skill intake for Codex

## Decision

The user approved intake of the Anthropic collection and requested its
skill-creator method. This plan preserves an explicit local source area while
keeping global discovery narrow and Codex-native.

Source: `anthropics/skills` at
`f17010c9bb483898c1d9c9f42dde2b3a98889434`.

The committed [intake manifest](../../manifests/anthropic-skills-intake-20260811.yaml)
records package hashes, commands, outcomes, and exclusions for the untracked
local source cache.

## Source and runtime layout

```text
vendor-skills/anthropic/f17010c9bb483898c1d9c9f42dde2b3a98889434/
  algorithmic-art, brand-guidelines, canvas-design, doc-coauthoring,
  frontend-design, internal-comms, mcp-builder, skill-creator,
  slack-gif-creator, template-skill, theme-factory,
  web-artifacts-builder, webapp-testing

ops/on-demand-skills/anthropic-skill-creator/
  Codex-compatible explicit-only adapter for the upstream method
```

The vendor source area is local and ignored by Git. The adapter is
explicit-only and versioned. Neither is silently added to ordinary discovery.

## Excluded packages

`docx`, `pdf`, `pptx`, and `xlsx` were not retained. Their license forbids
keeping copies outside Anthropic services, and their runtime purpose overlaps
the bundled Codex document, PDF, presentation, and spreadsheet capabilities.

## Dispositions

| Package | Disposition | Reason |
| --- | --- | --- |
| `anthropic-skill-creator` adapter | EXPLICIT_ONLY | Requested method, with Claude-only execution disabled. |
| `frontend-design`, `webapp-testing`, `mcp-builder`, `doc-coauthoring` | ON_DEMAND | Candidate procedures; host/dependency and routing behavior require task-level proof. |
| `theme-factory`, `canvas-design`, `algorithmic-art`, `slack-gif-creator`, `internal-comms`, `brand-guidelines` | REFERENCE / ON_DEMAND | Low-frequency or provider/brand-specific. |
| `web-artifacts-builder` | REFERENCE | Designed for Claude.ai artifact runtime. |
| `template-skill` | REFERENCE | Placeholder template, not an executable capability. |
| `docx`, `pdf`, `pptx`, `xlsx` | EXCLUDED | License restriction and existing Codex equivalents. |

## Validation and remaining evidence

- All staged upstream packages passed upstream static validation; local quality
  checks found no blocked credential or dangerous-command patterns.
- The source `template` package was renamed to `template-skill` in the local
  vendor cache to match its frontmatter name.
- The raw upstream `skill-creator` remains outside discovery because it invokes
  `claude -p` and assumes Claude trigger semantics. The explicit adapter
  replaces those steps with local validation and real Codex outcome evidence.
- No runtime utility claim is made for the source packages until each is used
  in a real Codex task and assessed against its declared boundary.
