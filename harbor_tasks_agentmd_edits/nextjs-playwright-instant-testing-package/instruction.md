# Extract Instant Navigation Testing API into Standalone Package

## Problem

The instant navigation testing API is implemented as an inline helper within the test file `test/e2e/app-dir/instant-navigation-testing-api/instant-navigation-testing-api.test.ts`. The `instant()` function and its associated `INSTANT_COOKIE` constant are defined directly in the test file, making them impossible to reuse across other test suites or share with external projects that want to test instant navigation behavior in their Next.js applications.

The inline implementation also means the nested-scope detection test has to manually manipulate cookies rather than exercising the actual API.

## Expected Behavior

Extract the `instant()` testing helper into a new `@next/playwright` package at `packages/next-playwright/`. The package should:

1. Export the `instant()` function as a standalone module with proper TypeScript types
2. Use a structural type for the Playwright `Page` interface so it works with any Playwright version
3. Include a proper `package.json`, `tsconfig.json`, and package entry point

The existing test file should import `instant()` from the new `@next/playwright` package instead of using the inline implementation. The root `tsconfig.json` needs a path alias mapping `@next/playwright` to the new package source.

The new package must include a comprehensive `README.md` documenting:
- The package's purpose and experimental status
- How to use the `instant()` helper with realistic Playwright examples
- How the underlying cookie-based mechanism works
- How to enable the testing API in production builds

After fixing the code, update the relevant documentation to reflect the change.

## Files to Look At

- `test/e2e/app-dir/instant-navigation-testing-api/instant-navigation-testing-api.test.ts` — contains the inline `instant()` implementation to extract
- `tsconfig.json` — root TypeScript config that needs a path alias for the new package
- `packages/` — existing monorepo packages for structural reference
- `CLAUDE.md` — repo conventions including the README files rule for new packages
