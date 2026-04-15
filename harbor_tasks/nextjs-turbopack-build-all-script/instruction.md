# Turbopack: Separate native binary build from JS build

## Problem

The current `pnpm build` command triggers both JavaScript compilation and Turbopack native binary compilation via the `next-swc` package. Developers who have already compiled a custom Turbopack binary have no way to build just the JavaScript parts without also triggering a potentially unnecessary native recompilation.

The root cause is that the `next-swc` package's `build` script calls `maybe-build-native.mjs`, and the root `pnpm build` command's Turbo pipeline includes the `next-swc` `build` task, which causes native compilation to run as part of every build.

## Required Behavior

The build system must provide two distinct commands with these exact names:

- **`pnpm build`** — builds all JavaScript code only (no Rust/Turbopack native compilation)
- **`pnpm build-all`** — builds all JavaScript and Rust code, including the Turbopack native binary

### Implementation Requirements

1. **Root `package.json`** — add a `build-all` script (exact name) that runs a Turbo pipeline including both JS builds and a `build-native-auto` task

2. **`packages/next-swc/package.json`** — the `build` script that currently calls `maybe-build-native.mjs` should be renamed to `build-native-auto` (exact name). The native build step must be decoupled from the standard `build` pipeline so that `pnpm build` only builds JS.

3. **`packages/next-swc/turbo.json`** — the `build` task should be renamed to `build-native-auto` (exact name). Since the task name change needs explanatory documentation, this configuration should use a format that supports comments (rename from `turbo.json` to `turbo.jsonc`). The comments should explain that the "auto" script checks for a precompiled Turbopack binary before building, and should reference when to use `build-all`.

4. **`AGENTS.md`** — must document:
   - The scope of `pnpm build` ("build all JS code") versus `pnpm build-all` ("JS and Rust" or similar)
   - Using `pnpm build-all` after switching branches
   - Using `pnpm build-all` when editing Turbopack/Rust code

## Files Involved

- `package.json` — root workspace scripts
- `packages/next-swc/package.json` — next-swc package scripts
- `packages/next-swc/turbo.json` — Turborepo task configuration for next-swc (should become `turbo.jsonc`)
- `AGENTS.md` — developer documentation
