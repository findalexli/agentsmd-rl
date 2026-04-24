# Task: Add connection string URL support to PrismaPgAdapterFactory

## PR
`prisma/prisma#29287` — "feat(adapter-pg): accept connection string URL in PrismaPg constructor"

## Context

`PrismaPgAdapterFactory` (in `packages/adapter-pg/src/pg.ts`) is the factory class for the Prisma PostgreSQL driver adapter. Its constructor currently accepts two overloads:

- `pg.Pool` — an existing `pg` pool instance
- `pg.PoolConfig` — a configuration object (with fields like `host`, `port`, `user`, `password`, `database`, `connectionString`, etc.)

Users want to pass a **raw connection string URL** directly, e.g.:
```ts
const factory = new PrismaPgAdapterFactory("postgresql://test:test@localhost:5432/test")
```

This is a common pattern — the `pg` library itself accepts `{ connectionString: "postgresql://..." }` as a config shorthand.

## Bug

When a plain string is passed, it is routed to the `PoolConfig` branch. At query execution time, `pg.Pool` internally checks `'password' in config`, which throws:

```
TypeError: Cannot use 'in' operator to search for 'password' in postgresql://test:test@localhost:5432/test
```

The string is a valid connection string URL but is not a valid `PoolConfig` object.

## Fix Required

Modify the `PrismaPgAdapterFactory` constructor to accept a third overload: a plain `string` connection URL.

When a string is received, the factory must:
1. Store `null` for `externalPool` (no pre-existing pool)
2. Store a `PoolConfig`-shaped object for `config` with a `connectionString` property equal to the input string

This way, when `connect()` calls `new pg.Pool(config)`, the pool receives the correct config shape.

## What you must do

1. Read `packages/adapter-pg/src/pg.ts` — locate the `PrismaPgAdapterFactory` class and its constructor
2. Add a string branch to the constructor type signature and runtime logic
3. Ensure the `config` field always ends up as a valid `pg.PoolConfig` object after construction
4. Verify with: `pnpm --filter @prisma/adapter-pg test -- --run` (all existing tests must pass)

## Key files

- `packages/adapter-pg/src/pg.ts` — the factory class (target of the fix)
- `packages/adapter-pg/src/__tests__/pg.test.ts` — existing test suite (36 tests)

## Reference: expected behavior

After the fix, the following must work:
```ts
const factory = new PrismaPgAdapterFactory("postgresql://user:pass@localhost:5432/mydb")
const adapter = await factory.connect()
// adapter is a valid PrismaPgAdapter
// adapter.underlyingDriver().options.connectionString === "postgresql://user:pass@localhost:5432/mydb"
```

## Notes

- Do not modify any test files
- The `pg` library's `Pool` constructor accepts `{ connectionString: string }` as a config — use this internally
- `externalPool` should be `null` when constructed from a string

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `eslint (JS/TS linter)`
