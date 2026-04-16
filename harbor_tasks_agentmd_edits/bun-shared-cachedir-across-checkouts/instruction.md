# Share cacheDir across checkouts for local builds

## Problem

Currently, local (non-CI) builds store the cache directory inside the build folder (`<buildDir>/cache`). This means:
1. Multiple checkouts of the Bun repo on the same machine don't share ccache objects, zig caches, dependency tarballs, or prebuilt WebKit
2. Developers lose cached work when they run `rm -rf build/`
3. Concurrent builds from different checkouts can stomp on each other's downloads due to non-unique temp file paths

## Required Changes

### 1. Build Configuration (`scripts/build/config.ts`)

Modify the `resolveConfig` function to default `cacheDir` to a machine-shared location for local builds:
- For **non-CI builds**: use `$BUN_INSTALL/build-cache` (or `~/.bun/build-cache` if BUN_INSTALL not set)
- For **CI builds**: keep current behavior (`<buildDir>/cache`) so runners remain hermetic
- Ensure relative BUN_INSTALL paths are anchored to repo root

### 2. Clean Script (`scripts/build/clean.ts`)

Add support for cleaning the machine-shared cache:
- Import `homedir` from `node:os`
- Define `sharedCacheDir` pointing to the same location as config.ts
- Add a new `cache` preset that deletes the shared cache directory
- Update the `zig` preset to also clean `sharedCacheDir/zig`
- Document the new preset in the help text

### 3. Configure Script (`scripts/build/configure.ts`)

Update the `ccacheEnv` function's documentation comment to reflect that ccache now uses `cfg.cacheDir` (machine-shared locally, per-build in CI) instead of always using the build directory.

### 4. Download Script (`scripts/build/download.ts`)

Make downloads concurrent-safe to support shared cacheDir across multiple checkouts:
- Use process-unique temp paths (e.g., `${dest}.${process.pid}.partial` instead of `${dest}.partial`)
- Add unique suffix using `Date.now().toString(36)` for staging directories
- Handle concurrent fetch race conditions: if another process wins the race, check if the stamp matches and treat as success
- Restructure extraction to use try/finally for cleanup

### 5. Documentation Update (`scripts/build/CLAUDE.md`)

After implementing the code changes, update the build system documentation to explain the new cache behavior:

Add a note explaining that:
- `rm -rf build/` no longer clears the cache locally
- The cache is machine-shared at `$BUN_INSTALL/build-cache` for non-CI builds
- This includes ccache, zig cache, tarballs, and prebuilt WebKit
- Cache entries are content-addressed/version-stamped, so stale entries can't be hit
- Developers shouldn't reach for `bun run clean cache` as a debugging step
- CI keeps `<buildDir>/cache` so `rm -rf build/` is still a full reset there

## Files to Modify

- `scripts/build/config.ts` - cacheDir resolution logic
- `scripts/build/clean.ts` - add cache preset
- `scripts/build/configure.ts` - update ccache comment
- `scripts/build/download.ts` - concurrent-safe downloads
- `scripts/build/CLAUDE.md` - document new cache behavior

## Verification

The tests will verify:
1. CLAUDE.md contains documentation about the shared cache behavior
2. config.ts uses machine-shared cacheDir for non-CI builds
3. clean.ts has a 'cache' preset
4. configure.ts has updated ccache comment
5. download.ts uses process.pid for unique temp paths
6. download.ts handles concurrent fetch scenarios
7. All TypeScript files have valid syntax
