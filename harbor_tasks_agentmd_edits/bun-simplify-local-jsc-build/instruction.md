# Simplify `bun run build:local` to Auto-Build JSC

## Problem

Building Bun with a local WebKit/JSC currently requires a cumbersome multi-step process:

1. Manually run `bun run jsc:build:debug` to build JSC
2. Manually delete a duplicate `InspectorProtocolObjects.h` header that causes build failures
3. Then run `bun run build:local` separately to build Bun

This means developers need to know about the header deletion workaround and manually orchestrate the JSC build before the Bun build. Incremental JSC rebuilds also require a separate manual `cmake --build` command with the same header deletion workaround.

## Expected Behavior

`bun run build:local` should handle everything automatically in a single command: configuring JSC, building JSC, and building Bun. The build system should:

- Integrate JSC configuration and building into the cmake setup (in `cmake/tools/SetupWebKit.cmake`)
- Define a `jsc` custom build target that delegates to JSC's inner build system
- Add the `jsc` target as a build dependency so Bun's C++ sources wait for JSC
- Support a `WEBKIT_BUILD_TYPE` option to override the JSC build type independently
- On Linux, use system ICU via `find_package` for local builds instead of requiring bundled static libraries
- On Windows, build ICU from source automatically when system libs don't exist

## Files to Look At

- `cmake/tools/SetupWebKit.cmake` — the core file that sets up WebKit/JSC paths and configuration for local builds. The `WEBKIT_LOCAL` block needs to be rewritten to add full JSC configure + build integration.
- `cmake/targets/BuildBun.cmake` — the main Bun build target file. Needs to add `jsc` as a dependency and handle system ICU linking for local builds on Linux.
- `CONTRIBUTING.md` — the "Building WebKit locally" section documents the old multi-step process and needs to be simplified to reflect the new single-command workflow.
- `docs/project/contributing.mdx` — the docs site version of the contributing guide, which should be updated to match.

After making the cmake changes, update both `CONTRIBUTING.md` and `docs/project/contributing.mdx` to reflect the simplified build process. The old manual steps (running `jsc:build:debug`, deleting the duplicate header, separate rebuild commands) should be replaced with documentation explaining that `bun run build:local` handles everything automatically.
