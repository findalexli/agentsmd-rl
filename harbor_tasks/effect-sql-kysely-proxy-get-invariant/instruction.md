# sql-kysely: Proxy `get` invariant violation when hashing builders twice

You are working in the `Effect-TS/effect` monorepo at
`/workspace/effect`. The relevant package is **`@effect/sql-kysely`**
(under `packages/sql-kysely/`).

## Problem

The `@effect/sql-kysely` package wraps Kysely query builders in a JavaScript
`Proxy` so that builder instances become Effect-yieldable while preserving
Kysely's fluent API. The proxy's `get` trap is implemented by an internal
helper that returns wrapped functions for method properties, and recurses on
nested objects.

The wrapping interacts badly with `effect`'s `Hash` module. `Hash.hash(value)`
caches the computed hash on the value itself, using
`Object.defineProperty(target, sym, { value: n, writable: false, configurable: false })`.

The first call to `Hash.hash(builder)` succeeds and writes the cached hash
onto the underlying target. The **second** call traps through the proxy's
`get` and reads that cached property. Because the helper does not check the
property descriptor, it returns a different value (a wrapped function /
re-wrapped value) for what is, on the target, a non-configurable,
non-writable data property. V8 then throws:

```
TypeError: 'get' on proxy: property 'Symbol(effect/Hash)' is a read-only
and non-configurable data property on the proxy target but the proxy did
not return its actual value (expected 'value(){return hash2}' but got
'(...args)=>effectifyWith(target[prop].call(target,...args),commit,whitelist)')
```

This is the [ECMAScript proxy invariant for `get`](https://tc39.es/ecma262/#sec-proxy-object-internal-methods-and-internal-slots-get-p-receiver):
when a target property is non-configurable and non-writable, the trap MUST
return a value strictly equal to the target's property value.

### Reproduction

```ts
import * as SqlKysely from "@effect/sql-kysely/Kysely"
import SqliteDB from "better-sqlite3"
import { Hash } from "effect"
import { SqliteDialect } from "kysely"

const db = SqlKysely.make({
  dialect: new SqliteDialect({ database: new SqliteDB(":memory:") })
})

const builder = db.selectFrom("users").selectAll()

Hash.hash(builder)   // ok — caches hash on target
Hash.hash(builder)   // throws TypeError: 'get' on proxy: ...
```

## Required behavior

After your fix:

- `Hash.hash(builder)` may be called any number of times on a wrapped Kysely
  builder without throwing, for every builder shape (`selectFrom`,
  `insertInto`, `updateTable`, `deleteFrom`, builders with `.where`/
  `.set`/etc. chained on top).
- Repeated calls must return the **same numeric** hash value (the cached one).
- Reading any non-configurable, non-writable own property of a wrapped target
  through the proxy must return the property's actual value (object identity
  preserved for object-valued properties).
- Existing Kysely behavior must continue to work: queries still compile to
  the same SQL, and the upstream `Kysely.test.ts` and `Sqlite.test.ts` test
  suites still pass.

## Hints

- The fix lives in the proxy `handler.get` trap inside the package's
  internal proxy helper. It is a small, additive change — you do not need to
  refactor or rewrite the helper.
- `Object.getOwnPropertyDescriptor(target, prop)` tells you whether a
  property is non-configurable and non-writable.
- Add a changeset (under `.changeset/`) describing the fix at `patch` level
  for `@effect/sql-kysely`, as required by the repo's contribution rules
  (see `AGENTS.md`).

## Code style requirements

This repository uses the conventions in `AGENTS.md`. In particular:

- Run `pnpm lint-fix` after editing files (the codebase uses ESLint with
  the `@effect/eslint-plugin` ruleset).
- Run `pnpm check` for type checking (`tsc -b tsconfig.json`).
- Avoid unnecessary comments: only comment when it explains an unusual or
  non-obvious invariant (a one- or two-line note explaining *why* an
  ECMAScript-level invariant matters here is appropriate).
- Keep changes minimal and focused — clarity over cleverness.
- All pull requests must include a changeset under `.changeset/`.
