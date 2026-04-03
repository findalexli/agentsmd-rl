# Fix Cloudflare Workers Logger Errors in D1 Template

## Problem

The `templates/with-cloudflare-d1` template crashes at runtime when deployed to Cloudflare Workers. Payload's default logger uses `pino-pretty`, which relies on Node.js-specific APIs (like `fs.write`) that are not available in the Workers runtime. This causes `fs.write is not implemented` errors whenever the application tries to log anything.

Additionally, developers see "Failed to publish diagnostic channel message" errors in their Cloudflare observability logs, caused by the `undici` HTTP client library used internally for file uploads.

## Expected Behavior

- The template should run without logger-related errors on Cloudflare Workers in production
- In development mode, the default `pino-pretty` logger should still be used for better DX
- The logger should produce structured (JSON) output compatible with Cloudflare's observability tools
- The `PayloadLogger` type should be exported from `packages/payload/src/index.ts` so downstream consumers can type their custom loggers
- The template's README should document the custom logger setup and the diagnostic channel error workaround, so future developers understand the configuration

## Files to Look At

- `templates/with-cloudflare-d1/src/payload.config.ts` — the Payload config where the custom logger needs to be added
- `packages/payload/src/index.ts` — the main package exports, where `PayloadLogger` type should be exported
- `templates/with-cloudflare-d1/README.md` — template documentation that should be updated to explain the logger configuration and diagnostic channel errors
