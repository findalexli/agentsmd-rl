# Upgrade `effect` dependency and fix breaking API changes

## Context

The project uses the `effect` library (currently at `4.0.0-beta.37`) and `@effect/platform-node` (also `4.0.0-beta.37`). Both need to be upgraded to `4.0.0-beta.42`.

The new version introduces at least one breaking change that will cause type errors at call sites in the codebase. The affected files are:

- `packages/app/src/app.tsx` — uses `Effect.timeoutOrElse` inside the `ConnectionGate` component's health check logic
- `packages/opencode/src/effect/cross-spawn-spawner.ts` — uses `Effect.timeoutOrElse` in the process kill escalation logic (inside `make`)

Both files pass options to `Effect.timeoutOrElse` that no longer match the API signature in `4.0.0-beta.42`.

## What needs to happen

1. Update the dependency versions in `package.json` (under `catalog`) for both `effect` and `@effect/platform-node` to `4.0.0-beta.42`
2. Fix the breaking API usage in the two affected files so they compile with the new version
3. Run `bun install` to regenerate the lockfile

## Where to look

- `package.json` — the workspace catalog section defines shared dependency versions
- `packages/app/src/app.tsx` — search for `timeoutOrElse`
- `packages/opencode/src/effect/cross-spawn-spawner.ts` — search for `timeoutOrElse`
- The `effect` library changelog or type definitions for `4.0.0-beta.42` to understand the breaking change
