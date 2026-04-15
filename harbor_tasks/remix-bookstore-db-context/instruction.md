# Refactor bookstore database context access pattern

## Problem

The bookstore demo currently uses a module augmentation pattern to attach the database to `RequestContext`. Route handlers and middleware access the database by destructuring `db` from the context object (e.g., `{ db, get }`). This is inconsistent with how other context values like `Session` and `FormData` are accessed — those use the standard `get()` API.

There is also a dedicated TypeScript module augmentation file (`app/types/context.db.ts`) that extends `RequestContext` with a custom `db` property, creating an extra escape hatch that doesn't match the rest of the demo.

## Expected Behavior

The `remix/data-table` package exports a `Database` symbol that serves as the context key for database access. All database access should follow the standard request context pattern used by other context values:

- **Middleware (database.ts)**: Import `Database` from `remix/data-table` and store the database handle using `context.set(Database, db)` instead of `context.db = db`.
- **Handlers and middleware**: Import `Database` from `remix/data-table` and read the database back with `get(Database)` instead of destructuring `db` from the context parameter.

The module augmentation file should be removed.

After making the code changes, update the bookstore demo's README to accurately describe the new database context pattern. The existing README references the old `context.db` pattern in its description of the database middleware — those references should be updated to reflect the new approach.

## Files to Look At

- `demos/bookstore/app/middleware/database.ts` — stores the database on request context
- `demos/bookstore/app/middleware/auth.ts` — reads the database from context
- `demos/bookstore/app/types/context.db.ts` — module augmentation for context.db
- `demos/bookstore/app/books.tsx` — example route handler that uses the database
- `demos/bookstore/app/cart.tsx` — another handler using the database
- `demos/bookstore/app/admin.books.tsx` — CRUD handler using the database
- `demos/bookstore/README.md` — demo documentation describing the context pattern
- `demos/bookstore/app/utils/context.ts` — context utilities (uses same key pattern)
