# Fix Retained Promise References Causing Memory Leaks

During navigation cycles in the router core, promise references are captured but not released after resolution, causing them to be retained in memory longer than necessary.

## The Problem

When the router handles navigation, promise variables are assigned references to existing promises. After these promises resolve, the variables continue to hold references, preventing garbage collection:

1. **Previous load promise references**: When capturing `match._nonReactive.loadPromise` before assigning a new controlled promise, the captured reference is never cleared after the controlled promise resolves.

2. **Match load promise references**: The `match._nonReactive.loadPromise` property is assigned a new promise but is never cleared after resolution, causing the promise object to be retained.

3. **Commit promise references**: When capturing `this.commitLocationPromise` before assigning a new controlled promise, the captured reference is never cleared after the controlled promise resolves.

## Required Fix

To properly release these references and allow garbage collection:

1. **Local promise capture variables must be reassignable**: Any local variable that captures a promise reference (to call `.resolve()` on it) must be declared with `let` so it can be reassigned to `undefined` after the resolve callback fires.

2. **Promise references must be cleared after resolution**: After calling `.resolve()` on a captured promise reference, the variable must be reassigned to `undefined` to release the reference.

3. **The `match._nonReactive.loadPromise` property must be cleared in multiple locations**: The property must be set to `undefined` after resolution in both error-handler paths and normal-completion paths.

The pattern for controlled promises is:
```typescript
let capturedPromise = existingPromise  // must be reassignable
controlledPromise = createControlledPromise(() => {
  capturedPromise?.resolve()
  capturedPromise = undefined  // clear after resolve
})
```

And for match properties:
```typescript
match._nonReactive.loadPromise?.resolve()
match._nonReactive.loadPromise = undefined  // clear the property
```

## Affected Files

- `packages/router-core/src/load-matches.ts` — `executeBeforeLoad` function and `loadRouteMatch` function
- `packages/router-core/src/router.ts` — `commitLocation` method

## Verification

After implementing the fix:
1. Build the package: `pnpm nx run @tanstack/router-core:build`
2. Run type checks: `pnpm nx run @tanstack/router-core:test:types`
3. Run unit tests: `pnpm nx run @tanstack/router-core:test:unit`

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `eslint (JS/TS linter)`
