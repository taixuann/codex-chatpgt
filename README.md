# Codex ChatGPT control plane

This repository is the portable coordination and control-plane layer for the
Codex setup. It contains runtime adapters, retained skill- and agent-creation
packages, and the small validation contracts that qualify them.

It is not a research-project repository and must not contain project datasets,
credentials, session state, caches, or linked project contents.

## Start here

1. [`AGENTS.md`](AGENTS.md) — operating boundaries and lifecycle kernel.
2. [`agents/ROLE-CONTRACT.md`](agents/ROLE-CONTRACT.md) — canonical role
   boundaries.
3. [`skills/skill-creator/SKILL.md`](skills/skill-creator/SKILL.md) — the
   minimal-kernel skill authoring procedure.
4. [`skills/harness-worker/SKILL.md`](skills/harness-worker/SKILL.md),
   [`skills/issue-execution/SKILL.md`](skills/issue-execution/SKILL.md), and
   [`skills/athena-review/SKILL.md`](skills/athena-review/SKILL.md) — bounded
   worker execution, Issue lifecycle, and two-axis review protocols.

The GitHub repository is a coordination bridge. Local Codex state is runtime
context, not repository authority; GitHub provides reviewable, portable
artifacts.
