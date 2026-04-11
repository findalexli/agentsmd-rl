# Refactor account module to use proper Effect patterns

## Problem

The account module in `packages/opencode/src/account/` uses loose typing throughout — raw strings for tokens and IDs, `Schema.Struct` for API response types, and plain numbers for time-based fields. The service and repo layers use older Effect patterns (`Layer.succeed`, inline service shapes, `ServiceMap.Service.Shape`) instead of the modern Effect conventions.

This makes the code harder to maintain and less type-safe. Domain identifiers like account IDs, access tokens, and device codes are all typed as `string`, losing the benefit of Effect's branded types.

## Expected Behavior

Refactor the account module to use proper Effect patterns:

1. **Branded types**: Create branded schemas for domain identifiers (`RefreshToken`, `DeviceCode`, `UserCode`) alongside the existing `AccessToken` and `AccountID` — using `Schema.brand` with `withStatics` for a `make` constructor
2. **Schema.Class**: Replace `Schema.Struct` usage in `service.ts` with `Schema.Class` for structured data types (token refresh, device auth, user, etc.)
3. **Duration fields**: Replace raw `Schema.Number` time fields in the `Login` schema with `Schema.Duration`
4. **Layer.effect pattern**: Convert `AccountRepo` from `Layer.succeed` to `Layer.effect` with `Effect.gen` and `AccountRepo.of({...})` — also add an `AccountRepo.Service` namespace
5. **Extract helpers**: Factor out shared HTTP helpers like `fetchOrgs` and `fetchUser` in the service layer

After updating the code, add an Effect guide section to `packages/opencode/AGENTS.md` that documents the patterns used in this refactor so future contributors follow the same conventions. The guide should cover schemas, services, errors, effects, and time patterns.

## Files to Look At

- `packages/opencode/src/account/schema.ts` — Schema definitions: branded types, Login class, error types
- `packages/opencode/src/account/service.ts` — Service layer: HTTP handling, token refresh, device auth flow
- `packages/opencode/src/account/repo.ts` — Repository layer: database operations, service registration
- `packages/opencode/src/account/account.sql.ts` — Drizzle table definitions with typed columns
- `packages/opencode/src/account/index.ts` — Public API surface
- `packages/opencode/AGENTS.md` — Add Effect guide documenting the patterns used here
