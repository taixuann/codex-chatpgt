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
isolated `.agents/skills/<skill-name>/` fixture for runtime checks and fail
closed when the host exposes no load or trace signal.
