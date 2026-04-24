# Edge runtime deployment fails due to node:stream imports

## Problem

When deploying a Next.js application using the edge runtime, the deployment crashes because server-side code unconditionally calls `require('node:stream')`. This Node.js built-in module is unavailable in the edge runtime, and the require executes at import time regardless of the runtime environment.

The affected code paths include stream conversion utilities, the pre-rendering tee operation, and render result stream handling.

## Expected Behavior

### Edge runtime guards with DCE-safe structure

All code paths that import `node:stream` must check whether the runtime is edge before executing the require. Specifically:

1. Use `process.env.NEXT_RUNTIME === 'edge'` to detect the edge runtime
2. Place the `require('node:stream')` call inside an `else` branch (the require must be preceded by a `} else {` block) so that webpack's dead code elimination removes the require from edge bundles entirely

In the edge branch, the behavior depends on the operation:
- Functions that fundamentally depend on Node.js streams must **throw** an error explaining the incompatibility
- Functions that can operate with web streams only must delegate to the existing `webstreamToUint8Array()` function instead of requiring `node:stream`

### Error codes

The project's error registry `packages/next/errors.json` uses a JSON schema that maps numeric string keys to error message strings: `{ "<code>": "<message>", ... }`. It must be updated with edge-runtime-specific error messages:

- At least **3** error messages containing the text "edge runtime"
- At least **1** of those must mention `Readable`, `stream`, or `webToReadable`

New error codes should follow the existing sequential numbering pattern.

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `prettier (JS/TS/JSON/Markdown formatter)`
