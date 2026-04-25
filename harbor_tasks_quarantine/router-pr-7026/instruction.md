# Remove Global Pollution from Router Modules

## Problem

The `@tanstack/react-router` and `@tanstack/solid-router` packages are polluting the global namespace. When these router modules are imported, they automatically assign functions to `globalThis`, which is an unwanted side effect.

Specifically, after importing either router package:
- `globalThis.createFileRoute` becomes defined
- `globalThis.createLazyFileRoute` becomes defined

This global pollution:
1. Can cause conflicts with other libraries
2. Increases bundle size unnecessarily
3. Violates module encapsulation principles

## Expected Behavior

Importing the router packages should not set any properties on `globalThis` or `window`. The following patterns must NOT appear in either router.ts file:

### Import patterns that must be removed:
- `import { createFileRoute, createLazyFileRoute } from './fileRoute'`

### Global assignment patterns that must be removed:
- `(globalThis as any).createFileRoute`
- `(globalThis as any).createLazyFileRoute`

### Window assignment patterns that must be removed:
- `(window as any).createFileRoute`
- `(window as any).createLazyFileRoute`

After the fix, importing the router packages should result in:
- `typeof globalThis.createFileRoute === 'undefined'`
- `typeof globalThis.createLazyFileRoute === 'undefined'`

The `createFileRoute` and `createLazyFileRoute` functions should only be available through explicit imports from the fileRoute module (e.g., `import { createFileRoute } from './fileRoute'` or `import { createFileRoute } from '@tanstack/react-router/fileRoute'`), not through global variables.

## Files to Investigate

- `packages/react-router/src/router.ts`
- `packages/solid-router/src/router.ts`

## Constraints

- The `createFileRoute` and `createLazyFileRoute` functions must remain importable from their respective `fileRoute` modules
- The `Router` class export must continue to work correctly
- Both react-router and solid-router packages need the same fix
- After making changes, rebuild the affected packages with `pnpm nx run @tanstack/react-router:build` and `pnpm nx run @tanstack/solid-router:build`

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `eslint (JS/TS linter)`
