# Convergence audit

Before handoff, verify that the synthesized intent still reflects the
investigation. Check for contradictions, silent scope expansion, implementation
prescription leaking into intent, dropped user decisions or open questions,
unsupported orientation claims, overwritten canonical decisions, and dangling
evidence IDs. Machine-checkable checks belong in `intentctl validate` and
semantic quality remains a behavioral-review concern.
