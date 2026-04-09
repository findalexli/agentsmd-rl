# Migrate Bun's build system from ccache to sccache

## Problem

Bun's build system currently uses `ccache` for local compilation caching, which limits caching to the local machine. The project wants to migrate to `sccache` (shared compilation cache) which supports distributed caching via S3, allowing CI and developer builds to share cached compilation artifacts.

## What Needs to Change

The migration touches multiple layers of the build system:

1. **CMake configuration**: The `cmake/tools/SetupCcache.cmake` module needs to be replaced with a new `SetupSccache.cmake` module that configures sccache with S3 bucket storage, AWS credential detection, and EC2 CI instance detection.

2. **Build scripts**: The JavaScript build script (`scripts/build.mjs`) has complex ccache-specific cache management logic (path computation, permission handling, cache copying) that should be simplified since sccache handles caching internally via S3. The script should just display sccache statistics after builds.

3. **Bootstrap scripts**: The shell and PowerShell bootstrap scripts need to install sccache instead of ccache. Since many Linux package managers don't ship sccache with S3 support, the Linux bootstrap should download the binary directly from GitHub releases.

4. **Nix and CI**: The `flake.nix`, `shell.nix`, Dockerfile, and CI machine provisioning scripts need to reference sccache instead of ccache. CI machines need an IAM instance profile for S3 write access.

5. **Documentation**: CONTRIBUTING.md needs to be updated to reflect the new dependency. The macOS Homebrew install command should use sccache. A new section should document sccache installation with S3 support, AWS credential setup for core developers, and common troubleshooting tips. The old ccache troubleshooting section should be removed.

## Files to Look At

- `cmake/tools/SetupCcache.cmake` — current ccache setup (to be replaced)
- `cmake/tools/SetupSccache.cmake` — new sccache setup module (to be created)
- `CMakeLists.txt` — includes the cache setup module
- `cmake/Globals.cmake` — defines CACHE_STRATEGY options
- `scripts/build.mjs` — build orchestration with cache management
- `scripts/bootstrap.sh` — Linux/macOS dependency installation
- `scripts/bootstrap.ps1` — Windows dependency installation
- `scripts/machine.mjs` — CI machine provisioning
- `CONTRIBUTING.md` — developer setup documentation
- `docs/project/building-windows.mdx` — Windows build instructions
- `flake.nix` / `shell.nix` — Nix development environment

## Notes

- The sccache version to use is 0.12.0
- The S3 bucket is `bun-build-sccache-store` in `us-west-1`
- sccache should fall back to anonymous (read-only) S3 access when no AWS credentials are found
- CI detection should query the EC2 metadata service at 169.254.169.254 for the `buildkite-agent` service tag
- The `CACHE_STRATEGY` option should no longer include "write-only" since sccache manages this via credential detection
- After fixing the code, update the relevant documentation to reflect the change
