# Refactor bookstore database context access pattern

## Problem

The bookstore demo stores the database handle on request context using a custom `db` property (e.g., `context.db = db` or destructuring `db` from the context parameter in handlers/middleware). This approach is inconsistent with how other context values like `Session` and `FormData` are accessed — those use a standard `get()` API.

Additionally, a TypeScript module augmentation file (`app/types/context.db.ts`) extends `RequestContext` with this custom `db` property, which is an escape hatch that doesn't match the rest of the codebase.

## Expected Behavior

All database access should follow the same request context pattern used by `Session`, `FormData`, and other context values in this codebase. Specifically, the `Database` symbol from `remix/data-table` should be used as the context key. Handlers and middleware should retrieve the database handle using `get(Database)`, and the database middleware should store it using `context.set(Database, db)`. No handler or middleware should destructure a `db` property from the context parameter.

The TypeScript module augmentation adding a custom `db` property to `RequestContext` (`app/types/context.db.ts`) should be removed, since the `Database` context key makes it unnecessary.

The bookstore demo's README should accurately document the `context.set(Database, db)` / `get(Database)` context pattern and should no longer reference the old `context.db` pattern for attaching the database handle to the request context.

## Code Style Requirements

This project enforces code style with ESLint (`pnpm lint`) and Prettier (`pnpm format:check`). All changes must pass both checks.

## Files to Inspect

- `demos/bookstore/app/middleware/database.ts` — database middleware
- `demos/bookstore/app/middleware/auth.ts` — auth middleware that accesses the database
- `demos/bookstore/app/types/context.db.ts` — TypeScript module augmentation (check if this pattern is used)
- `demos/bookstore/app/books.tsx` — route handler using the database
- `demos/bookstore/app/cart.tsx` — another handler using the database
- `demos/bookstore/app/admin.books.tsx` — CRUD handler using the database
- `demos/bookstore/README.md` — demo documentation
- `demos/bookstore/app/utils/context.ts` — context utilities (reference for the standard pattern used by other values like Session)