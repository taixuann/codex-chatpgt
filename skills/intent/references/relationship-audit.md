# Relationship and staleness audit

For an Issue or a focused/deep request, search only the canonical Issue/PR and
repository surfaces implicated by the source. Record each asserted relationship
with a real locator and observation time. A relationship that was not checked is
not the same as a relationship that was absent.

Compare observed repository HEAD and relevant Issue/PR timestamps with the
source observation. Staleness is a review signal, not automatic invalidation:
`fresh`, `stale_soft`, `stale_review_required`, or `stale_hard`.
