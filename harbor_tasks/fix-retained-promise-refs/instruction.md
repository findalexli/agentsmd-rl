# Fix Retained Promise References Causing Memory Leaks

During navigation cycles in the router core, promise references are captured but not released after resolution, causing them to be retained in memory longer than necessary.

## The Problem

When the router handles navigation, several promise variables are assigned references to existing promises. After these promises resolve, the variables continue to hold references, preventing garbage collection:

1. **Previous load promise references**: A variable named `prevLoadPromise` captures `match._nonReactive.loadPromise` and calls `.resolve()` on it, but the variable is never cleared, retaining the reference.

2. **Match load promise references**: The `match._nonReactive.loadPromise` property is assigned a new promise but is never cleared after resolution in error handlers or normal completion paths.

3. **Commit promise references**: A variable named `previousCommitPromise` captures `this.commitLocationPromise` and calls `.resolve()` on it, but the variable is never cleared, retaining the reference.

## Required Fix Pattern

To properly release these references and allow garbage collection, implement the following specific patterns:

1. **Variable `prevLoadPromise` must be declared with `let` and cleared**: The source code must contain the pattern:
   - `let prevLoadPromise = match._nonReactive.loadPromise`
   - `prevLoadPromise = undefined` (after the resolve call)

2. **Variable `previousCommitPromise` must be declared with `let` and cleared**: The source code must contain the pattern:
   - `let previousCommitPromise = this.commitLocationPromise`
   - `previousCommitPromise = undefined` (after the resolve call)

3. **Property `match._nonReactive.loadPromise` must be cleared in at least two locations**: The source code must contain `match._nonReactive.loadPromise = undefined` appearing at least twice - once in an error handler path and once in a normal completion path.

The pattern should be:
```typescript
let somePromise = existingPromise
somePromise?.resolve()
somePromise = undefined  // Clear the reference
```

And for match properties:
```typescript
match._nonReactive.loadPromise?.resolve()
match._nonReactive.loadPromise = undefined  // Clear the property
```

## Verification

After implementing the fix:
1. Build the package: `pnpm nx run @tanstack/router-core:build`
2. Run type checks: `pnpm nx run @tanstack/router-core:test:types`
3. Run unit tests: `pnpm nx run @tanstack/router-core:test:unit`
