# AUDIT workflow

AUDIT is a holistic, read-only-by-default inspection. It answers whether a
skill should continue to exist in its current form and location. It returns a
recommendation; it does not apply that recommendation. Authorized repair is a
separate UPDATE.

## Flow and dispositions

```text
CURRENT SKILL + SYSTEM CONTEXT
→ NECESSITY / OWNERSHIP
→ PLACEMENT
→ UPSTREAM / PROVENANCE
→ ROUTING / COLLISION
→ USAGE / VALUE / COST
→ RESOURCES / DEPENDENCIES
→ QUALITY / EVIDENCE / PORTABILITY
→ ONE DISPOSITION + FINDINGS
```

Return exactly one of `HEALTHY`, `UPDATE_NEEDED`, `LOCALIZE`, `MERGE`,
`DISABLE`, `RETIRE`, or `BLOCKED`. Do not mutate files, active discovery, or
remote state while auditing. A blocked provenance, ownership, collision, or
runtime question stays `BLOCKED`.

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

For audit cases, inspect the isolated fixture and record the evidence that
supports the disposition. If applying the disposition would change placement,
ownership, resources, or active discovery, record it as a recommendation and
route the authorized mutation through UPDATE. Do not preserve two overlapping
implicitly active skills merely because both are structurally valid.
