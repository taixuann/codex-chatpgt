from __future__ import annotations

SIGNALS = {
    "interfaces": "software-design/domain boundaries",
    "contexts": "software-design/domain boundaries",
    "state": "data-systems/operations",
    "migration": "data-systems/operations",
    "recovery": "data-systems/operations",
    "trust": "threat-modeling",
    "authorization": "threat-modeling",
    "external-input": "threat-modeling",
    "agent": "ai-engineering/agent design",
    "model": "ai-engineering/agent design",
    "rag": "ai-engineering/agent design",
}

def select_references(signals: list[str], *, canonical_pattern: bool = False) -> list[str]:
    if canonical_pattern:
        return []
    selected = []
    for signal in signals:
        focus = SIGNALS.get(signal.lower())
        if focus and focus not in selected:
            selected.append(focus)
    return selected[:2]
