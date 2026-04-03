# Remove `router.run()` from fetch-router

## Problem

The `@remix-run/fetch-router` package exposes a `router.run()` method that lets callers execute a callback inside the router's middleware/request context without dispatching to a route. This API was added but never released — it encourages testing through internal callback execution rather than the router's public HTTP interface (`router.fetch`).

The `router.run()` method should be completely removed: its type signatures from the `Router` interface, its implementation inside `createRouter()`, and all associated tests.

## Expected Behavior

- The `Router` interface in `packages/fetch-router/src/lib/router.ts` should no longer declare `run()` method overloads.
- The `createRouter()` implementation should no longer include the `run()` method body.
- All `router.run()` tests in `packages/fetch-router/src/lib/router.test.ts` should be deleted. Imports that were only used by those tests should be cleaned up.
- The unreleased change file at `packages/fetch-router/.changes/minor.router-run.md` should be deleted since this API was never published.
- After fixing the code, update the relevant documentation to reflect the removal. The fetch-router README documents `router.run()` with a full section and code examples. The bookstore demo README also references it. These docs should be updated to remove mentions of the removed API.

## Files to Look At

- `packages/fetch-router/src/lib/router.ts` — Router interface and createRouter implementation
- `packages/fetch-router/src/lib/router.test.ts` — Tests including the router.run() describe block
- `packages/fetch-router/README.md` — Documents the router.run() API
- `demos/bookstore/README.md` — References router.run() in code highlights
- `packages/fetch-router/.changes/minor.router-run.md` — Unreleased change file for this API
