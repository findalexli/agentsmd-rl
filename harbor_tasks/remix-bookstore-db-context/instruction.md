# Refactor bookstore database context access pattern

## Problem

The bookstore demo stores the database handle on request context using a custom `db` property (e.g., `context.db = db` or destructuring `db` from the context parameter in handlers/middleware). This approach is inconsistent with how other context values like `Session` and `FormData` are accessed — those use a standard `get()` API.

Additionally, a TypeScript module augmentation file (`app/types/context.db.ts`) extends `RequestContext` with this custom `db` property, which is an escape hatch that doesn't match the rest of the codebase.

## Expected Behavior

All database access should follow the same request context pattern used by `Session`, `FormData`, and other context values in this codebase. Route handlers and middleware should access the database through this standard API, not through a custom property assignment.

The `remix/data-table` package exports symbols that enable this pattern. The TypeScript augmentation adding a custom `db` property to `RequestContext` should be removed.

The bookstore demo's README should accurately document the database context pattern used in the codebase.

## Files to Inspect

- `demos/bookstore/app/middleware/database.ts` — database middleware
- `demos/bookstore/app/middleware/auth.ts` — auth middleware that accesses the database
- `demos/bookstore/app/types/context.db.ts` — TypeScript module augmentation (check if this pattern is used)
- `demos/bookstore/app/books.tsx` — route handler using the database
- `demos/bookstore/app/cart.tsx` — another handler using the database
- `demos/bookstore/app/admin.books.tsx` — CRUD handler using the database
- `demos/bookstore/README.md` — demo documentation
- `demos/bookstore/app/utils/context.ts` — context utilities (reference for the standard pattern used by other values like Session)