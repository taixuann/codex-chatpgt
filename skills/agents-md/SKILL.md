---
name: agents-md
description: Create, audit, update, relocate, or maintain AGENTS.md guidance when instruction scope, precedence, discovery reachability, or stale policy needs evidence; do not use for ordinary repository coding.
metadata:
  last_reviewed: 2026-09-13
  source: issue-111-and-pr-112
---

# AGENTS.md maintenance

Use this Skill for evidence-backed maintenance of AGENTS.md and its effective
instruction chain. It owns guidance placement and validation; it does not own
ordinary implementation, role identity, or global policy mutation.

## Route

- `SETUP`: inspect the actual root/CWD chain, choose the smallest scope, then
  author only the required guidance.
- `MAINTAIN`: classify each proposed rule before changing it. Prefer
  `NO_CHANGE`, `REMOVE`, `MOVE_TO_SKILL`, `MOVE_TO_CI`, `MOVE_TO_README`,
  `RELOCATE`, or `UPDATE_MINIMALLY`.
- `AUDIT`: reconstruct selected AGENTS sources, native `.agents/skills`
  reachability, repository `skills/` package/source roots separately, broken
  references, duplicate Skill names, stale authority, and size/drift signals.
- `UPDATE_FROM_FEEDBACK`: preserve the sequence
  `OBSERVE → EVIDENCE → PROPOSE → VALIDATE → REVIEW → HUMAN_ACCEPT → UPDATE`.

Do not trigger for normal coding merely because a repository contains
AGENTS.md. Do not create nested AGENTS files or Skill-package AGENTS files by
convention. A nested file needs durable operational divergence and a supported
launch CWD that reaches it.

## Evidence boundary

Run the bundled audit from the real repository root and intended execution
CWD before making placement claims:

```text
python3 skills/agents-md/scripts/audit.py <repo-root> --cwd <execution-cwd>
```

The report separates:

`EXPECTED` → `SELECTED` → `ACCESSED` → `LOADED` → `BEHAVIOR_OBSERVED`

Filesystem inspection can establish expected/selected/accessed facts. It
cannot establish that a host loaded or followed instructions; preserve those
states as `NOT_ASSESSED` unless the runtime exposes evidence.

The report is diagnostic, not authority. Repository policy, role contracts,
Issue contracts, and the human owner remain authoritative. Global
`$CODEX_HOME` guidance is proposal-only unless the human explicitly authorizes
its mutation.

## Placement rules

- Put repo-wide always-on truth in the root AGENTS.md.
- Put reusable conditional procedures in a root Skill with precise metadata.
- Put deterministic enforcement in scripts or CI.
- Use nested AGENTS/Skill roots only for independently operated subtrees with
  reproduced discovery reachability and materially different operations.
- Treat same-name Skills as collisions, never as AGENTS-style overrides.
- A CWD change is material when it changes the instruction or Skill surface;
  recompute the audit before continuing.

Read only the relevant references:

- [scope-and-precedence.md](references/scope-and-precedence.md) for chain and
  placement decisions;
- [rule-admission.md](references/rule-admission.md) for classifying guidance;
- [validation.md](references/validation.md) for deterministic and behavioral
  qualification;
- [provenance.md](references/provenance.md) for the bounded source basis.

Do not build an AGENTS database, generator, transcript archive, or universal
template. Stop with `NOT_ASSESSED` when runtime selection/load evidence is not
observable.
