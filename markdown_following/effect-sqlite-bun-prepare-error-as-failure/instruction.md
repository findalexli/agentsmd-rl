# `@effect/sql-sqlite-bun`: prepare errors leak as fiber defects

## Symptom

In `@effect/sql-sqlite-bun`'s `SqliteClient`, queries that fail at *prepare*
time (the underlying `db.query(sql)` call into `bun:sqlite`) currently surface
as fiber **defects** instead of typed `SqlError` failures. A defect is not
catchable by `Effect.catchAll`, so consumer code that wants to handle the
error (or simply continue) cannot.

Reproduction (a Bun script in the repo's `scratchpad/`, fully provided):

```ts
import { Reactivity } from "@effect/experimental"
import { SqliteClient } from "@effect/sql-sqlite-bun"
import { Effect } from "effect"

const program = Effect.gen(function*() {
  const sql = yield* SqliteClient.make({ filename: ":memory:" })

  // Non-existent table → bun:sqlite throws at db.query(sql) prepare time.
  // After the fix this should be catchable; before the fix it dies.
  return yield* sql`SELECT * FROM non_existent_table`.pipe(
    Effect.catchAll(() => Effect.succeed("recovered"))
  )
}).pipe(
  Effect.scoped,
  Effect.provide(Reactivity.layer)
)

await Effect.runPromise(program)
```

Today this rejects (the defect is not caught); after the fix, it resolves with
`"recovered"`.

The same problem applies to **any** error raised by `db.query(sql)`, not just
non-existent tables — for example a malformed SQL statement that fails to
parse at prepare time exhibits identical behavior.

## Expected behavior

Any failure originating from the SQLite client's preparation or execution of
a query — including failures thrown by `db.query(sql)` — must surface as a
typed `SqlError` failure (a `Cause.Fail` carrying a `SqlError` whose `_tag` is
`"SqlError"`), so that downstream code can handle it with `Effect.catchAll`,
`Effect.either`, etc., and the same `SqliteClient` instance remains usable
for further queries afterwards.

There must be no `Cause.Die` (defect) in the cause for these errors.

## Scope

- Package: `@effect/sql-sqlite-bun`
- The fix is local to the SQLite client's query helpers and should not change
  any public types or signatures.
- The two helper functions that drive `Effect`-returning query execution
  (one used for `.all()`, one for `.values()`) both have the same defect and
  must both be fixed.

## What is already correct

The `try { ... } catch (cause) { return Effect.fail(new SqlError(...)) }`
shape is already in place. The wrapper class and its message strings
(`"Failed to execute statement"`) do not need to change. The fix is about
*what is covered* by that try, not about introducing new error types.

## Code Style Requirements

The repo's CI runs the TypeScript typechecker (`tsc -b` / `pnpm check`) and
ESLint (`pnpm lint`) — both are hard gates and your changes must
typecheck and lint cleanly. Per `AGENTS.md`:

- "Zero Tolerance for Errors: All automated checks must pass."
- "Reduce comments: Avoid comments unless absolutely required to explain
  unusual or complex logic."
- "Clarity over Cleverness — Choose clear, maintainable solutions."
- "Always look at existing code in the repository to learn and follow
  established patterns before writing new code." Other `sql-sqlite-*`
  sibling packages already handle this case correctly — their pattern is
  the reference.
- "All pull requests must include a changeset in the `.changeset/`
  directory."

Tests run `tsc -b` against the `sql-sqlite-bun` package and an end-to-end
Bun probe that exercises the bug. Both must pass.
