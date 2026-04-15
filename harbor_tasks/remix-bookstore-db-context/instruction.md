# Refactor bookstore database context access pattern

## Problem

The bookstore demo currently stores the database handle on request context via a non-standard approach. Route handlers and middleware access the database by destructuring `db` directly from the context object (e.g., `async function({ db, get })`). This is inconsistent with how other context values like `Session` and `FormData` are accessed — those use the standard `get()` API from `remix/fetch-router`.

There is also a dedicated TypeScript module augmentation file (`app/types/context.db.ts`) that extends `RequestContext` with a custom `db` property, creating an extra escape hatch that doesn't match the rest of the codebase.

The `remix/data-table` package exports a `Database` symbol that should be used as the context key for database access, consistent with the pattern used by `Session`, `FormData`, and other context values in this codebase.

## Expected Behavior

All database access should follow the standard request context pattern:

- **Middleware (`app/middleware/database.ts`)**: Must store the database handle on request context using the standard `context.set()` API with the `Database` symbol exported by `remix/data-table`, instead of direct property assignment.

- **Handlers and middleware (`app/books.tsx`, `app/cart.tsx`, `app/admin.books.tsx`, `app/middleware/auth.ts`, and others)**: Must read the database back using `get(Database)` instead of destructuring `db` from the context parameter.

- **TypeScript types**: The module augmentation file (`app/types/context.db.ts`) that adds `db` to `RequestContext` must be removed.

- **Documentation**: The bookstore demo's README currently references the old `context.db` pattern in its description of the database middleware. Update the README to accurately describe the new database context pattern using the `Database` symbol and the standard `context.set()` / `get()` API.

## Files to Look At

- `demos/bookstore/app/middleware/database.ts` — stores the database on request context
- `demos/bookstore/app/middleware/auth.ts` — reads the database from context
- `demos/bookstore/app/types/context.db.ts` — module augmentation for context.db (to be removed)
- `demos/bookstore/app/books.tsx` — example route handler that uses the database
- `demos/bookstore/app/cart.tsx` — another handler using the database
- `demos/bookstore/app/admin.books.tsx` — CRUD handler using the database
- `demos/bookstore/README.md` — demo documentation describing the context pattern
- `demos/bookstore/app/utils/context.ts` — context utilities (uses same key pattern)
