---
name: harness-worker
description: "Run and qualify a bounded worker harness request when a governed workflow needs a supported backend invoked with an exact repository/CWD/context, fresh or resumable native session evidence, bounded results, and disposable runtime cleanup."
---

# Harness Worker

Use this skill for bounded worker-harness work: bind the request to its exact
repository, worktree, CWD, context, permission policy, and allowed paths;
invoke the selected supported backend; preserve fresh/resume semantics and
native session/usage fields; normalize availability and execution errors; and
return one bounded receipt.

The current v1 backend is native AGY. The skill name is future-neutral, but it
does not provide a generic router, model manager, plugin registry, or provider
fallback. Availability failures are reported to the parent, which alone may
invoke its native Prometheus fallback. Quality failures stay on the current
worker for repair. Deferred providers are outside the active v1 lane.

The harness owns disposable runtime roots and removes only roots it created.
It never owns Issue lifecycle, acceptance, Athena review, commits, PR state,
or parent decisions. For AGY implementation dispatch, it consumes the
parent-rendered request and never reads or reinterprets the GitHub Issue.
Role mentions such as `subagent://prometheus` are labels, not executable
transport commands; the parent/native dispatcher resolves the role and binds
the selected executor before this worker is called.

For the implementation contract, read `references/contracts.md`. Run the bounded
adapter with:

```text
python3 skills/harness-worker/scripts/harness_worker.py run --request REQUEST --registry REGISTRY --receipt RECEIPT
```

Production AGY launches fail closed unless the caller explicitly supplies
`HEADLESS_CLI_ALLOW_NETWORK=1` and one or more existing, non-repository
directories in `HEADLESS_CLI_RUNTIME_WRITE_ROOTS`. The harness passes these
allowlisted values into the sandbox; it never reads or copies credentials.
On POSIX, AGY is attached to a fresh PTY so non-TTY `--print` output remains
capturable; terminal control bytes are removed before parsing, which still
accepts only AGY's documented JSON envelope.
