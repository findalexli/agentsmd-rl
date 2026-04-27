# Simplify local WebKit builds to auto-configure and build JSC

## Problem

Building Bun with a local WebKit clone (`-DWEBKIT_LOCAL=ON`) currently requires developers to manually configure and build JSC in separate steps before building Bun itself. The workflow documented in CONTRIBUTING.md involves running `bun run jsc:build:debug` followed by a manual `cmake --build vendor/WebKit/WebKitBuild/Debug --target jsc` command, plus deleting a generated header file each time. This is error-prone and confusing for contributors.

Several related issues need to be addressed:

1. **No automatic JSC configuration**: When `WEBKIT_LOCAL` is enabled in cmake, the build system assumes JSC has already been configured and built externally. It should instead auto-configure JSC by invoking cmake on the WebKit source and create a build target so JSC is built as part of the normal build.

2. **No way to decouple JSC build type**: There is no way to set the JSC build type independently of the main Bun build type. A new cmake option is needed so developers can, for example, build Bun in Debug mode while building JSC in Release mode.

3. **vcpkg dependency for Windows ICU**: On Windows, the current code uses pre-installed vcpkg packages for ICU headers. This should be replaced with building ICU from the WebKit source tree so the build is self-contained.

4. **Hardcoded ICU library paths on Linux**: For local builds on Linux, ICU libraries are linked via hardcoded paths that assume the prebuilt WebKit layout. Local builds should use the system's ICU installation via cmake's `find_package`.

5. **Missing build ordering**: There is no build dependency ensuring JSC is compiled before Bun's C++ sources when using a local WebKit. This can cause build failures on clean builds.

6. **Stale documentation**: Both `CONTRIBUTING.md` and `docs/project/contributing.mdx` describe the old multi-step manual process (including commands like `jsc:build:debug && rm ...` and `cmake --build vendor/WebKit/WebKitBuild/...`). They also contain a typo: "if you change make changes" should be "if you make changes".

## Acceptance Criteria

- `cmake/tools/SetupWebKit.cmake` must define a `WEBKIT_BUILD_TYPE` cmake option for setting the local JSC build type independently
- `cmake/tools/SetupWebKit.cmake` must auto-configure JSC via `execute_process` when `WEBKIT_LOCAL` is enabled, and create a build target via `add_custom_target` so JSC is built automatically
- `cmake/tools/SetupWebKit.cmake` must not use vcpkg for ICU; Windows ICU should be built from the WebKit source tree
- `cmake/targets/BuildBun.cmake` must add a build dependency (via `add_dependencies`) to ensure JSC is built before Bun when using a local WebKit
- `cmake/targets/BuildBun.cmake` must use `find_package(ICU)` for local WebKit builds on Linux instead of hardcoded prebuilt library paths
- `CONTRIBUTING.md` and `docs/project/contributing.mdx` must remove the old multi-step manual JSC build commands and fix the "change make changes" typo
