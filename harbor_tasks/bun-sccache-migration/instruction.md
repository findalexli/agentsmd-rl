# Migrate Build System from ccache to sccache

## Overview

Bun currently uses `ccache` for C/C++ compilation caching. This task is to migrate the build system to use `sccache` instead, which provides distributed S3-backed caching capabilities.

## Required Changes

### 1. CMake Configuration

Update the CMake build system to use sccache:

- Replace `cmake/tools/SetupCcache.cmake` with a new `cmake/tools/SetupSccache.cmake` module
- The new module should:
  - Configure the S3 bucket `bun-build-sccache-store` in region `us-west-1`
  - Detect AWS credentials from environment or `~/.aws/credentials`
  - Detect CI environment via EC2 instance metadata (check for `buildkite-agent` Service tag)
  - Support read-only cache mode for users without AWS credentials
  - Set `SCCACHE_LOG=info` for observability
- Update `CMakeLists.txt` to include `SetupSccache` instead of `SetupCcache`
- Update `cmake/Globals.cmake` to remove the `write-only` option from `CACHE_STRATEGY` (now only `read-write|read-only|none`)

### 2. Documentation Updates

Update `CONTRIBUTING.md` to document the new build cache system:

- Replace `ccache` with `sccache` in all package manager install commands (Homebrew, apt, pacman, dnf)
- Add a new "Optional: Install `sccache`" section after the dependencies section that:
  - Explains sccache is used for compilation caching with S3 support
  - Provides macOS (`brew install sccache`) and Linux (`cargo install sccache --features=s3`) install instructions
  - Documents AWS credential setup for core developers with write access
  - Includes troubleshooting for common issues (cache stats command, multiple AWS profiles, server restart)
- Remove the "ccache conflicts with building TinyCC on macOS" troubleshooting section

### 3. Build Script Updates

Update the build and bootstrap scripts:

**scripts/bootstrap.sh:**
- Replace `install_ccache` function with `install_sccache` that downloads from GitHub releases (v0.12.0)
- Update the execute() function to use `set -x` for better debugging

**scripts/bootstrap.ps1:**
- Remove `ccache` from package installation
- Add `Install-Sccache` function that uses `Install-Package sccache -Version "0.12.0"`
- Call `Install-Sccache` after `Install-Rust`

**scripts/build.mjs:**
- Remove the custom cache handling logic (cache copying, read/write mode detection, `getCachePath`, `isCacheReadEnabled`, `isCacheWriteEnabled`, `getDefaultBranch`)
- Simplify to just set `CACHE_STRATEGY=read-write` by default
- Add `sccache --show-stats` call after the build completes (wrapped in a "sccache stats" group)
- Remove unused fs imports (`chmodSync`, `cpSync`, `mkdirSync`)

**scripts/machine.mjs:**
- Attach IAM instance profile `buildkite-build-agent` when `options.ci` is true
- Set `Service` tag to `buildkite-agent` when CI mode is enabled

### 4. Nix Configuration

Update Nix files to use sccache:

- **flake.nix**: Replace `pkgs.ccache` with `pkgs.sccache`
- **shell.nix**: Replace `ccache` with `sccache`

### 5. Windows Documentation

Update `docs/project/building-windows.mdx`:
- Remove `Ccache` from the required tools list
- Replace `ccache` with `sccache` in the scoop install command

### 6. CI Configuration

Update `.buildkite/Dockerfile`:
- Add sccache v0.12.0 installation from GitHub releases after cmake installation
- Install to `/usr/local/bin`

## Key Requirements

- **sccache version**: Use exactly version 0.12.0
- **S3 bucket**: `bun-build-sccache-store` in `us-west-1`
- **AWS credential detection**: Should check environment variables AND `~/.aws/credentials`
- **CI detection**: Query EC2 metadata at `169.254.169.254/latest/meta-data/tags/instance/Service`
- **Fallback behavior**: Read-only anonymous access when no credentials available

## Testing

After making changes:

1. Verify `SetupSccache.cmake` exists with correct S3 configuration
2. Verify `SetupCcache.cmake` is removed
3. Verify `CMakeLists.txt` references SetupSccache
4. Verify CONTRIBUTING.md has sccache (not ccache) in package lists
5. Verify all build scripts reference sccache correctly

## Relevant Files

- `CMakeLists.txt` - Main CMake configuration
- `cmake/Globals.cmake` - Cache strategy options
- `cmake/tools/SetupCcache.cmake` - Old module (to delete)
- `cmake/tools/SetupSccache.cmake` - New module (to create)
- `CONTRIBUTING.md` - Developer documentation
- `docs/project/building-windows.mdx` - Windows build docs
- `flake.nix`, `shell.nix` - Nix environment
- `scripts/bootstrap.sh`, `scripts/bootstrap.ps1` - Bootstrap scripts
- `scripts/build.mjs` - Build orchestration
- `scripts/machine.mjs` - CI machine provisioning
- `.buildkite/Dockerfile` - CI Docker image
