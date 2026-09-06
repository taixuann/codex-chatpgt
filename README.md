# Codex ChatGPT control plane

This repository is the portable coordination and control-plane layer for the
Codex setup. It contains runtime adapters, the retained skill-creator package,
and the small validation contracts that qualify it.

It is not a research-project repository and must not contain project datasets,
credentials, session state, caches, or linked project contents.

## Start here

1. [`AGENTS.md`](AGENTS.md) — operating boundaries and lifecycle kernel.
2. [`agents/AGENTS.md`](agents/AGENTS.md) — canonical role boundaries.
3. [`skills/AGENTS.md`](skills/AGENTS.md) — skill admission and operating rules.
4. [`skills/skill-creator/SKILL.md`](skills/skill-creator/SKILL.md) — the
   minimal-kernel skill authoring procedure.

The GitHub repository is a coordination bridge. Local Codex state remains the
runtime source; GitHub provides reviewable, portable artifacts.
