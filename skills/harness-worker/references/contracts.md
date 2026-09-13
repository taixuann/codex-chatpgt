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
5. snapshot Git/runtime state, including Git control metadata outside the
   worktree, and reject unexpected mutation; and
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
the repository. `HEADLESS_CLI_RUNTIME_READ_ROOTS` must also explicitly name
existing, non-repository directories needed for configuration, authentication,
cache, or temporary runtime state; these roots are read-allowlisted only and
are never inferred from `HOME`. This prevents an incomplete macOS sandbox from
being misreported as an unexplained hang; the resulting `RUNTIME_UNAVAILABLE`
receipt remains eligible for the parent-owned Prometheus fallback.

Q0 runs before the native process launch. It records a capability fingerprint
without repository payload and requires
`HEADLESS_CLI_REPOSITORY_EGRESS_ALLOWED=1` for the default repository stage.
When that host gate is absent, the receipt records
`live_qualification.status: NOT_ASSESSED`,
`live_qualification.reason: HOST_REPOSITORY_EGRESS_BLOCKED`,
`provider_launched: false`, and a retry condition of `capability fingerprint
changes`; the provider is not invoked.
Q0 also runs the resolved AGY executable with `--version` inside the declared
sandbox. The macOS loader exception is deny-listed for `/Users`, temporary
directories, and credential paths, then exact runtime inputs are reopened. If
that startup probe aborts, the receipt uses
`HOST_AGY_SANDBOX_INCOMPATIBLE` and keeps `provider_launched: false`.
The worker always binds AGY's native `--sandbox` flag for provider turns;
without it, AGY can wait on its own permission boundary even when the outer
host sandbox is correctly configured. It binds one `--add-dir` to the exact
request CWD. Bounded-write turns also use `--mode accept-edits` so headless
file creation is non-interactive; read-only turns reject an execution mode.

On POSIX hosts, AGY runs attached to a fresh PTY because upstream print mode
has reported empty or hanging output when stdout is a pipe. PTY capture is a
transport workaround only; it does not change the prompt, permissions, trust
boundary, or receipt authority. Unsupported hosts fail closed as
`RUNTIME_UNAVAILABLE`.
The capture loop stops early on AGY's interactive-auth markers and classifies
the attempt as `AUTH_REQUIRED`, preventing a repeated auth prompt from being
reported only as `TIMED_OUT` or `NOT_ASSESSED`.

Required skills in `expected_context` must be present in the resolved project
skill roots; missing skills fail closed as `CONTEXT_CONTRACT_UNVERIFIED`.
The request also supplies the expected instruction fingerprint and the
effective-context fingerprint; both must match the normalized receipt.
Production AGY requests must carry the parent-rendered prompt, renderer
version, source-contract fingerprint, rendered-prompt fingerprint, and the
canonical source contract so the worker can verify both hashes before launch.
Registry state is derived from the normalized receipt: only a valid native
session without an authentication or session-binding failure is resumable;
non-resumable results remain explicitly failed even when the process exits 0.
