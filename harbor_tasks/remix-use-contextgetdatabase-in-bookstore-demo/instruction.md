# Use typed context keys for database access in bookstore demo

## Problem

The bookstore demo accesses the database by setting `context.db` directly as a property on the request context, then reading it back by destructuring `db` from the context object in route handlers. This requires a separate TypeScript module augmentation file (`app/types/context.db.ts`) to declare the `db` property on `RequestContext`.

This is inconsistent with how other request-scoped values like `Session` and `FormData` are stored and retrieved in the same demo — those use typed context keys with `context.set(Key, value)` and `get(Key)`.

## Expected Behavior

The database should be stored and retrieved using the same typed context key pattern already used for `Session` and `FormData`. The module augmentation file should be removed since it's no longer needed.

After fixing the code, update the relevant documentation to reflect the change. The demo's README describes how the database middleware works, and that description should match the actual implementation.

## Files to Look At

- `demos/bookstore/app/middleware/database.ts` — where the database is put on request context
- `demos/bookstore/app/types/context.db.ts` — the module augmentation that types `context.db`
- `demos/bookstore/app/` — route handlers that read the database from context (account, books, auth, cart, etc.)
- `demos/bookstore/README.md` — describes the demo's patterns including database middleware
