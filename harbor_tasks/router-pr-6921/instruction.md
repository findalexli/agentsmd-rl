# Stale Loader Reload Behavior

## Problem

When route loader data becomes stale in TanStack Router, the router always reloads in the background without blocking navigation. This provides a smooth "stale-while-revalidate" experience, but some applications need different behavior.

For example, an application might want navigation to wait for stale data to refresh before completing, especially when:
- The stale data might be significantly out of date
- Users expect to see fresh data immediately after navigation
- The application has specific consistency requirements

Currently there is no way to configure this behavior - stale reloads always happen in the background.

## Task

Add a configurable `staleReloadMode` option that allows controlling how stale loader data is revalidated:

1. **`'background'`** (default): Preserves current behavior - stale data is shown immediately while reloading happens asynchronously
2. **`'blocking'`**: Navigation waits for stale loader reloads to complete before resolving

The configuration should be available at two levels:
- **Route-level**: Each route's loader can specify its own `staleReloadMode`
- **Router-level**: A `defaultStaleReloadMode` option sets the fallback for routes that don't specify

## Requirements

- Add the necessary type definitions for the new configuration options
- Support an object-form loader syntax that allows specifying both the handler and staleReloadMode
- Update the loader execution logic in `load-matches.ts` to respect the staleReloadMode setting
- Ensure all existing tests continue to pass (the default behavior should be unchanged)
- Export any new public types from the package

## Files to Modify

- `packages/router-core/src/route.ts` - Add type definitions
- `packages/router-core/src/router.ts` - Add router-level option
- `packages/router-core/src/load-matches.ts` - Implement the conditional blocking logic
- `packages/router-core/src/index.ts` - Export new types

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `eslint (JS/TS linter)`
