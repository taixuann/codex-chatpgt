# Harness-worker contract

The parent workflow supplies one bounded request. The request binds the Issue
task, canonical repository/root/worktree/CWD, allowed paths, permission
policy, required context, semantic route, session policy, output locations,
and supported backend command. The harness validates those bindings before
launch.

The harness owns backend mechanics only:

1. bind backend options to the request and reject caller overrides;
2. use a fresh native session or resume the exact stored native session;
3. preserve native session and genuinely exposed usage fields;
4. normalize success, bounded output, availability, protocol, and execution
   errors into one receipt;
5. snapshot Git/runtime state and reject unexpected mutation; and
6. clean disposable runtime roots created by the harness.

AGY is the active v1 backend. Availability codes are limited to
`QUOTA_EXHAUSTED`, `RATE_LIMITED`, `RUNTIME_UNAVAILABLE`, and
`PROVIDER_UNAVAILABLE`. An AGY availability receipt remains an AGY stage-1
receipt and may request the parent-owned native Prometheus fallback; it never
claims that Prometheus ran. Quality or correctness failures remain on AGY.

The parent retains worker selection, fallback authorization, Issue lifecycle,
validation/reconciliation, Athena review, acceptance, commit, PR, and STOP
decisions. No receipt can manufacture those states.

Production AGY launch is fail-closed before process creation when
`HEADLESS_CLI_ALLOW_NETWORK=1` is absent or
`HEADLESS_CLI_RUNTIME_WRITE_ROOTS` does not name an existing directory outside
the repository. This prevents an incomplete macOS sandbox from being
misreported as an unexplained hang; the resulting `RUNTIME_UNAVAILABLE`
receipt remains eligible for the parent-owned Prometheus fallback.

On POSIX hosts, AGY runs attached to a fresh PTY because upstream print mode
has reported empty or hanging output when stdout is a pipe. PTY capture is a
transport workaround only; it does not change the prompt, permissions, trust
boundary, or receipt authority. Unsupported hosts fail closed as
`RUNTIME_UNAVAILABLE`.

Required skills in `expected_context` must be present in the resolved project
skill roots; missing skills fail closed as `CONTEXT_CONTRACT_UNVERIFIED`.
Production AGY requests must carry the parent-rendered prompt, renderer
version, source-contract fingerprint, rendered-prompt fingerprint, and the
canonical source contract so the worker can verify both hashes before launch.
