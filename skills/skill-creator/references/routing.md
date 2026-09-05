# ROUTING

Use this reference across CREATE, UPDATE, MAINTAIN, and EVALUATE. The
description is the primary routing signal, so front-load the action and user
cues; body instructions are available only after selection.

Test a small realistic corpus, not only obvious positives. Include explicit
positive requests, contextual/ambiguous requests, noisy real-world requests,
adjacent coding tasks, sibling-owned requests, and explicit “do not use or
modify a skill” requests. Keep a held-out subset that is not used to tune the
description.

Measure activation separately from task quality. Record TP/FN/FP/TN, precision,
recall, false-positive rate, the prompt partition, and the exact description
revision. A static case file does not prove native runtime routing; use an
isolated `.agents/skills/$SKILL_NAME/` fixture for runtime checks and fail
closed when the host exposes no load or trace signal.

The with-skill and without-skill controls must receive the same natural user
request. Do not tell the control group the skill name, intended disposition, or
that it is participating in a skill evaluation. Keep fixture setup and grading
outside the prompt, and treat an observed wrong selection as `FAIL`; reserve
`NOT_ASSESSED` for missing runtime evidence.
