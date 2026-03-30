# Fix TS6 baseUrl deprecation for extended tsconfig

## Bug Description

When a Next.js project uses TypeScript 6 and has a `tsconfig.json` that **extends** another tsconfig which defines `compilerOptions.baseUrl`, the type checking fails with TS5101 deprecation errors. The current code in `getTypeScriptConfiguration.ts` only handles `baseUrl` that is directly declared in the project's own `tsconfig.json` (via `configToParse`), but does not handle the case where `baseUrl` is inherited via the `extends` chain. After `ts.parseJsonConfigFileContent()` resolves the full configuration, `result.options.baseUrl` may contain a value inherited from an extended tsconfig that was never rewritten to use explicit `paths`.

In TypeScript 6, `baseUrl` is deprecated and produces TS5101 warnings during type checking. Next.js already handles this for directly declared `baseUrl` by rewriting path aliases and removing `baseUrl`, but this logic does not run for inherited values, causing the deprecation error to surface.

## What to Fix

In `packages/next/src/lib/typescript/getTypeScriptConfiguration.ts`:

1. After `ts.parseJsonConfigFileContent()` produces the fully resolved `result`, check if `result.options.baseUrl` is a non-empty string when running on TypeScript >= 6.0.0. This covers `baseUrl` that was inherited via `extends` and not caught by the earlier direct-config check.

2. If so, normalize the inherited `baseUrl` relative to the tsconfig directory, rewrite `result.options.paths` using that base URL (so path aliases resolve correctly without `baseUrl`), and then delete `result.options.baseUrl` from the parsed options.

3. Extract the existing inline path-rewriting logic into a reusable helper function so both the direct-config path and the post-parse inherited path can share the same rewriting code.

## Affected Code

- `packages/next/src/lib/typescript/getTypeScriptConfiguration.ts` — the main fix location

## Acceptance Criteria

- When `baseUrl` is inherited via `extends` in a tsconfig, TS6 deprecation checks no longer fail type checking
- Path aliases are correctly rewritten to be relative when `baseUrl` is removed
- Direct `baseUrl` declarations continue to work as before
- The file remains syntactically valid TypeScript
