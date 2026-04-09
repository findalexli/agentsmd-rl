# Edge runtime deployment fails due to node:stream imports

## Problem

When deploying a Next.js application that uses the edge runtime, the deployment fails because several server-side code paths unconditionally try to import `node:stream`, which is not available in the edge runtime environment. The affected code paths include stream conversion utilities, the pre-render tee operation, and render result stream handling.

The root cause is that `require('node:stream')` calls are executed regardless of the runtime environment, so even when running in edge mode (where Node.js built-in modules are unavailable), the code attempts to load `node:stream` and crashes.

## Expected Behavior

Code that uses `node:stream` should detect when it is running in the edge runtime and either:
- Throw a clear error explaining the operation is not supported in edge runtime
- Fall back to web stream APIs that are available in edge runtime

The `require('node:stream')` calls should be structured so that webpack's dead code elimination (DCE) can remove them from edge bundles entirely.

## Files to Look At

- `packages/next/src/server/stream-utils/node-web-streams-helper.ts` — Contains `webToReadable()` and `streamToUint8Array()` which convert between web and node streams
- `packages/next/src/server/app-render/app-render-prerender-utils.ts` — Contains `ReactServerResult` class with a `tee()` method that uses `node:stream`
- `packages/next/src/server/render-result.ts` — Contains `RenderResult` class with `toReadableStream()` and `tee()` methods that use `node:stream`
- `packages/next/errors.json` — Error message registry
