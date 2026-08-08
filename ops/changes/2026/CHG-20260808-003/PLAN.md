---
id: PLAN-ARW-GLOBAL-KERNEL-RECONCILE-20260808-002
title: Global kernel reconciliation and cloud entrypoint
status: approved
date: 2026-08-08
scope: codex-control-plane
---

# Objective

Reconcile the local Codex control plane with the authoritative AI Labs role
registry and establish the smallest cloud-facing state and task-contract layer
needed for progressive disclosure.

## In scope

- clarify canonical roles versus non-canonical support adapters;
- preserve the existing Franky control-plane semantics;
- document the lifecycle/agent/skill/task-contract separation;
- add `CURRENT.md`, `DECISIONS.md`, `CLOUD-BRIEF.md`, and handoff guidance;
- add the canonical task-contract schema;
- record deterministic validation and GitHub publication provenance.

## Out of scope

- adding the seven global capability skills;
- changing the AI Labs role registry;
- adding project-specific workflows;
- changing agent models or permissions;
- memory migration, self-evolution, or OpenScience duplication;
- modifying linked research projects.

## Acceptance

- canonical role count and ownership are unambiguous;
- Argus/Athena are explicitly bounded support adapters;
- cloud entrypoint links to current state, decisions, plan, and task schema;
- task-contract schema validates as a JSON Schema document;
- Franky layout, skill interfaces, allowlist, unit tests, and Git checks pass;
- only `.codex` control-plane paths are committed and pushed.
