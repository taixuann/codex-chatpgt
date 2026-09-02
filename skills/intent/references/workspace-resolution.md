# Workspace anchor

Intent starts from the active runtime context. When the current working directory
is inside a Git checkout, resolve the repository root with Git, retain the CWD,
and load only the `AGENTS.md` files from that root down to the CWD. The current
repository and subtree are the default context boundary.

Do not scan sibling repositories or broad workspace directories. Escalate only
when the user names another repository, the source Issue belongs to another
repository, or bounded evidence shows the current repository cannot own the
request. Cloud reasoning may use GitHub state but must not infer unpushed local
state.

`intentctl workspace` is the mechanical implementation of this contract.
