# Remove sccache build caching, use ccache only

## Problem

The Bun project's build system uses `sccache` for compilation caching, which requires S3 credentials for distributed caching and adds complexity to the build setup. When `sccache` is not installed, the build falls back to `ccache`, but the CMake configuration still tries to detect and prefer `sccache`, and missing `ccache` on CI causes build failures. The `scripts/build-cache/` directory contains AWS S3 access tooling that's only needed for `sccache`.

The bootstrap scripts download a specific `sccache` binary from GitHub releases, which is more complex than just using system package managers.

## Expected Behavior

- The build system should use `ccache` exclusively (no `sccache`)
- Missing `ccache` should be gracefully skipped without failing the build
- The `scripts/build-cache/` directory (S3 access tooling) should be removed
- Bootstrap scripts should install `ccache` via system package managers instead of downloading a binary
- Documentation should reflect the `ccache`-only approach

## Files to Look At

- `CMakeLists.txt` — sccache/ccache detection and inclusion logic
- `cmake/tools/SetupCcache.cmake` — ccache cmake module (currently disables ccache on CI)
- `cmake/tools/SetupSccache.cmake` — sccache cmake module (should be removed)
- `scripts/bootstrap.sh` — `install_sccache` function downloads sccache binary
- `scripts/build.mjs` — references sccache for build stats
- `scripts/build-cache/` — S3 access tooling (only for sccache)

## Documentation Updates Required

After making the code changes, update the documentation to reflect the new `ccache`-only approach:

- `CONTRIBUTING.md` — Update the "Optional: Install sccache" section to use ccache instead
- `docs/project/contributing.mdx` — Same changes as CONTRIBUTING.md
- `docs/project/building-windows.mdx` — Update scoop install command to use ccache
