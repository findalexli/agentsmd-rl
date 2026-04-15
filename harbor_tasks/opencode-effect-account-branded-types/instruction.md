# Refactor account module to use proper Effect patterns

## Problem

The account module in `packages/opencode/src/account/` has several type-safety and architectural issues:

1. **Missing branded types**: While `AccessToken` and `AccountID` already use branded types, other domain identifiers — `RefreshToken`, `DeviceCode`, and `UserCode` — are typed as raw `string`. The module needs branded types for these, defined via `Schema.brand` with `withStatics` to provide a `make` constructor.

2. **Unstructured API types**: Complex API response types (token refresh, device auth, user info, etc.) throughout the module are built with `Schema.Struct`, which doesn't provide class-based instances or methods. The module should use `Schema.Class` for these structured data types — enough to cover all the API response shapes (at least 5 class definitions). After refactoring, no `Schema.Struct` usage should remain in the service layer.

3. **Untyped time fields**: The `Login` schema uses `Schema.Number` for time-based fields like expiration and polling intervals. These should be `Schema.Duration` fields for proper temporal type safety.

4. **Simplistic service registration**: The `AccountRepo` is registered via `Layer.succeed`, which bypasses Effect's dependency injection. The expected pattern uses `Layer.effect` with `Effect.gen`, constructs the service via `AccountRepo.of({...})`, and exports `namespace AccountRepo` with a `Service` type for proper Effect service definitions.

5. **Duplicated HTTP logic**: The service layer has repeated HTTP fetch patterns. Shared logic for fetching org and user data should be extracted into `fetchOrgs` and `fetchUser` helpers.

## Documentation

The `packages/opencode/AGENTS.md` file should include an "Effect guide" section documenting the patterns used in this codebase. The guide must cover:
- **Schema patterns**: including `Schema.brand` for branded single-value types (the guide should use the term "branded" in this context)
- **Service patterns**
- **Error patterns**

## Files

The relevant source files are in `packages/opencode/src/account/`:
- `schema.ts` — schema definitions
- `service.ts` — service layer, HTTP handling
- `repo.ts` — repository layer, database operations
- `account.sql.ts` — Drizzle table definitions
- `index.ts` — public API surface

Also update `packages/opencode/AGENTS.md` with the Effect guide.

## Verification

All existing unit tests and TypeScript type-checking must pass after the refactoring.
