# Fix Cloudflare Workers logger errors in with-cloudflare-d1 template

## Problem

The `templates/with-cloudflare-d1` template crashes in production on Cloudflare Workers with `fs.write is not implemented` errors. This happens because Payload's default logger uses `pino-pretty`, which relies on Node.js-specific APIs (`fs.write`, `worker_threads`) that are not available in the Workers runtime.

Users deploying this template to Cloudflare Workers see broken logging and potentially degraded application behavior in production.

## Expected Behavior

The template should use a custom console-based logger that works in the Cloudflare Workers environment. The logger should:
- Route logs through `console.*` methods instead of `pino-pretty`
- Output JSON-formatted log messages for Cloudflare observability
- Only be active in production (development should keep using the default logger for better DX)
- Support configurable log levels

Additionally, the `PayloadLogger` type should be exported from the main payload package so it can be reused by consumers.

## Files to Look At

- `templates/with-cloudflare-d1/src/payload.config.ts` — main Payload configuration; needs a custom logger implementation
- `packages/payload/src/index.ts` — package exports; the logger type should be available to consumers
- `templates/with-cloudflare-d1/README.md` — template documentation; should be updated to explain the logger configuration and any known workarounds for Workers-specific issues (like diagnostic channel errors from undici)
- `templates/with-cloudflare-d1/eslint.config.mjs` — ESLint configuration
- `templates/with-cloudflare-d1/package.json` — template dependencies
