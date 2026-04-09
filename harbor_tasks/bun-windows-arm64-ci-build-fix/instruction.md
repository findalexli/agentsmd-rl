# CI: Fix Windows ARM64 build crash and add binary size monitoring

## Problem

The CI pipeline has two issues that need to be fixed:

1. **Windows ARM64 builds intermittently crash** with exit code 0xC0000409 (STATUS_STACK_BUFFER_OVERRUN) during the build process. This appears to happen when running `scripts/build.ts` under Node v24 on Windows ARM64 targets specifically.

2. **No binary size tracking** exists in the CI pipeline. There's no automated way to detect when release binaries grow beyond acceptable thresholds compared to canary or release builds.

## Expected Behavior

1. Windows ARM64 builds should complete successfully without the 0xC0000409 crash.

2. The CI pipeline should support:
   - Parsing `[skip size check]` flags from commit messages
   - A `getBinarySizeStep()` function that aggregates binary sizes from release builds
   - Comparison of current build sizes against canary (latest main) and release baselines
   - Configuration option for size threshold (e.g., 0.5 MB)

## Files to Look At

- `.buildkite/ci.mjs` — The main CI pipeline configuration that generates BuildKite steps. Contains `getBuildCommand()` function that determines how to run the build script, and needs the new `getBinarySizeStep()` function.
- `scripts/build/ci.ts` — CI build utilities that handle packaging and upload. May need to record binary size metadata.
- `scripts/utils.mjs` — Shared utilities including emoji mappings for BuildKite annotations.

## Notes

- The Windows ARM64 crash appears related to Node v24's experimental TypeScript support (`--experimental-strip-types`)
- The binary size step should run after all release builds complete and depend on them
- Consider what runtime alternatives might work more reliably on Windows ARM64
