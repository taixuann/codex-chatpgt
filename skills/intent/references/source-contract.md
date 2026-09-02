# Intent source contract

`intent` accepts exactly two origin branches. The legacy packet field
`source.kind: user` is the serialized spelling of the `user_idea` origin;
`intent_run.origin.type` uses the explicit `user_idea` name.

| Origin | Packet source kind | Run-state origin type |
| --- | --- | --- |
| User idea / request | `user` | `user_idea` |
| GitHub Issue | `github_issue` | `github_issue` |

Packet source kinds:

| `source.kind` | Required locator | Meaning |
| --- | --- | --- |
| `user` | `conversation`, `user-request:<ref>`, or `pasted-text:<ref>` | The current user's request or explicitly pasted text |
| `github_issue` | `owner/repo#<number>` or canonical `https://github.com/owner/repo/issues/<number>` | An existing GitHub Issue used as the request source |

The locator forms are intentionally narrow so a packet cannot claim arbitrary
text or a non-GitHub URL as its origin. The deterministic validator checks the
syntax; it does not retrieve the Issue or inspect external conversation state.

Other material is supporting context only. A plan, review, memory entry,
generated report, or agent proposal must not be promoted to `source.kind`.

The source is evidence, not permission. Reading an Issue does not authorize
editing it, opening a new Issue, assigning work, or changing repository state.
