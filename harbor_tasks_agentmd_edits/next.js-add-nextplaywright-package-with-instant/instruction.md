# Extract instant navigation testing helper into @next/playwright package

## Problem

The Next.js codebase has an inline `instant()` testing helper defined directly inside the e2e test file at `test/e2e/app-dir/instant-navigation-testing-api/instant-navigation-testing-api.test.ts`. This function enables deterministic testing of instant navigation by controlling a cookie-based protocol that defers dynamic data during navigations.

The problem: this useful helper is buried in a single test file. Other tests (and eventually external users) can't reuse it without copy-pasting the implementation. The cookie-based protocol is simple enough that other testing frameworks could replicate it, but there's no documentation of how it works.

## Expected Behavior

The `instant()` helper should be extracted into a standalone `@next/playwright` package under `packages/next-playwright/`. The package should:

1. Export the `instant()` function that takes a Playwright page and an async callback
2. Use a structural type for the page parameter (no hard dependency on a specific Playwright version)
3. Implement the cookie-based protocol: set the `next-instant-navigation-testing` cookie before the callback, clear it after (even on error)
4. Include a `package.json` with the correct package name and build configuration
5. Include a `tsconfig.json` for TypeScript compilation

The root `tsconfig.json` should be updated to add a path mapping for `@next/playwright` so the monorepo's tests can import from it.

After creating the package, update its documentation to describe the API, show usage examples, explain how the cookie mechanism works, and note that the protocol is intentionally minimal so other testing frameworks and dev tools can replicate it.

## Files to Look At

- `test/e2e/app-dir/instant-navigation-testing-api/instant-navigation-testing-api.test.ts` — contains the current inline implementation of `instant()`
- `packages/` — where monorepo packages live (see existing packages for conventions)
- `tsconfig.json` — root TypeScript config with path aliases for monorepo packages
