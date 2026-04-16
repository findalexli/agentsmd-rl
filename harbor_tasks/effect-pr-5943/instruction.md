# Task: Fix Crash in PostgreSQL Pool Connection Handler

## Symptom

In the `@effect/sql-pg` package, the code that acquires PostgreSQL pool connections crashes when `pool.connect` returns a null client. The code uses non-null assertions on the returned client, but pg's `pool.connect` callback can return both an error AND a null client simultaneously. When the client is null, the code attempts to call methods on null, causing a crash.

## Expected Behavior

The pool connection code in `PgClient.ts` should handle all edge cases safely:

- No unsafe non-null assertions should be used on the pool client variable in the `reserveRaw` function
- The code must explicitly check for a null/falsy client from the pool callback and return early in those cases
- When no client is returned, a `SqlError` should be raised with:
  - `message`: `"Failed to acquire connection for transaction"`
  - `cause`: a new `Error("No client returned")`

## Context

The pg library's `Pool.connect` callback signature is `(err: Error | null, client: PoolClient | null, release: () => void)`. Both `err` and `client` can be null independently. The existing code handles the `err` case but assumes the client is always non-null otherwise.

The `reserveRaw` function lives in `packages/sql-pg/src/PgClient.ts` and is defined as `const reserveRaw = Effect.async`.
