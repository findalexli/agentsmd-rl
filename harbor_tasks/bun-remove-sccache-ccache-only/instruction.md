# Remove sccache, Use ccache Only

## Background

The Bun build system currently supports both sccache (with S3 distributed caching) and ccache. This dual-caching setup adds unnecessary complexity and causes build failures when ccache is not installed. The project should use only ccache, and ccache should be optional — builds must succeed even without it installed.

## Problem Statement

### Build System

The build system configures sccache and ccache for compilation caching:

- `cmake/tools/SetupSccache.cmake` — configures sccache for the build
- `cmake/tools/SetupCcache.cmake` — configures ccache but treats it as a hard requirement
- `CMakeLists.txt` — references both caching configurations
- `scripts/build-cache/` — contains scripts for sccache's S3-based distributed caching

The current ccache configuration causes builds to fail when ccache is not present on the system.

### Documentation

Three documentation files reference the current dual-caching setup:

1. **`CONTRIBUTING.md`** — Contains references to sccache and includes an AWS credentials section for S3 cache access. Lacks dedicated ccache installation instructions for macOS, Linux, and other platforms.

2. **`docs/project/contributing.mdx`** — Same documentation in docs-site format. References sccache and does not include ccache in the macOS Homebrew install instructions.

3. **`docs/project/building-windows.mdx`** — The Windows `scoop install` line references sccache instead of ccache.

## Desired Outcome

After the changes, the build system should:

- Have no sccache configuration files remaining
- Have ccache available as an optional dependency (builds succeed without it installed)
- Reference only ccache, not sccache, in all build documentation

Specifically:

- `cmake/tools/SetupSccache.cmake` should be removed
- `scripts/build-cache/` directory should be removed
- `cmake/tools/SetupCcache.cmake` should continue to locate ccache via `find_command` but ccache must not be a hard requirement for builds
- `CONTRIBUTING.md`, `docs/project/contributing.mdx`, and `docs/project/building-windows.mdx` should reference ccache and not sccache
- `CONTRIBUTING.md` should include ccache installation instructions for macOS and Linux, and mention how to check cache statistics
- `CONTRIBUTING.md` should not contain AWS or S3 configuration references
- `docs/project/building-windows.mdx` scoop install line for nodejs should reference ccache, not sccache