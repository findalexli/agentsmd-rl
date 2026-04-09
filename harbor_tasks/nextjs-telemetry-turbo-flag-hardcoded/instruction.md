# Telemetry turboFlag always reports false

## Problem

The `turboFlag` field in Next.js build telemetry is hardcoded to `false` in both the build and export code paths. This means telemetry always reports that Turbopack is *not* being used, even when the build is actually running with Turbopack as the bundler.

The telemetry event is emitted at the start of a build (in the `build()` function) and during export (in `exportAppImpl()`). In both locations, the `turboFlag` property is set to a literal `false` instead of checking which bundler is actually in use.

## Expected Behavior

When a build uses Turbopack, `turboFlag` should be `true`. When using webpack or another bundler, it should be `false`. The value should be derived from the actual bundler selection, not hardcoded.

The `Bundler` enum (in `packages/next/src/lib/bundler.ts`) already tracks which bundler is active. The export code path receives its configuration through `ExportAppOptions` (defined in `packages/next/src/export/types.ts`), but that interface currently has no way to convey which bundler is in use.

## Files to Look At

- `packages/next/src/build/index.ts` — the main build entry point, contains the telemetry call with hardcoded `turboFlag: false`
- `packages/next/src/export/index.ts` — the export implementation, also has `turboFlag: false` in its telemetry call
- `packages/next/src/export/types.ts` — defines `ExportAppOptions`, which needs to carry bundler info
- `packages/next/src/lib/bundler.ts` — the `Bundler` enum with `Turbopack`, `Webpack`, `Rspack` members
