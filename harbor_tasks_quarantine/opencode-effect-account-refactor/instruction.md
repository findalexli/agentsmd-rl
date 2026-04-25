# Align account module with Effect patterns

## Problem

The account module at `packages/opencode/src/account/` currently uses legacy patterns that are inconsistent with the Effect-TS architectural standards used throughout this codebase. This misalignment causes maintainability issues and fails to leverage type-safe abstractions for security-sensitive authentication data.

## Current Symptoms

### Schema definitions (`src/account/schema.ts`)

The current implementation lacks proper type branding for security tokens and uses incorrect patterns for time-based fields. The following specific patterns should be present after refactoring:
- Branded types: `RefreshToken`, `DeviceCode`, and `UserCode` with corresponding brand literals `"RefreshToken"`, `"DeviceCode"`, and `"UserCode"`
- Duration types using `Schema.Duration` for time-related fields
- Data classes using `Schema.Class` pattern

### Repository layer (`src/account/repo.ts`)

The repository is not constructed using the standard service layer patterns. After the fix, it should use:
- Layer construction via `Layer.effect(` pattern
- Effect composition via `Effect.gen(function* ()` pattern
- Implementation return via `AccountRepo.of({` pattern
- Type signatures referencing the branded types (`RefreshToken`, `DeviceCode`, `UserCode`)

### Service layer (`src/account/service.ts`)

The service layer is missing namespace organization and proper Effect patterns. After the fix, it should contain:
- A namespace export pattern with `export namespace AccountService` containing `export interface Service`
- Layer construction using `Layer.effect(`
- Effect composition using `Effect.gen(function* ()`
- HTTP filtering using `HttpClient.filterStatusOk`
- Helper function patterns: `Effect.fnUntraced` for internals
- Public method patterns: `Effect.fn(`
- Return type annotations: `readonly Org[]` and `readonly AccountOrgs[]`

### SQL definitions (`src/account/account.sql.ts`)

Database columns for token fields lack branded type enforcement. After the fix, Drizzle column definitions should use `.$type<` annotations with the branded types (e.g., `.$type<RefreshToken>()`).

### CLI commands (`src/cli/cmd/account.ts`)

The polling logic uses raw numeric values instead of type-safe Duration types. After the fix, it should use:
- `Duration.Duration` type annotations for interval values
- `Duration.sum` for combining duration values

### Documentation (`AGENTS.md`)

The codebase lacks a reference guide for the Effect patterns being introduced. After the fix, the documentation should contain a new section with:
- Header: `# opencode Effect guide`
- Subsection: `## Schemas`
- Subsection: `## Services`
- Subsection: `## Effects`
- Error handling guidance mentioning both `yield* new MyError` and `Effect.fail`

## Files to Modify

- `packages/opencode/src/account/schema.ts`
- `packages/opencode/src/account/repo.ts`
- `packages/opencode/src/account/service.ts`
- `packages/opencode/src/account/account.sql.ts`
- `packages/opencode/src/cli/cmd/account.ts`
- `packages/opencode/AGENTS.md`

## Verification

Run `bun test test/account/repo.test.ts test/account/service.test.ts` to verify the implementation passes all tests.
