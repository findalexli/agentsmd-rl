# pg Statement Name Generator

The Prisma PostgreSQL adapter (`packages/adapter-pg`) currently sends every query to the database without naming the prepared statement. This prevents `pg` from caching statements, which hurts performance for repeated queries.

Users want to leverage `pg`'s prepared statement caching by providing a custom name generator function.

## What's Broken

The `PrismaPgOptions` interface in `packages/adapter-pg/src/pg.ts` does not expose a way to configure statement naming. When `pg.Client#query()` is called, it receives only `text`, `values`, and `rowMode` — no `name` property — so the underlying statement cache is never used.

## Expected Behavior

When a `statementNameGenerator` function is provided in `PrismaPgOptions`, it is called with the query object and its result is passed as the `name` property to `pg.Client#query()`. When no generator is provided, the `name` property is absent from the query config.

The option must be documented with a JSDoc comment in `PrismaPgOptions`.

## Requirements

The implementation must satisfy the following:

1. **Option name**: `statementNameGenerator` must be added to `PrismaPgOptions`
2. **Generator invocation**: The generator must be invoked in the query method, and its result must be assigned to the `name` property passed to `pg.Client#query()`
3. **Type export**: A type alias for the generator function must be exported, accepting a query object and returning a string. The type must be named `StatementNameGenerator` and must be callable with a single query argument.
4. **Test coverage**: `pg.test.ts` must include two test cases with the following titles:
   - "should pass generated name when statement name generator is provided"
   - "should not pass name when statement name generator is not provided"
5. **Import**: The test file must import `SqlQuery` from `@prisma/driver-adapter-utils`

## Key Files

- `packages/adapter-pg/src/pg.ts` — `PrismaPgOptions`, `PgQueryable.queryRaw()`
- `packages/adapter-pg/src/__tests__/pg.test.ts` — adapter test suite

## Relevant Types

- `SqlQuery` from `@prisma/driver-adapter-utils` — the query object passed to `queryRaw`
- The `pg.Client#query()` config accepts a `name` property for prepared statement identification

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `prettier (JS/TS/JSON/Markdown formatter)`
- `eslint (JS/TS linter)`
