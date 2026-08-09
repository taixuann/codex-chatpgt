# Historical Franky change records

Existing records are retained as immutable historical provenance. Ordinary
repository work now uses the GitHub Issue / optional PLAN / PR / CI surface.
Create a new `CHG-YYYYMMDD-NNN/change.yaml` only when a named machine or audit
consumer requires it, or when an explicit contract says it is required. Never
create `result.md` by default. Promotion remains explicit and is never
automatic.
