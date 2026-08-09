---
id: PLAN-ARW-CONTEXT-ACQUISITION-20260809-001
issue: 2
status: execution-ready
date: 2026-08-09
scope: bounded-context-acquisition-v1
---

# Bounded context-acquisition vertical slice

## Objective

Prove one small, repeatable path for:

```text
context insufficiency
→ bounded read-only acquisition
→ compact context packet
→ parent resumes planning
```

The slice must remain useful without creating a context-strengthening skill,
workflow, agent, session store, or repository-wide crawler.

## Authority and boundaries

- Issue #2 defines the required behavior and acceptance criteria.
- This PLAN defines the current implementation method.
- The parent retains context sufficiency, planning, conflict-resolution, and
  synthesis authority.
- Acquisition is read-only and accepts an explicit allowlist of paths.
- Credentials, sessions, logs, caches, linked projects, and paths outside the
  selected root are excluded.
- Argus remains an optional bounded reader; this slice does not assume that
  host adapter selection is observable.

## Phase 1 — deterministic bounded packet

Implement one small standard-library helper under `ops/scripts/` that:

1. receives a repository root and explicit relative include paths;
2. rejects absolute paths, traversal, missing paths, directories, symlinks,
   and excluded sensitive/runtime paths;
3. reads only the allowlisted regular files;
4. emits a compact JSON packet containing:
   - canonical path and SHA-256;
   - file size and line count;
   - conflicts and uncertainties supplied by the caller;
5. never writes to the selected root or to the repository;
6. exits non-zero with an exact error for invalid scope.

The helper must not interpret project content, build a graph, discover every
file, or decide whether delegation is useful.

## Phase 2 — task contract and parent handoff

Use the existing `ops/schemas/task-contract.schema.yaml` for one bounded
context task. The parent compares direct inspection with delegation and chooses
direct inspection when the scope is small enough that delegation overhead adds
no value. The resulting packet is evidence for parent planning, not a durable
session/checkpoint artifact.

## Phase 3 — validation and closure

Validate:

- valid packet generation;
- traversal/absolute/symlink/sensitive-path rejection;
- deterministic hashes and stable ordering;
- no-write behavior;
- task-contract compatibility;
- `git diff --check` and the existing control-plane suite.

Closure must identify the implementation, tests, task-contract fixture, CI
surface, and documentation references affected by this new helper. It must not
expand to unrelated skills, workflows, project contents, or memory machinery.

## Phase 4 — empirical handoff

Record on Issue #2 and the implementation PR:

- sufficient-context and insufficient-context decisions;
- exact bounded packet output shape;
- direct-vs-delegated decision and overhead rationale;
- parent synthesis after acquisition;
- runtime limitations, especially unavailable Codex adapter/parent-resume
  traces;
- whether the helper earned packaging as a skill. Default: no new skill until
  repeated stable reuse is demonstrated.

## Acceptance mapping

- AC-01: parent records one sufficient and one materially insufficient case.
- AC-02: helper performs repeatable allowlisted read-only acquisition.
- AC-03: packet has canonical/repository evidence/conflicts/uncertainties.
- AC-04: task contract validates when delegation is considered.
- AC-05: any Argus use remains read-only, bounded, and non-recursive.
- AC-06: parent resumes planning and synthesis from the packet.
- AC-07: direct inspection is preferred when scope is small; delegation needs
  an explicit value argument.
- AC-08: helper and existing validators pass deterministically.
- AC-09: runtime limitations are recorded rather than inferred away.
- AC-10: no standalone context skill/workflow/agent is added.
- AC-11: change scope and durable state remain limited to this vertical slice.

## Stop conditions

Stop and report if the selected root cannot be resolved, the allowlist would
touch protected project/runtime state, a requested host behavior is not
observable, or a contract change requires #8/#9/#11/#15 machinery.
