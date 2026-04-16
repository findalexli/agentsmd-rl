# Simplify local JSC build process in build:local

## Problem

Building Bun with a local WebKit/JSC checkout currently requires a cumbersome multi-step process. Developers must manually run a JSC build command, then delete a duplicate header file to avoid conflicts, and only then build Bun itself. Incremental JSC rebuilds require yet another manual command. This is error-prone and poorly documented.

## Expected Behavior

`bun run build:local` should be a single command that handles everything: configuring JSC, building JSC, and building Bun. No manual JSC build step or header deletion should be needed. Incremental rebuilds should just work when WebKit sources change.

The build system needs to be extended to support local WebKit/JSC builds:

### CMake Requirements

When using a local WebKit checkout, the cmake setup must integrate full JSC configuration and building. Specifically:
- cmake configuration for local WebKit must include arguments appropriate for JSC-only builds
- The build type for WebKit must be configurable via a cmake option
- cmake must create a jsc build target
- When building Bun with local WebKit on Linux, ICU must be resolved via the system package finder

### Documentation Requirements

After making the code changes, update the contributing documentation (`CONTRIBUTING.md` and `docs/project/contributing.mdx`) to reflect the simplified workflow. The documentation must:
- Explain that `build:local` handles JSC configuration and building
- Mention incremental JSC rebuilds
- Remove all references to the old manual JSC build command (`jsc:build:debug`)
- Remove all references to manual header deletion (`InspectorProtocolObjects.h`)

## Files to Look At

- `cmake/tools/SetupWebKit.cmake` — WebKit/JSC setup logic for local vs prebuilt builds
- `cmake/targets/BuildBun.cmake` — Bun build target linking and dependencies
- `CONTRIBUTING.md` — Developer documentation for building with local WebKit
- `docs/project/contributing.mdx` — Same docs in MDX format for the website