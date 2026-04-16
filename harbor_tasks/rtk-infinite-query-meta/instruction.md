# Fix Meta Handling for Infinite Queries

## Problem

When using `build.infiniteQuery` with `onQueryStarted`, the `meta` property from `queryFulfilled` comes back as `undefined` instead of containing the expected `request` and `response` objects.

This breaks code that relies on accessing response metadata (like headers, status) inside `onQueryStarted` callbacks for infinite queries.

## Affected File

The issue is in `packages/toolkit/src/query/core/buildThunks.ts`. The infinite query result construction after fetching a page does not include the `meta` field that is present in `pageResponse`.

## Expected Behavior

When an infinite query fetches a page, the `queryFulfilled` promise in `onQueryStarted` should resolve with a `meta` object containing:
- `request`: The request object
- `response`: The response object

Currently, `meta` is `undefined` in the returned result object, even though the page response contains this metadata.

## Test File Updates

The test file `packages/toolkit/src/query/tests/infiniteQueries.test.ts` has an existing test with an expectation of `meta: undefined`. This expectation must be updated to expect `meta` to be defined with `request` and `response` properties (using `expect.anything()` for each).

## Verification

After fixing, the following must be true:
1. `packages/toolkit/src/query/core/buildThunks.ts` contains the appropriate `meta` handling for infinite queries
2. `packages/toolkit/src/query/tests/infiniteQueries.test.ts` no longer contains `meta: undefined` and instead expects `meta` with `request: expect.anything()` and `response: expect.anything()`
3. `yarn vitest run src/query/tests/infiniteQueries.test.ts` passes
4. `yarn build` completes successfully
5. TypeScript compilation succeeds with `npx tsc --noEmit -p tsconfig.json`
