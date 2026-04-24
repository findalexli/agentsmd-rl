# Memory Leak: Retained Promise References

## Problem

The TanStack Router has a memory management issue where promise references are retained during route loading and navigation commits. This causes potential memory accumulation during navigation cycles.

## Symptoms

When users navigate through multiple routes in an application:
- Promise chains can accumulate without being properly cleaned up
- References to resolved promises are kept longer than necessary
- This can lead to increased memory usage over extended navigation sessions

## Investigation Areas

The memory leak involves these specific promise references in the following files:

### 1. `packages/router-core/src/load-matches.ts`

Three specific cleanup locations need to be addressed:

**Location A - `executeBeforeLoad` function:**
- The variable `prevLoadPromise` is captured from `match._nonReactive.loadPromise`
- This variable must be declared with `let` (not `const`) to allow reassignment
- After the promise resolves, `prevLoadPromise` must be set to `undefined` to release the reference
- The pattern should be: `let prevLoadPromise = match._nonReactive.loadPromise` followed later by `prevLoadPromise = undefined` inside the callback

**Location B - `loadRouteMatch` function try block:**
- When cleaning up `match._nonReactive.loaderPromise` (setting it to `undefined`), the same should be done for `match._nonReactive.loadPromise`
- Both `loaderPromise` and `loadPromise` should be set to `undefined` in the same cleanup block
- Expected pattern: `match._nonReactive.loaderPromise = undefined` and `match._nonReactive.loadPromise = undefined` should appear together

**Location C - `loadRouteMatch` synchronous loader path:**
- When `loaderIsRunningAsync` is false, after resolving `match._nonReactive.loadPromise`, the reference should be released
- The pattern should include: `if (!loaderIsRunningAsync)` block containing `match._nonReactive.loadPromise = undefined`

### 2. `packages/router-core/src/router.ts`

**Location D - commit location handling:**
- The variable `previousCommitPromise` is captured from `this.commitLocationPromise`
- This variable must be declared with `let` (not `const`) to allow reassignment
- After the promise resolves, `previousCommitPromise` must be set to `undefined` to release the reference
- The pattern should be: `let previousCommitPromise = this.commitLocationPromise` followed by `previousCommitPromise = undefined` inside the callback

## Requirements

- Fix the memory leak by ensuring these promise references are properly cleaned up after resolution:
  - `prevLoadPromise` should be declared with `let` and set to `undefined` after it resolves in `executeBeforeLoad`
  - `match._nonReactive.loadPromise` should be set to `undefined` alongside `match._nonReactive.loaderPromise` in the try block of `loadRouteMatch`
  - `match._nonReactive.loadPromise` should be set to `undefined` when the synchronous loader path is taken (`!loaderIsRunningAsync`)
  - `previousCommitPromise` should be declared with `let` and set to `undefined` after it resolves during commit location handling
- Maintain existing functionality - routes should still load correctly
- Ensure the fix passes TypeScript type checking and linting

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `eslint (JS/TS linter)`
