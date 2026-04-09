# build: share cacheDir across checkouts for local builds

## Problem

Local (non-CI) builds default `cfg.cacheDir` to `<buildDir>/cache`, so each checkout maintains its own ccache, zig cache, dep tarballs, and prebuilt WebKit. Multiple checkouts on the same developer machine can't reuse each other's cached artifacts, leading to redundant downloads and cold rebuilds.

Additionally, the download helper in `scripts/build/download.ts` uses a fixed `.partial` temp file suffix, which means concurrent builds from different checkouts sharing a cache directory could stomp on each other's downloads and extractions.

## Expected Behavior

- Local builds should default `cfg.cacheDir` to a shared location (`$BUN_INSTALL/build-cache` or `~/.bun/build-cache`) so cached artifacts are reused across checkouts
- CI builds should continue using `<buildDir>/cache` to stay hermetic (`rm -rf build/` is a full reset)
- An explicit `--cacheDir=...` should continue to override both
- Download temp files should use process-unique paths to prevent concurrent-build collisions
- A `clean cache` preset should exist to wipe the shared cache when needed
- `scripts/build/CLAUDE.md` should document the new cache behavior in the Gotchas section

## Files to Look At

- `scripts/build/config.ts` — `resolveConfig()` cacheDir resolution logic
- `scripts/build/download.ts` — temp path generation in `downloadWithRetry()` and `fetchPrebuilt()`
- `scripts/build/clean.ts` — clean presets
- `scripts/build/configure.ts` — ccache environment documentation
- `scripts/build/CLAUDE.md` — build system Gotchas section
