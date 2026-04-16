# Task: Make Tracing.group() return a Disposable

## Problem

The `Tracing.group()` method in Playwright currently returns `Promise<void>`. This prevents using the `await using` pattern for automatic cleanup:

```typescript
await using group = await context.tracing.group('name');
```

Currently this pattern doesn't work because `group()` doesn't return a disposable object. The group should automatically end when the scope exits by calling `groupEnd()` on disposal.

## What You Need To Do

### 1. Fix the Core Implementation

The `group()` method in the Tracing client implementation (located in the playwright-core package) returns `Promise<void>`. It needs to instead return a `DisposableStub` object that calls the existing `groupEnd()` method when disposed.

You must:
- Import `DisposableStub` from `'./disposable'` in the tracing module
- Return `new DisposableStub(() => this.groupEnd())` from the `group()` method

### 2. Update Type Definitions

The type definition files for the Tracing interface need to reflect the new return type. Update both type definition files (one in the playwright-client package and one in the playwright-core package):

The `group()` method signature should return `Promise<Disposable>` instead of `Promise<void>`.

### 3. Update API Documentation

In the Tracing class API documentation file (in the docs/src/api directory), add the return type annotation for the `group` method:

Add the line: `returns: <[Disposable]>`

Follow the format pattern used by other methods in the same file for documenting return types.

### 4. Update CLAUDE.md

The project's `CLAUDE.md` has a "Commit Convention" section. Add a line instructing contributors to run `npm run flint` and fix errors before committing.

## Verification

The solution should:

1. Allow the `await using` pattern shown above
2. Automatically call `groupEnd()` when the disposable is disposed
3. Pass TypeScript compilation
4. Pass lint checks
