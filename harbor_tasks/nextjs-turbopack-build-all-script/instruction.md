# Turbopack: Separate native binary build from JS build

## Problem

The current `pnpm build` command triggers both JavaScript compilation and Turbopack native binary compilation via the `next-swc` package. Developers who have already compiled a custom Turbopack binary have no way to build just the JavaScript parts without also triggering a potentially unnecessary native recompilation.

The root cause is that the `next-swc` package's `build` script calls `maybe-build-native.mjs`, and the root `pnpm build` command's Turbo pipeline includes the `next-swc` `build` task, which causes native compilation to run as part of every build.

## Expected Behavior

The build system should provide two distinct commands:

- **`pnpm build`** — builds all JavaScript code only (no Rust/Turbopack native compilation)
- **`pnpm build-all`** — builds all JavaScript and Rust code, including the Turbopack native binary

The root `package.json` should have a `build-all` script that runs a Turbo pipeline including both JS builds and a `build-native-auto` task.

The `next-swc` package should expose a `build-native-auto` script (invoking `maybe-build-native.mjs`). The native build step should be decoupled from the standard `build` pipeline so that `pnpm build` only builds JS.

The Turborepo task configuration for `next-swc` should define a `build-native-auto` task (for use by `build-all`) and include a comment explaining that the "auto" script checks for a precompiled Turbopack binary before building. Since comments are needed, the configuration should use a JSON-with-comments format.

`AGENTS.md` should document:
- The scope of `pnpm build` ("build all JS code") versus `pnpm build-all` (JS and Rust)
- Using `pnpm build-all` after switching branches
- Using `pnpm build-all` when editing Turbopack/Rust code

## Files Involved

- `package.json` — root workspace scripts
- `packages/next-swc/package.json` — next-swc package scripts
- `packages/next-swc/turbo.json` — Turborepo task configuration for next-swc
- `AGENTS.md` — developer documentation
