# TypeScript 6 Compatibility: Deprecated Defaults in Next.js Config

## Bug Description

Next.js automatically configures TypeScript compiler options when setting up or updating a project's `tsconfig.json`. The relevant logic lives in two files under `packages/next/src/lib/typescript/`:

- **`writeConfigurationDefaults.ts`** — the `getDesiredCompilerOptions()` function determines what defaults to write into a project's `tsconfig.json`. It currently always defaults `moduleResolution` to `"node"` regardless of the TypeScript version or the configured `module` setting.

- **`getTypeScriptConfiguration.ts`** — the `getTypeScriptConfiguration()` function parses the user's `tsconfig.json` via TypeScript's own config API. It currently passes the raw config through without any transformations.

## Problem

TypeScript 6 introduces several deprecations that break builds using Next.js defaults:

1. **`moduleResolution: "node"`** is treated as the deprecated `"node10"` in TS 6, causing `TS5107` errors. For projects using modern module modes (ESNext, ES2020, Preserve, etc.), the `"bundler"` resolution strategy is the correct default. Only `commonjs`/`amd` module configs should keep `"node"`.

2. **`baseUrl` for path aliasing** is deprecated in TS 6 (`TS5101`). Projects that rely on `baseUrl` to resolve bare-specifier imports (e.g., `import foo from "utils/foo"`) will fail. The resolution needs to happen by migrating `baseUrl`-based resolution into explicit `paths` entries with properly resolved relative targets.

3. **`target: "es5"` / `"es3"`** are deprecated in TS 6. Configs using these targets need to be rewritten in-memory to a supported target (like `"es2015"`) before the TypeScript config parser sees them.

## Expected Behavior

- For TypeScript >= 5.0.0 with non-`commonjs`/non-`amd` module settings, `moduleResolution` should default to `"bundler"` instead of `"node"`.
- For TypeScript >= 6.0.0, `baseUrl` should be transparently migrated to equivalent `paths` entries (including a wildcard fallback) before config parsing.
- For TypeScript >= 6.0.0, deprecated `target` values (`es3`, `es5`) should be rewritten in-memory to `"es2015"` before config parsing.

## Reproduction

Configure a Next.js project with TypeScript 6 and an empty or default `tsconfig.json`. Running `next dev` or `next build` will fail with `TS5107` because `moduleResolution: "node"` is deprecated.

Similarly, any project with `baseUrl: "."` in its tsconfig will break under TS 6 due to `TS5101`.
