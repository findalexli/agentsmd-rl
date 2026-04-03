# Handle PostgreSQL 22P02 error in driver adapters

## Problem

When using PostgreSQL with the `pg`, `neon`, or `ppg` driver adapters, database errors with SQL error code `22P02` ("invalid_text_representation" / "invalid input value") are not handled. This can happen when, for example, an enum value that exists in the Prisma schema does not match what's in the database. Instead of returning a proper user-facing Prisma error, the error propagates as an unhandled internal error.

## Expected Behavior

The `22P02` PostgreSQL error should be mapped to a proper user-facing Prisma error through the driver adapter error handling pipeline, similar to how other PostgreSQL errors (like `22003` for value out of range or `23505` for unique constraint violations) are already handled.

The fix needs to touch all three PostgreSQL driver adapters (`pg`, `neon`, `ppg`) as well as the shared error type definitions and runtime error mapping.

## Files to Look At

- `packages/driver-adapter-utils/src/types.ts` — defines the `MappedError` type used by all driver adapters
- `packages/adapter-pg/src/errors.ts` — error mapping for the `pg` adapter
- `packages/adapter-neon/src/errors.ts` — error mapping for the `neon` adapter
- `packages/adapter-ppg/src/errors.ts` — error mapping for the `ppg` adapter
- `packages/client-engine-runtime/src/user-facing-error.ts` — maps `MappedError` kinds to Prisma error codes and renders error messages

After fixing the code, update `AGENTS.md` to document the driver adapter error handling flow so future contributors know how to add new error mappings. Also add documentation about the client functional test structure since that knowledge is currently undocumented.
