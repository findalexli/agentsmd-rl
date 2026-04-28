# SQL injection vulnerability in database queue operations

## Problem

The database queue message operations in Supabase Studio construct SQL queries by directly interpolating user-controlled values into template literal strings without any sanitization. This means parameters containing special SQL characters (such as single quotes) will break query syntax and could enable SQL injection attacks.

For example, sending a message with a payload like `{"key": "it's a value"}` will produce malformed SQL because the embedded single quote terminates the string literal prematurely. A malicious user could exploit this with a payload like `'; DROP TABLE users; --`.

The vulnerable operations live in the `apps/studio/data/database-queues/` area of the codebase. They handle send, query (infinite/paginated), archive, and delete mutations. Each constructs SQL using `executeSql` with raw `${...}` template interpolation for user-provided values.

## Available Escaping Function

The codebase provides a `literal()` function in the `@supabase/pg-meta/src/pg-format` module that performs type-appropriate SQL literal escaping:

- **Strings**: wraps in single quotes with embedded single quotes doubled — e.g., `"it's a value"` becomes `'it''s a value'`
- **Objects**: serializes to JSON with a `::jsonb` cast suffix
- **`null`**: returns the SQL keyword `NULL` (unquoted)
- **Numbers**: returns the plain numeric string without quotes — e.g., `42` becomes `42`

## Code Style Requirements

- The project uses ESLint with Prettier. All modified files must pass `pnpm run lint` in `apps/studio`.
- Modified TypeScript files must not contain `as any` type casts.
- The solution must pass TypeScript type checking (`pnpm run typecheck` in `apps/studio`).
