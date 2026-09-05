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
3. Materialize one intent-stage packet at `<repository-root>/.agents/sessions/<session-id>/`
   with `context.md`, `intent.md`, and `references.yaml`. Feed only a confirmed
   intent packet into `plan`; Plan extends the same packet with `plan.md` (and
   `task.md` only when required), rather than creating a second session.
4. Keep Issue/PLAN, the repository operating workflow, and task contracts as
   canonical authority. The session packet links to them; it does not redefine
   their gates or approvals.

## Target convention

Every repository uses `<repository-root>/.agents/sessions/<session-id>/` for
new live packets. Existing legacy session material is history only and is never
a new packet target.
