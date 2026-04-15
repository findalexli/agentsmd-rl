# Align account module with Effect patterns

## Overview

The account module at `packages/opencode/src/account/` does not follow the Effect patterns established in this codebase. The tests will verify that the module meets these requirements by checking for specific string patterns in the source files.

## Requirements

### Schema definitions (`src/account/schema.ts`)

The file MUST contain:
- `export const RefreshToken` with `Schema.brand("RefreshToken")` for the token type
- `export const DeviceCode` with `Schema.brand("DeviceCode")` for the device code type
- `export const UserCode` with `Schema.brand("UserCode")` for the user code type
- `Schema.Duration` for time-related fields (e.g., in the `Login` type)
- `Schema.Class` for data types with multiple fields (e.g., `Login` class with `expiry` and `interval` fields)

### Repository layer (`src/account/repo.ts`)

The file MUST contain:
- `Layer.effect(` for constructing the AccountRepo layer
- `Effect.gen(function* ()` for Effect composition
- `AccountRepo.of({` for returning the implementation object
- Type signatures using the branded token types (`RefreshToken`, `DeviceCode`, `UserCode`)

### Service layer (`src/account/service.ts`)

The file MUST contain:
- `export namespace AccountService` with `export interface Service` inside it
- `Layer.effect(` for constructing the service layer
- `Effect.gen(function* ()` for Effect composition
- `HttpClient.filterStatusOk` for HTTP response filtering
- `Effect.fnUntraced` for internal helper functions
- `Effect.fn(` for named public methods
- Return type annotations `readonly Org[]` for `orgs` method
- Return type annotations `readonly AccountOrgs[]` for `orgsByAccount` method

### SQL definitions (`src/account/account.sql.ts`)

The file MUST contain:
- `.$type<` applied to Drizzle column definitions to enforce branded type safety (e.g., `.$type<RefreshToken>()`)

### CLI commands (`src/cli/cmd/account.ts`)

The file MUST contain:
- `Duration.Duration` types for polling interval values (instead of raw numbers)
- `Duration.sum` for combining duration values in polling logic

### Documentation (`AGENTS.md`)

The file MUST contain a new section with:
- Header: `# opencode Effect guide`
- Subsection: `## Schemas` documenting `Schema.Class` for data types and `Schema.brand` for single-value types
- Subsection: `## Services` documenting `Layer.effect` and `ServiceName.of` patterns
- Subsection: `## Effects` documenting `Effect.gen` and `Effect.fn` patterns
- Subsection documenting error handling with `yield* new MyError` preferred over `yield* Effect.fail`

## Files to Modify

- `packages/opencode/src/account/schema.ts`
- `packages/opencode/src/account/repo.ts`
- `packages/opencode/src/account/service.ts`
- `packages/opencode/src/account/account.sql.ts`
- `packages/opencode/src/cli/cmd/account.ts`
- `packages/opencode/AGENTS.md`

## Verification

Run `bun test test/account/repo.test.ts test/account/service.test.ts` to verify the implementation passes all tests.
