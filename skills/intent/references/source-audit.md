# Intent source audit

`intent` has two admissible source branches. The branch changes how evidence
is collected, not who may mutate the repository.

## User request branch

Use the current user message or explicitly pasted wording as the source. Keep
the locator as `conversation`, `user-request:<ref>`, or
`pasted-text:<ref>`. Ask only the smallest questions needed to establish the
outcome, audience, constraints, success criteria, and out-of-scope boundary.
`interview-me` owns one-question-at-a-time clarification; `idea-refine` owns
alternatives and assumption testing; `define-goal` owns measurable objective
and acceptance shaping.

## GitHub Issue branch

Read the existing Issue without editing it. Preserve the canonical locator
(`owner/repo#number` or the canonical Issue URL) and record the observed
title/body/labels, timestamp, and source revision or URL in the packet's
supporting evidence. Audit for:

- a stated problem and intended outcome;
- affected users or components;
- reproducible evidence or examples;
- explicit acceptance signals and constraints;
- missing, contradictory, or stale requirements.

If material information is missing, route to `interview-me` or leave the
packet unconfirmed. If the Issue is sufficiently clear, route to
`define-goal`. Never rewrite, assign, close, or comment on the Issue as an
intent side effect.

## Common audit rules

- A source locator is provenance, not permission.
- Repository files, memory, reviews, and agent suggestions are supporting
  context only; they cannot become the source silently.
- Do not claim that an Issue was retrieved or validated unless the observed
  evidence is retained with its timestamp and locator.
- Run `validate_intent_packet.py` after normalization. The validator checks
  packet shape and locator syntax; it does not fetch GitHub or prove the
  conversation state.
