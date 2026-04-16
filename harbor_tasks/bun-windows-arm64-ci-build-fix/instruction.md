# CI: Fix Windows ARM64 build crash and add binary size monitoring

## Problem

1. **Windows ARM64 builds intermittently crash** with exit code 0xC0000409 (STATUS_STACK_BUFFER_OVERRUN) during the build process. The current runtime selection in the build command function causes this crash on Windows ARM64.

2. **No binary size tracking** exists in the CI pipeline. Binary sizes are not recorded during release builds or compared against canary and release baselines.

## Expected Behavior

1. Windows ARM64 builds must complete successfully without crashing. The build command function must select a different runtime for Windows ARM64 than for other platforms. The function checks both the OS and architecture of the target.

2. The CI pipeline must support:
   - Parsing `[skip size check]` or `[skip-size-check]` flags from commit messages — when present, the size check step should soft-fail
   - A `getBinarySizeStep(releasePlatforms, options)` function that creates a BuildKite step for size aggregation. The step uses `soft_fail` (set via a truthy check on the skip option), includes a `key` property with value `"binary-size"`, a `command` property running `bun scripts/binary-size.ts`, a `depends_on` property linking to release builds, and a `threshold-mb` configuration parameter. The function ends with a constant named `BINARY_SIZE_THRESHOLD_MB`.
   - An option `skipSizeCheck` accessed via `options.skipSizeCheck` to skip size checks

## Files to Look At

- `.buildkite/ci.mjs` — The main CI pipeline configuration that generates BuildKite steps. Contains `getBuildCommand(target, options, mode)` and `getBuildArgs(target, options, mode)` functions.
- `scripts/build/ci.ts` — CI build utilities that handle packaging and upload
- `scripts/utils.mjs` — Shared utilities including emoji mappings for BuildKite annotations

## Notes

- The Windows ARM64 crash is an intermittent runtime crash triggered during the build process
- Other platforms (non-Windows-ARM64) must continue using the existing build configuration
- The binary size step should run after all release builds complete