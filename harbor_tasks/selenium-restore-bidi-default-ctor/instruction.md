# Restore the missing single-argument `BiDi` constructor

The Selenium Java BiDi module currently exposes only the two-argument
constructor `BiDi(Connection connection, Duration timeout)` in
`java/src/org/openqa/selenium/bidi/BiDi.java`. Downstream projects (notably
the Appium Java client) historically constructed `BiDi` with just a
`Connection`, and that one-argument constructor is no longer present.
Remove of that constructor is a breaking change for those callers.

## Required behavior

Provide a public `BiDi` constructor that takes a single `Connection`
parameter. When called via this constructor, the resulting `BiDi` instance
must use a default WebSocket timeout of **30 seconds** (i.e.
`Duration.ofSeconds(30)`). The existing two-argument
`BiDi(Connection, Duration)` constructor must continue to work unchanged —
both constructors should coexist.

The new constructor is intended to be removed in a future major release; it
exists only to give downstream callers a deprecation window. Mark it
accordingly so that callers who use it see a removal warning at compile
time.

## What to follow

This change touches the Java BiDi public API surface, which is called out
as a high-risk area in `AGENTS.md`. Read the repo's agent-facing
documentation before writing code:

- `AGENTS.md` (root) — the project's invariants, deprecation policy, and
  general code guidelines.
- `java/AGENTS.md` — Java-specific conventions, including the deprecation
  annotation pattern and the Javadoc style expected on public APIs.

Match the conventions described there exactly; the evaluator checks both
the runtime behavior of the constructor and adherence to those conventions.

## Out of scope

Do not modify any other files, do not reformat surrounding code, and do not
alter the existing two-argument constructor's signature or behavior.
