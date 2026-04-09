# Separate Turbopack native build from `pnpm build`

## Problem

Currently, `pnpm build` in the Next.js monorepo triggers compilation of everything including the Turbopack native Rust binary (via `packages/next-swc/`). This means developers who already have a custom-compiled Turbopack binary (e.g., built with a specific profile or debug flags) cannot rebuild just the JavaScript portions without also recompiling the Rust code, which is slow and overwrites their custom binary.

The `packages/next-swc/package.json` has a `build` script that runs `maybe-build-native.mjs`, which gets picked up by the workspace-level `pnpm build` through Turborepo task resolution.

## Expected Behavior

- `pnpm build` should only build JavaScript code (not trigger Rust/native compilation)
- A separate command (e.g., `pnpm build-all`) should exist for building everything including native Rust code
- The Turborepo task configuration in `packages/next-swc/` should be updated to reflect the new script naming
- The project's agent instructions (`AGENTS.md`) should be updated to document the new build commands, distinguishing when to use `pnpm build` (JS only) vs the full build command

## Files to Look At

- `package.json` — root workspace scripts
- `packages/next-swc/package.json` — native SWC/Turbopack build scripts
- `packages/next-swc/turbo.json` — Turborepo task configuration for the next-swc package
- `AGENTS.md` — developer/agent build workflow documentation (multiple sections reference `pnpm build`)
