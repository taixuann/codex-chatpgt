# MAINTAIN

Use this reference when a skill may be stale, redundant, expensive, or wrongly
placed.

## Audit

Check each dimension and record evidence:

- `UPSTREAM`: has the pinned source changed?
- `PROVENANCE`: can the adaptation still be traced and licensed?
- `TRIGGER`: has the surrounding skill set changed?
- `COLLISION`: does a sibling now own the same request?
- `USAGE`: does the skill still earn existence?
- `PLACEMENT`: should it be project-local rather than global?
- `RESOURCES`: are scripts, references, and assets used and necessary?
- `DEPENDENCY`: are tool/runtime assumptions current and portable?
- `QUALITY`: do must-pass, regression, and held-out cases still pass?
- `COST`: is context, token, command, or maintenance cost justified?

For maintenance cases, execute the selected disposition in an isolated fixture
when it changes placement, ownership, resources, or active discovery. Record
the before/after artifact delta and the evidence that the disposition was
actually applied; a recommendation without the resulting state is not a
maintenance proof.

Return exactly one disposition:

`UNCHANGED`, `UPDATE`, `LOCALIZE`, `MERGE`, `DISABLE`, `RETIRE`, or `BLOCKED`.

Do not preserve two overlapping implicitly active skills merely because both
are structurally valid. A blocked provenance, collision, or runtime question
stays `BLOCKED`; it is not silently converted to an update.
