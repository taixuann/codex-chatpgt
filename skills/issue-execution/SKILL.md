---
name: issue-execution
description: Drive one stable GitHub Issue through bounded execution, Git reconciliation, validation, exact-head review, repair, and the external Draft PR STOP boundary; do not use as a general workflow engine.
metadata:
  issue: 107
  status: candidate
---

# Issue execution

Use this skill only when a real GitHub Issue is the authority for a bounded
change. The Issue owns intent, scope, acceptance criteria, and amendments. The
skill owns the compact execution ledger and parent decision path; it does not
copy the Issue body, create a second tracker, or accept its own work.

## Contract boundary

```text
Issue authority
→ preflight/baseline
→ small task DAG
→ bounded request to the harness-worker execution boundary
→ actual Git reconciliation
→ task and integrated validation
→ candidate HEAD
→ fresh Athena Luna Max WORK review
→ if WORK passes, a different fresh Athena Luna Max GOAL review
→ if WORK finds a verified material defect, repair on the compatible worker
→ new HEAD and fresh WORK review
→ if GOAL is incomplete, repair the mapped task
→ new HEAD and fresh WORK then GOAL reviews
→ technically eligible
→ awaiting_parent_decision
→ external parent/Draft-PR boundary
```

The local adapter is the thin AGY-backed execution substrate and owns the
#107 contract gap: canonical repository/CWD, allowed paths, exact session
binding, and normalized receipts. Neither the transport nor this skill claims
AC completion, review success, or acceptance. See `references/contracts.md` and
`../harness-worker/references/contracts.md`.

Use `agy` as the primary worker. On an availability failure
(`QUOTA_EXHAUSTED`, `RATE_LIMITED`, `RUNTIME_UNAVAILABLE`, or provider
unavailability), the stage-1 receipt remains an AGY receipt and returns
`fallback_required: prometheus` to the parent/native host. Only a returned
stage-2 native Prometheus result may set `actual_worker: prometheus`; it must
bind the parent request, Issue/repository/CWD/worktree, fallback reason,
attempt, result status, changed paths, and observed validation. Quality failures
stay on the current compatible worker for repair. Record `requested_worker`,
`actual_worker`, `fallback_triggered`, and `fallback_reason` in every worker
route.
Semantic routes remain request-time details, not a model-manager service.

## State

Keep only these durable workflow files in the repository-local ignored state
directory:

```text
<repo>/.agents/sessions/issue-<N>/session.yaml
<repo>/.agents/sessions/issue-<N>/tasks.yaml
<repo>/.agents/sessions/issue-<N>/review/athena-<head7>-<axis>-r<round>.yaml
```

`session.yaml` owns lifecycle identity and the compact review cycle. A cycle
records the candidate, round, separate WORK/GOAL receipt identities, native
reviewer IDs, and stale/status state; an unrun axis is `not_run`. `tasks.yaml` owns the
small DAG, AC/file/evidence mapping, supporting-document dispositions, and an
optional bounded `executions[]` list of compact pointers (`actor`, `primitive`,
`display_label`, `attempt`, `receipt`, `result`, `validation`). It preserves
AGY, fallback, and repair attempts without storing prompts or transcripts.
Native runtime bindings belong to the `harness-worker` boundary,
not to these files. Never store transcripts or hidden reasoning. Each formal
Athena attempt has a fresh native reviewer thread/session and a deterministic
display label; never resume an Athena thread for formal re-review. Existing
receipt paths are never overwritten.

## Hard gates

- Re-read the live Issue and current base before mutation.
- Preserve and fingerprint pre-existing work; ambiguous overlap is BLOCKED.
- Canonicalize real repository/CWD paths and reject mismatched sessions.
- Treat Git as changed-file authority; every Issue-owned file maps to a task,
  relevant AC, disposition, and evidence.
- Missing evidence is `NOT_ASSESSED`, never PASS.
- A material mutation makes prior review stale.
- Terminal eligibility requires separate fresh WORK and GOAL reviews bound to
  the same candidate/base/criteria/evidence snapshot and different native
  reviewer sessions. A `joint` diagnostic cannot satisfy this gate.
- Only verified material findings or explicit parent-accepted semantic findings
  enter repair.
- Athena is fresh, read-only, exact-head, and non-binding. The parent/human
  owns acceptance, Draft PR creation, merge, and Issue closure.
- The acceptance helper only proves technical eligibility and stops at
  `awaiting_parent_decision`. It never reads an approval artifact or creates
  accepted state. Review evidence alone cannot create STOP.
- Parent acceptance and Draft PR publication are host-owned operations outside
  this repository process; repository YAML is not an authentication channel.
- Child executors, task completion, repair completion, tests, and tool calls
  never imply a commit. The parent owns commits and may create one only at a
  coherent, validated, reconciled recovery/review boundary. Do not create
  per-task, per-agent, per-test, retry, or WIP commits. Terminal history is
  classified as semantic checkpoint, repair checkpoint,
  authority/config reconciliation, or history noise; overlapping consecutive
  noise commits fail hygiene and must be compacted before final review.
- The local lifecycle is `candidate reviewed → technically eligible →
  awaiting_parent_decision → STOP`. External Cloud/GitHub tooling creates or
  updates the Draft PR after the local boundary.

## Deterministic helpers

```bash
python3 skills/issue-execution/scripts/issue_execution.py preflight ...
python3 skills/harness-worker/scripts/harness_worker.py run ...
python3 skills/issue-execution/scripts/issue_execution.py validate-receipt ...
python3 skills/issue-execution/scripts/issue_execution.py reconcile ...
```

Every AGY implementation request must carry the parent-selected canonical task
contract and pass through `scripts/delegation_prompt.py` before the worker is
invoked. The same renderer supplies the parent-native Prometheus request; the
qualification-only `identity` profile is the raw baseline. The renderer
preserves contract semantics and fingerprints both source and output; it never
selects the executor. See `references/delegation-prompt-provenance.md` for the
selective donor adaptation and rejected concepts, and
`references/delegation-prompt-cases.yaml` for DP-01 through DP-10.

The normal #107 lifecycle uses one parent issue-execution workflow and does not
create a user-visible Codex task for each stage. Use the AGY harness for the
primary bounded worker, the native parent dispatcher for Prometheus fallback,
and fresh native Athena review sessions for WORK then GOAL. `create_thread` is
not a normal execution primitive; create a user-visible task only when the
human explicitly asks for a separate task.

The scripts are bounded adapters, not an orchestration service. Live runtime
signals that are unavailable remain `NOT_ASSESSED`.

For the coupled #107/#113/#114 qualification, the local golden loop ends at
`awaiting_parent_decision`. Parent acceptance, Draft PR publication, and STOP
verification are external host actions and are not local qualification steps.
