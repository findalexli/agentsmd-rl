# Simplify `bun run build:local` to auto-build JSC

## Problem

Building Bun with a local WebKit/JSC checkout currently requires multiple manual steps: running `bun run jsc:build:debug`, manually deleting a duplicate `InspectorProtocolObjects.h` header, and then running the Bun build separately. This is error-prone and poorly documented across platforms (macOS, Linux, Windows each have different ICU requirements).

The `cmake/tools/SetupWebKit.cmake` file's `WEBKIT_LOCAL` code path only sets include paths and assumes JSC is already pre-built. It doesn't actually configure or build JSC.

## Expected Behavior

`bun run build:local` should handle everything in a single command: configuring JSC, building JSC, and building Bun. Specifically:

1. **`cmake/tools/SetupWebKit.cmake`** should, when `WEBKIT_LOCAL` is set:
   - Configure JSC automatically using CMake (with proper flags like `-DPORT=JSCOnly`, `-DENABLE_STATIC_JSC=ON`, etc.)
   - Create a build target that builds JSC (delegating to JSC's inner build system)
   - Support incremental rebuilds
   - Handle ICU correctly per platform (system ICU on macOS/Linux, build from source on Windows)
   - Add a `WEBKIT_BUILD_TYPE` option that defaults to `CMAKE_BUILD_TYPE`

2. **`cmake/targets/BuildBun.cmake`** should:
   - Add JSC as a build dependency so it's built before Bun's C++ sources
   - Use system ICU (via `find_package`) on Linux for local builds instead of requiring bundled static libs

3. **Documentation** (`CONTRIBUTING.md` and `docs/project/contributing.mdx`) should be updated to reflect the simplified workflow — remove the old multi-step manual JSC build instructions and explain that `build:local` handles everything automatically.

## Files to Look At

- `cmake/tools/SetupWebKit.cmake` — the `WEBKIT_LOCAL` code path needs to be replaced with full JSC configure + build integration
- `cmake/targets/BuildBun.cmake` — needs JSC build dependency and system ICU support for local builds
- `CONTRIBUTING.md` — "Building WebKit locally" section has outdated multi-step instructions
- `docs/project/contributing.mdx` — parallel documentation file that mirrors CONTRIBUTING.md
