# Fix `evaluateArg` so DateTime cursor values compare correctly

You are working in the Prisma monorepo, checked out at `/workspace/prisma`.
The relevant package is `@prisma/client-engine-runtime` under
`packages/client-engine-runtime/`.

## Symptom

When a Prisma Client query uses a DateTime value as a cursor against a
`@db.Date` column, pagination silently returns the wrong rows. Concretely:

1. A consumer fetches a row whose `createdAt` field is a DateTime backed by a
   `DATE`-typed column. The Prisma Client materializes that field as a JS
   `Date`.
2. The consumer passes that row's `createdAt` value back into a follow-up
   query as a `cursor` (e.g. inside a compound `appId_createdAt` cursor).
3. Internally, the cursor value travels through the query plan as a
   `PrismaValuePlaceholder` of type `'DateTime'`. By the time it is bound to
   the SQL parameter, the value has been serialised through the query plan
   protocol and arrives in the interpreter's scope as an **ISO-formatted
   string**, not a `Date`.
4. The pagination logic later compares this scope value against rows
   returned from the database (where the `@db.Date` column was hydrated as a
   `Date`). The comparison is `string === Date`, which is always `false`.
   Pagination is broken.

The query interpreter does not have parameter type information at the
comparison site. The fix must happen earlier — when the placeholder is
resolved against the scope.

## Where to look

The placeholder-to-value resolution lives in the
`@prisma/client-engine-runtime` package, inside the exported function
`evaluateArg(arg, scope, generators)`. Today, when `arg` is a
`PrismaValuePlaceholder`, `evaluateArg` looks the value up in `scope` and
returns it unchanged regardless of the placeholder's declared
`prisma__value.type`.

Relevant types live alongside the interpreter in the same package:

```ts
export type PrismaValuePlaceholder = {
  prisma__type: 'param'
  prisma__value: { name: string; type: string }
}
```

`prisma__value.type` is the placeholder's nominal Prisma scalar type — for
the bug above it will be the literal string `'DateTime'`.

## Required behavior

After your fix, calling `evaluateArg(placeholder, scope, {})` must satisfy:

1. **DateTime placeholder + string in scope → JS `Date`.**
   For `placeholder = { prisma__type: 'param', prisma__value: { name: 'cursor', type: 'DateTime' } }`
   and `scope = { cursor: '2025-01-03T00:00:00.000Z' }`, the result is a
   `Date` instance whose `.toISOString()` equals
   `'2025-01-03T00:00:00.000Z'`.

2. **DateTime placeholder + `Date` already in scope → unchanged.** The
   resolved value remains the same `Date` (or an equivalent `Date`) — do not
   round-trip through string.

3. **Non-DateTime placeholder → value is returned untouched.** A `String`
   placeholder whose scope value happens to look like an ISO timestamp must
   still resolve to the original string. An `Int` placeholder still resolves
   to a number. Do not coerce types other than `DateTime`.

4. **Arrays of placeholders work elementwise.** When `arg` is an array of
   placeholders, each element is evaluated and the array of resolved values
   is returned (existing behavior preserved).

5. **All existing tests must keep passing**, including the existing
   render-query unit tests and the broader
   `pnpm --filter @prisma/client-engine-runtime test` suite.

## Verifying locally

The package's tests run with vitest:

```bash
pnpm --filter @prisma/client-engine-runtime test
```

You can build the package with:

```bash
pnpm --filter @prisma/client-engine-runtime build
```

Both must succeed.

## Code Style Requirements

This repository's `AGENTS.md` (root) defines coding conventions you must
follow. In particular:

- **Comments answer WHY, not WHAT.** Do not add inline comments that
  restate what the code does ("// assigns found to arg"). Inline comments
  are reserved for *why* the code exists or behaves a certain way — context,
  background, links to issues, reasons behind a decision. The DateTime
  branch warrants a short comment explaining the cursor-vs-database
  comparison reason; do not add commentary that merely narrates the
  assignment or branch shape.
- **Keep changes ASCII** unless the surrounding file already uses Unicode.
- **Respect existing structure** — keep the change tightly scoped to the
  placeholder-resolution branch; do not refactor unrelated code.
- **kebab-case for any new file names** (e.g. `query-utils.ts`); avoid
  introducing barrel files.

The full conventions live in `/workspace/prisma/AGENTS.md`.
