# Map PostgreSQL `22P02` errors in the pg / neon / ppg driver adapters

This monorepo (`/workspace/prisma`) ships three Postgres-flavoured driver
adapters — `@prisma/adapter-pg`, `@prisma/adapter-neon`, and
`@prisma/adapter-ppg` — each of which translates raw database errors into a
shared `MappedError` discriminated union from `@prisma/driver-adapter-utils`.
The `MappedError` value is later picked up by
`@prisma/client-engine-runtime` and turned into a Prisma user-facing error
code (`P2xxx`).

## The bug

When a PostgreSQL server rejects a value with SQLSTATE
**`22P02`** (`invalid_text_representation`, also rendered as the
"invalid input value" / "invalid input syntax" family of messages), none of
the three adapters above currently recognise the code. The error falls
through their `mapDriverError` switch into the generic `kind: 'postgres'`
branch, which the engine cannot translate into a structured Prisma error
code — so the user sees an opaque 500-class failure instead of a proper
validation error.

A common way to reproduce this in production is inserting an enum value
that exists in the Prisma schema but not in the underlying database enum
(for example, after the database type was migrated out-of-band). Postgres
returns `22P02` with a message like
`invalid input value for enum "Status": "PENDING"`, and the engine should
report this as the Prisma "Data validation error" rather than an internal
error.

## What you need to do

Make the three Postgres adapters and the engine error mapper agree on a
new structured error variant for `22P02`:

1. Extend the shared `MappedError` discriminated union (in
   `@prisma/driver-adapter-utils`) with a new variant whose discriminator is
   `kind: 'InvalidInputValue'` and which carries a `message: string` field.
   The variant must be added in addition to (not in place of) the existing
   variants — none of the existing ones may be removed or renamed.

2. In each of `@prisma/adapter-pg`, `@prisma/adapter-neon`, and
   `@prisma/adapter-ppg`, recognise SQLSTATE `'22P02'` in
   `convertDriverError` and return the new `InvalidInputValue` variant. The
   `message` field must be populated from the database error's own
   `message` (so the user-facing text such as
   `invalid input value for enum "Status": "PENDING"` is preserved
   verbatim). The wrapper around `mapDriverError` already supplies
   `originalCode` and `originalMessage`; do not remove that behaviour.

3. In `@prisma/client-engine-runtime`'s user-facing error mapper, route
   the new variant to:

   - Prisma error code **`P2007`** (the existing "Data validation error"
     code) from the function that returns the `P2xxx` string for a given
     `MappedError`.
   - A rendered message of the exact form
     ``Invalid input value: ${err.cause.message}``
     from the function that renders the human-readable text. (The leading
     literal must be the words `Invalid input value:` followed by a single
     space, followed by the original message.)

   Place the new branches in the same switch statements that already
   handle the other `MappedError` variants. Do not change the existing
   `assertNever` exhaustiveness behaviour.

## Acceptance criteria

- Calling `convertDriverError({ code: '22P02', message, severity: 'ERROR' })`
  on each of the three adapters returns
  `{ kind: 'InvalidInputValue', message, originalCode: '22P02', originalMessage: message }`
  — i.e. the exact object the existing tests for sibling codes (`22001`,
  `22003`, `23505`, …) follow as a shape.
- `pnpm --filter @prisma/adapter-pg test` and
  `pnpm --filter @prisma/adapter-neon test` continue to pass — no
  regressions on the existing per-code unit tests.
- TypeScript compiles for any module that exhaustively switches on
  `MappedError['kind']` (i.e. the new variant must be reachable in those
  switches without breaking `assertNever`).

## Notes / repo conventions

- New TypeScript files (none are required for this fix) must be named in
  **kebab-case** (e.g. `my-helper.ts`).
- Do **not** introduce barrel `index.ts` re-export files; import directly
  from the source module.
- Keep the diff ASCII unless a file already contains non-ASCII characters.
- The build/test runner is `pnpm` (workspace-aware); run package-scoped
  tests via `pnpm --filter @prisma/<pkg> test`.
