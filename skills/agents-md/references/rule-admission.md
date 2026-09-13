# Rule admission

Classify every retained or proposed instruction before editing it:

- `NON_INFERABLE_REQUIRED`: safety, authority, or repository truth that must
  remain explicit;
- `NON_INFERABLE_HELPFUL`: useful evidence-backed context that is not a hard
  gate;
- `INFERABLE`: remove unless a demonstrated failure makes it necessary;
- `DUPLICATED`: remove the copy and keep one owner;
- `MECHANICALLY_ENFORCEABLE_ELSEWHERE`: move to CI, a validator, or a tool;
- `PROCEDURE_BELONGS_IN_SKILL`: move conditional workflow out of AGENTS;
- `PERSONAL_PREFERENCE`: keep out of repository authority;
- `MODEL_SPECIFIC_LEGACY_COMPENSATION`: remove or narrow unless current
  behavior still demonstrates a need;
- `STALE_OR_UNSUPPORTED`: remove, correct, or mark the claim
  `NOT_ASSESSED`.

The valid outcomes are `NO_CHANGE`, `REMOVE`, `MOVE_TO_SKILL`,
`MOVE_TO_CI`, `MOVE_TO_README`, `RELOCATE`, and `UPDATE_MINIMALLY`.
Do not add a rule because it sounds generally good. Check native behavior,
the current repository tree, the owning contract, deterministic enforcement,
and maintained candidates before selecting an owner.

Always-on safety/authority rules may be valuable even when rarely triggered.
Low frequency alone is not evidence for deletion. Situational procedures
usually belong in a Skill rather than root AGENTS.

Global guidance is runtime context, not repository-owned state. Propose global
changes separately and require explicit human authorization before mutation.
