# Turbopack: Move turbopack out of `pnpm build` and into a `pnpm build-all` command

## Problem

The current build setup forces the Turbopack native binary compilation to run during `pnpm build`, which causes pain for developers who have already compiled a custom version of Turbopack with specific profiles or flags. There's no way to build just the JavaScript parts without also triggering a potentially unnecessary native recompilation.

## What You Need to Do

You need to separate the Turbopack native build from the standard JavaScript build workflow:

1. **Add a `pnpm build-all` command** at the workspace root that builds both JS and Rust code (including the Turbopack native binary). This should call a renamed task `build-native-auto` in the next-swc package.

2. **Rename the build script** in `packages/next-swc/package.json` from `build` to `build-native-auto` (it runs `maybe-build-native.mjs`).

3. **Update `packages/next-swc/turbo.json`** (rename to `turbo.jsonc` with trailing commas) to change the task name from `build` to `build-native-auto`, and add a comment explaining that "auto" checks for precompiled turbopack before building.

4. **Update `AGENTS.md`** to document the new workflow:
   - `pnpm build` should build all JS code only
   - `pnpm build-all` should build all JS and Rust code
   - Update the "after switching branches" section to use `build-all`
   - Update the "when editing Turbopack" section to use `build-all`

## Files to Look At

- `package.json` — root workspace scripts
- `packages/next-swc/package.json` — next-swc package scripts
- `packages/next-swc/turbo.json` — turborepo task configuration (rename to turbo.jsonc)
- `AGENTS.md` — developer guide that needs updating

## Notes

- The `build-native-auto` script checks if there's already an up-to-date precompiled version of turbopack available before performing the build
- The turbo.jsonc file should have trailing commas (hence the .jsonc extension)
- Make sure the AGENTS.md documentation clearly distinguishes when to use `pnpm build` vs `pnpm build-all`
