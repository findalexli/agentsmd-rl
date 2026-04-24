# Fix Preload Error Handling in Router Core

There is a bug in the preload logic of `@tanstack/router-core`. When a parent route's `beforeLoad` handler throws an error during `router.preloadRoute()`, child route handlers (both `beforeLoad` and `head`) are incorrectly being executed.

## The Bug

In a nested route structure like:
```
/parent
  └── /child
```

When you call `router.preloadRoute({ to: '/parent/child' })`:
1. If the parent's `beforeLoad` throws an error
2. The router should stop processing that branch
3. **Bug**: Child's `beforeLoad` and `head` handlers are still being called

## Expected Behavior

When a parent route's `beforeLoad` fails during preload:
- Parent's `beforeLoad` should run (and throw)
- Parent's `head` should run (it's already been reached)
- Child's `beforeLoad` should **NOT** run
- Child's `head` should **NOT** run

## Your Task

1. Fix the bug in the `loadMatches` function in `packages/router-core/src/load-matches.ts` so that when a parent beforeLoad throws during preload, child handlers are not executed.
2. Add a regression test to `packages/router-core/tests/load.test.ts` that verifies this behavior. The test must be named exactly: `skip child beforeLoad when parent beforeLoad throws during preload`

## Testing

Run the router-core tests:
```bash
pnpm nx run @tanstack/router-core:test:unit
```

To run a specific test:
```bash
pnpm nx run @tanstack/router-core:test:unit -- tests/load.test.ts -t "skip child beforeLoad"
```

## Files to Modify

- `packages/router-core/src/load-matches.ts` - Apply the fix
- `packages/router-core/tests/load.test.ts` - Add regression test

## Key Points

- This is a **preload** bug - normal navigation works correctly
- The `serialError` field only tracks serialization errors, not beforeLoad errors
- The route matching loop needs to account for both serial errors AND beforeLoad errors when deciding whether to continue processing child routes

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `prettier (JS/TS/JSON/Markdown formatter)`
- `eslint (JS/TS linter)`
