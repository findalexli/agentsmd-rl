# Simplify local JSC build process in build:local

## Problem

Building Bun with a local WebKit/JSC checkout currently requires a cumbersome multi-step process. Developers must manually run `bun run jsc:build:debug` to build JSC, then delete a duplicate `InspectorProtocolObjects.h` header to avoid conflicts, and only then run `bun run build:local` to build Bun itself. Incremental JSC rebuilds require yet another manual cmake command. This is error-prone and poorly documented.

## Expected Behavior

`bun run build:local` should be a single command that handles everything: configuring JSC, building JSC, and building Bun. No manual JSC build step or header deletion should be needed. Incremental rebuilds should just work when WebKit sources change.

The build system changes involve:
- `cmake/tools/SetupWebKit.cmake` — should integrate full JSC configure and build when `WEBKIT_LOCAL` is set, instead of just assuming JSC was pre-built
- `cmake/targets/BuildBun.cmake` — should add JSC as a build dependency so it builds before Bun's C++ sources, and use system ICU on Linux for local builds instead of requiring bundled static libs

After making the code changes, update the contributing documentation (`CONTRIBUTING.md` and `docs/project/contributing.mdx`) to reflect the simplified workflow. The old multi-step instructions for building WebKit locally should be replaced with the new single-command approach.

## Files to Look At

- `cmake/tools/SetupWebKit.cmake` — WebKit/JSC setup logic for local vs prebuilt builds
- `cmake/targets/BuildBun.cmake` — Bun build target linking and dependencies
- `CONTRIBUTING.md` — Developer documentation for building with local WebKit
- `docs/project/contributing.mdx` — Same docs in MDX format for the website
