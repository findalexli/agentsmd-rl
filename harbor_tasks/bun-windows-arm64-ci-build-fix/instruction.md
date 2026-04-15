# CI: Fix Windows ARM64 build crash and add binary size monitoring

## Problem

1. **Windows ARM64 builds intermittently crash** with exit code 0xC0000409 (STATUS_STACK_BUFFER_OVERRUN) during the build process. The crash occurs when running the build script under Node v24 with experimental TypeScript support enabled on Windows ARM64 targets.

2. **No binary size tracking** exists in the CI pipeline. Binary sizes are not recorded during release builds or compared against canary and release baselines.

## Expected Behavior

1. Windows ARM64 builds must complete successfully without crashing.

2. The CI pipeline must support:
   - Parsing `[skip size check]` or `[skip-size-check]` flags from commit messages
   - A `getBinarySizeStep()` function that creates a BuildKite step with key `"binary-size"` for size aggregation
   - Running `bun scripts/binary-size.ts` for size checking
   - A `threshold-mb` parameter for size threshold configuration
   - An option `skipSizeCheck` (accessed via `options.skipSizeCheck`) to skip size checks
   - The size step must have a `depends_on` property linking to release builds
   - Platform-aware runtime selection using a ternary expression that selects different runtimes based on OS (`target.os`) and architecture (`target.arch`)

## Files to Look At

- `.buildkite/ci.mjs` — The main CI pipeline configuration that generates BuildKite steps
- `scripts/build/ci.ts` — CI build utilities that handle packaging and upload
- `scripts/utils.mjs` — Shared utilities including emoji mappings for BuildKite annotations

## Notes

- The Windows ARM64 crash is related to Node v24's experimental TypeScript support and the interaction between the runtime and Windows ARM64 platform
- Other platforms should continue using the existing Node configuration with TypeScript support
- The binary size step should run after all release builds complete