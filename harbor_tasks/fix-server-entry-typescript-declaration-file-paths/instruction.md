# Fix server-entry TypeScript declaration file paths

## Problem

The `server-entry` package export types are missing from published packages. When building the `react-start`, `solid-start`, and `vue-start` packages, TypeScript declaration files are not being emitted at the expected paths.

## Background

This issue was introduced when upgrading to TypeScript 6. In TS6, the default `rootDir` behavior changed from inferred to defaulting to `"."`. This causes `vite-plugin-dts` to emit declarations at the wrong nested path instead of the expected path declared in `package.json` exports.

**Current (broken) output path:**
```
dist/default-entry/esm/src/default-entry/server.d.ts
```

**Expected output path:**
```
dist/default-entry/esm/server.d.ts
```

## Your Task

Fix the `server-entry` package export types path so published packages include the expected declaration files. You need to:

1. Add a `tsconfig.server-entry.json` file to each of the three packages (`react-start`, `solid-start`, `vue-start`) with:
   - `rootDir` set to `"./src/default-entry"`
   - `include` set to `["src/default-entry"]`
   - Extending the base `./tsconfig.json`

2. Update each `vite.config.server-entry.ts` to reference the new tsconfig via `tsconfigPath` option in the `tanstackViteConfig` call.

3. Update the `test:build` script in each package's `package.json` to run package validation (`publint --strict && attw --ignore-rules no-resolution --pack .`) instead of the current no-op.

## Relevant Files

- `packages/react-start/vite.config.server-entry.ts`
- `packages/react-start/package.json`
- `packages/solid-start/vite.config.server-entry.ts`
- `packages/solid-start/package.json`
- `packages/vue-start/vite.config.server-entry.ts`
- `packages/vue-start/package.json`

## Tips

- Look at how other `vite.config.ts` files in the repo configure `tsconfigPath`
- The `tanstackViteConfig` function accepts a `tsconfigPath` option
- The issue is specifically about the `default-entry` server entry point
- Build validation should pass after the fix

## Agent Context

This is a TanStack Router monorepo using pnpm workspaces. Build with `pnpm build` in each package directory. The `publint` and `@arethetypeswrong/cli` (attw) packages are used for package validation.

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `prettier (JS/TS/JSON/Markdown formatter)`
