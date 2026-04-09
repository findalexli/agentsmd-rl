# Make Tracing.group() return a Disposable

## Problem

`Tracing.group()` currently returns `Promise<void>`, which means there's no way to use the `await using` pattern for automatic group cleanup. Users must manually call `groupEnd()`, which is error-prone — if an exception occurs between `group()` and `groupEnd()`, the group is never closed.

The `DisposableStub` class already exists in the codebase at `packages/playwright-core/src/client/disposable.ts` and is used elsewhere to enable the disposable pattern.

## Expected Behavior

`Tracing.group()` should return a `Disposable` so callers can use:
```typescript
await using _group = await context.tracing.group("my group");
// ... actions ...
// groupEnd() is called automatically when _group goes out of scope
```

The return type must be updated in the implementation, the TypeScript type definitions, and the API documentation.

## Files to Look At

- `packages/playwright-core/src/client/tracing.ts` — the `group()` method implementation
- `packages/playwright-core/src/client/disposable.ts` — `DisposableStub` class (already exists)
- `packages/playwright-core/types/types.d.ts` — public type definitions for playwright-core
- `packages/playwright-client/types/types.d.ts` — public type definitions for playwright-client
- `docs/src/api/class-tracing.md` — API documentation for the Tracing class

After making the code changes, update the project's agent instructions to reinforce the lint workflow in the commit convention section.
