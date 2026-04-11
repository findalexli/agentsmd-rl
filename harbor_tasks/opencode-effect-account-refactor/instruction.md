# Refactor account module to use Effect patterns

## Problem

The account module in `packages/opencode/src/account/` needs to be refactored to align with the project's Effect-based architecture. Currently, the code uses inconsistent patterns:

1. **Schema definitions** use loose string types for tokens and codes instead of branded types
2. **Time fields** in schemas use raw `Schema.Number` instead of `Schema.Duration`
3. **Service implementations** use `Layer.succeed` with plain objects instead of the standard `Layer.effect` with `Effect.gen`
4. **HTTP handling** lacks proper status filtering and structured error handling

Additionally, there's no documentation for developers on how to write Effect code in this codebase.

## Expected Behavior

After the refactor, the account module should follow these patterns:

### Schema changes (`src/account/schema.ts`)
- Add branded types for `RefreshToken`, `DeviceCode`, and `UserCode` using `Schema.String.pipe(Schema.brand("Name"))`
- Change `Login` class to use `Schema.Duration` for `expiry` and `interval` fields (instead of `Schema.Number`)
- Use `Schema.Class` for data types with multiple fields

### Repo changes (`src/account/repo.ts`)
- Convert from `Layer.succeed(AccountRepo.of({...}))` to `Layer.effect(AccountRepo, Effect.gen(function* () {...}))`
- Move helper functions inside the `Effect.gen` scope
- Use `AccountRepo.of({...})` to return the service implementation
- Update type signatures to use branded types for tokens

### Service changes (`src/account/service.ts`)
- Add namespace `AccountService` with `Service` interface
- Convert from `Layer.succeed` to `Layer.effect` with `Effect.gen`
- Use structured schema classes for HTTP request/response bodies
- Use `HttpClient.filterStatusOk` for proper HTTP status handling
- Use `Effect.fnUntraced` for internal helpers and `Effect.fn("Name")` for public methods
- Update `orgs` and `orgsByAccount` return types to `readonly Org[]` and `readonly AccountOrgs[]`

### SQL schema changes (`src/account/account.sql.ts`)
- Add type imports from `./schema`
- Use `.$type<BrandedType>()` on Drizzle columns for branded type safety

### CLI changes (`src/cli/cmd/account.ts`)
- Update polling logic to use `Duration.Duration` instead of raw numbers
- Use `Duration.sum()` for adding durations

### Documentation (`AGENTS.md`)
- Add a new "opencode Effect guide" section documenting the Effect patterns used in this codebase
- Include sections on: Schemas, Services, Errors, Effects, and Time
- Document the specific patterns: `Schema.Class`, `Schema.brand`, `Layer.effect`, `Effect.gen`, `Effect.fn`, `Effect.fnUntraced`, and error handling conventions

## Files to Look At

- `packages/opencode/src/account/schema.ts` — Schema definitions, branded types, data classes
- `packages/opencode/src/account/repo.ts` — Account repository service layer
- `packages/opencode/src/account/service.ts` — Account service with HTTP operations
- `packages/opencode/src/account/account.sql.ts` — Drizzle SQL table definitions
- `packages/opencode/src/account/index.ts` — Public exports and convenience functions
- `packages/opencode/src/cli/cmd/account.ts` — CLI account commands
- `packages/opencode/AGENTS.md` — Agent instructions (needs new Effect guide section)

## Notes

- The test files `test/account/repo.test.ts` and `test/account/service.test.ts` show how the APIs should be used after the refactor
- Run `bun tsc --noEmit` to check for TypeScript errors
- Run `bun test test/account/repo.test.ts test/account/service.test.ts` to verify the refactor
