# Remove router.run() from fetch-router

## Problem

The `@remix-run/fetch-router` package has a `router.run()` method that was added but never released. This API lets code execute inside the router's middleware/request context without dispatching to a route. However, tests should exercise the router through its public HTTP interface (`router.fetch`) instead of callback execution internals. The method should be removed entirely.

## Expected Behavior

The `run()` method should not exist on the `Router` interface or its implementation. All related tests, the unreleased change file, and documentation referencing this API should be cleaned up.

## Files to Look At

- `packages/fetch-router/src/lib/router.ts` — Router interface and `createRouter()` implementation containing the `run` method
- `packages/fetch-router/src/lib/router.test.ts` — Test file with the `router.run()` test suite
- `packages/fetch-router/README.md` — Package documentation that describes the `run` API
- `packages/fetch-router/.changes/minor.router-run.md` — Unreleased change file for this API
- `demos/bookstore/README.md` — Demo README that references `router.run()`

## Notes

After removing the code, update all documentation files that reference `router.run()`. The project's README files should not mention the removed API.
