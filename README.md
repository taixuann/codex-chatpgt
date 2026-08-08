# Codex ChatGPT control plane

This repository is the portable coordination and control-plane layer for the
Codex setup. It contains runtime adapters, reusable skills, lifecycle
workflows, validation contracts, and concise cloud handoff state.

It is not a research-project repository and must not contain project datasets,
credentials, session state, caches, or linked project contents.

## Start here

1. [`AGENTS.md`](AGENTS.md) — operating boundaries and lifecycle kernel.
2. [`documentation/CLOUD-BRIEF.md`](documentation/CLOUD-BRIEF.md) — concise
   cloud-facing state and next actions.
3. [`documentation/CURRENT.md`](documentation/CURRENT.md) — accepted current
   architecture and known gaps.
4. [`documentation/DECISIONS.md`](documentation/DECISIONS.md) — durable
   architecture decisions.
5. [`ops/schemas/task-contract.schema.yaml`](ops/schemas/task-contract.schema.yaml)
   — glue contract between workflows, roles, and skills.

The GitHub repository is a coordination bridge. Local Codex state remains the
runtime source; GitHub provides reviewable, portable artifacts.
