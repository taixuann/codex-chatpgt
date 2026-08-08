---
id: PLAN-ARW-CLOUD-HANDOFF-20260808-001
title: Local-to-Cloud Repository Handoff
status: target-confirmation-required
date: 2026-08-08
scope: cloud-local-handoff
priority: high
implementation_order: codex-first
canonical_bridge: github
supersedes: null
---

# Objective

Create a minimal Local → GitHub → ChatGPT Cloud handoff for brainstorming,
architecture review, execution review, and follow-up planning. The cloud entry
point must be concise and point to the active plan, latest execution handoff,
commit, and relevant files without requiring raw conversation history.

# Target resolution evidence

| Candidate | Local state | GitHub remote | Result |
| --- | --- | --- | --- |
| `/Users/tai/.codex` | Git repo, branch `master` | none | Not viable as GitHub bridge |
| `/Users/tai/workspace` | Git repo, branch `main` | `git@github.com:taiixuann/workspace.git` | Only viable candidate |
| `/Users/tai/ai-labs` | no local `.git` detected | none resolved | Not a local Git target |
| `/Users/tai/workspace/projects` | Git repo, branch `main` | none | Not viable as GitHub bridge |
| `/Users/tai/workspace/documentation` | Git repo, branch `master` | none | Not viable as GitHub bridge |

The likely target is `/Users/tai/workspace`, but this remains a human choice
because the plan explicitly forbids inferring the target from prior
conversation. No files have been created or changed in that repository.

# Pre-existing target state

`/Users/tai/workspace` is dirty before this plan: tracked root files including
`AGENTS.md`, `README.md`, `GEMINI.md`, `_sidebar.md`, and
`.docsify_sidebar_gen` are deleted, while `personal-wiki/` is untracked. These
changes are preserved and must not be mixed with the handoff implementation.

# Proposed v1 scope after target confirmation

In scope:

- `documentation/CLOUD-BRIEF.md` as one concise cloud-facing entrypoint;
- `documentation/handoffs/HANDOFF-<PROJECT>-YYYYMMDD-NNN.md` template;
- links between plan, execution, validation, branch, and commit;
- target-repository guidance for future local runs;
- local artifact/reference validation;
- a human-reviewed local commit and explicit push only after approval.

Out of scope:

- agent architecture redesign;
- memory or Wiki/RAG redesign;
- OpenScience/OpenCode integration;
- automatic self-evolution;
- mirroring the whole workspace;
- resolving or overwriting the target's pre-existing dirty files.

# Information flow

```text
Cloud plan → target repository → local execution → validation
→ HANDOFF + CLOUD-BRIEF → human-reviewed commit/push → Cloud inspection
```

`CLOUD-BRIEF.md` must remain progressive-disclosure context, not a copy of
plans, logs, diffs, or conversation history. Handoffs record execution
provenance and must not invent canonical decisions.

# Acceptance after target confirmation

- the target repository and remote are explicitly confirmed;
- pre-existing dirty paths are preserved and excluded;
- one concise `CLOUD-BRIEF.md` exists;
- one handoff template exists and validates its references;
- PLAN → execution → validation → commit → HANDOFF is traceable;
- the selected branch/commit is reachable from GitHub after explicit approval;
- ChatGPT Cloud can inspect the brief, handoff, plan, and referenced diff.
