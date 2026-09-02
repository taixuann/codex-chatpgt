# Evidence and claim classification

Use lightweight claims rather than a knowledge graph. Every material claim has
one state:

- `CONFIRMED`: directly supported by a retained evidence reference.
- `INFERRED`: a reasoned interpretation that remains marked as inference.
- `UNKNOWN`: unresolved or not yet observed.
- `USER_DECISION`: an authority or preference supplied by the user.
- `PROPOSED`: a candidate direction, not current state.

`CONFIRMED` claims must list evidence IDs. Evidence entries retain a locator,
kind, observation time, and observed repository/Issue revision when relevant.
Never silently upgrade `UNKNOWN`, `INFERRED`, or `PROPOSED` to fact.
