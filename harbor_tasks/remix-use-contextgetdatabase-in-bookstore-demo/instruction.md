# Use typed context keys for database access in bookstore demo

## Problem

The bookstore demo accesses the database by setting `context.db` directly as a property on the request context, then reading it back by destructuring `db` from the context object in route handlers. This requires a separate TypeScript module augmentation file (`app/types/context.db.ts`) to declare the `db` property on `RequestContext`.

This is inconsistent with how other request-scoped values like `Session` and `FormData` are stored and retrieved in the same demo — those use typed context keys with `context.set(Key, value)` and `get(Key)`.

## Expected Behavior

The database should be stored and retrieved using the same typed context key pattern already used for `Session` and `FormData`. Specifically:

- The typed context key for the database is `Database`, imported from `remix/data-table`.
- In the database middleware (`app/middleware/database.ts`), the database handle should be stored using `context.set(Database, db)` instead of assigning `context.db` directly. The old `context.db` assignment must be removed.
- In the auth middleware (`app/middleware/auth.ts`), the database should be retrieved using `get(Database)` instead of destructuring `db` from the request context. This file also needs to import `Database` from `remix/data-table`.
- All of the following route handler files should retrieve the database using `get(Database)` instead of destructuring `db` from the context, and each needs to import `Database` from `remix/data-table`:
  - `app/account.tsx`
  - `app/admin.books.tsx`
  - `app/admin.orders.tsx`
  - `app/admin.users.tsx`
  - `app/books.tsx`
  - `app/auth.tsx`
  - `app/cart.tsx`
  - `app/checkout.tsx`
  - `app/fragments.tsx`
  - `app/marketing.tsx`
- The module augmentation file `app/types/context.db.ts` should be removed since it is no longer needed.
- The demo's `README.md` should be updated to reflect the new pattern. It must describe the `context.set(Database, ...)` and `get(Database)` approach so that the documented behavior matches the implementation.

## Files to Look At

- `demos/bookstore/app/middleware/database.ts` — where the database is put on request context
- `demos/bookstore/app/middleware/auth.ts` — auth middleware that also accesses the database
- `demos/bookstore/app/types/context.db.ts` — the module augmentation that types `context.db`
- `demos/bookstore/app/utils/context.ts` — context utilities
- `demos/bookstore/app/` — route handlers that read the database from context
- `demos/bookstore/README.md` — describes the demo's patterns including database middleware
