# Intent/plan to session bridge

Intent and plan packets are conversational or derived planning artifacts. A
session packet is an optional persistence boundary for a governed,
multi-session task; it is not a replacement workflow or a second source of
authority.

## When to create a session packet

Create or resume one only when the user explicitly wants persistence/handoff or
the governing task contract requires a resumable evidence record. Do not create
one for every raw idea, and do not treat silence as approval to write files.

## Mapping

1. Keep the validated `intent_packet` in the conversation until the user
   confirms it.
2. When persistence is approved, use
   `skills/control-plane/session-packet-management` and its templates. Record
   the intent packet as bounded source/context evidence and retain its source
   locator, confirmation state, and observed commit or timestamp in
   `references.yaml`/`context.md`.
3. Feed only a confirmed intent packet into `plan`. Record the resulting plan
   and task decomposition in the packet's `plan.md`/`task.md` projections when
   the owning contract permits it.
4. Keep Issue/PLAN, the repository operating workflow, and task contracts as
   canonical authority. The session packet links to them; it does not redefine
   their gates or approvals.

## Target convention

- Codex control-plane repository: `documentation/sessions/<session-id>/`.
- Project repository: `<repo>/.agents/sessions/<session-id>/`.
- `.agent/sessions/` is not a default convention.

Do not consolidate these locations in an intent/plan change. Such a move would
require a coordinated migration of validators, CI, allowlists, schemas,
historical links, and exact-head review.
