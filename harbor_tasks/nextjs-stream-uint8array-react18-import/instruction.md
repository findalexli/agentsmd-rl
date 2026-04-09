# Build fails with React 18 due to react-dom import from stream-ops

## Problem

When React 18 is installed, `next build` fails because `react-dom` gets imported transitively through the `stream-ops` module. The issue is that `streamToUint8Array` was moved into `stream-ops.node.ts` / `stream-ops.web.ts` (the platform-specific stream operations modules), which import from `react-dom`. This means any consumer of `streamToUint8Array` now transitively depends on `react-dom` through the stream-ops barrel, breaking builds with React 18 since its `react-dom` doesn't export the same API surface.

The `serialized-errors.ts` module imports `streamToUint8Array` from `stream-ops`, pulling the entire react-dom dependency chain into the dev server error handling path.

## Expected Behavior

`streamToUint8Array` should be importable without pulling in `react-dom`. It belongs in a lower-level utility module that doesn't have framework-specific dependencies.

The function needs to handle both Node.js `Readable` streams and web `ReadableStream` instances, with DCE-safe `require()` patterns for the Node.js stream module.

## Files to Look At

- `packages/next/src/server/app-render/stream-ops.ts` — barrel that re-exports platform-specific stream operations
- `packages/next/src/server/app-render/stream-ops.node.ts` — Node.js platform implementation
- `packages/next/src/server/app-render/stream-ops.web.ts` — web platform implementation
- `packages/next/src/server/dev/serialized-errors.ts` — imports and uses `streamToUint8Array`
- `packages/next/src/server/stream-utils/node-web-streams-helper.ts` — lower-level stream utilities without react-dom dependency
