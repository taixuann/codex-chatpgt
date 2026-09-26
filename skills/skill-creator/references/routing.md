# Routing

Owner: target-skill discovery and trigger behavior. Consumers: all four peer
actions and routing evaluation. Persistence: the target description plus
revision-bound cases; no hidden router state. Non-overlap: discovery owns
capability placement, while routing owns selection signals and collisions.

Front-load what the skill does and when it applies. Test explicit CREATE,
INSTALL, UPDATE, and AUDIT requests; contextual and noisy positives; adjacent
coding, native, AGENTS, sibling, and explicit opt-out negatives. Keep held-out
cases separate from description tuning.

Measure activation separately from task quality with TP/FN/FP/TN,
precision/recall, false-positive rate, partition, and description revision.
Use isolated .agents/skills fixtures and require an explicit host load signal.
Without one, report NOT_ASSESSED rather than inferring activation from prose.
