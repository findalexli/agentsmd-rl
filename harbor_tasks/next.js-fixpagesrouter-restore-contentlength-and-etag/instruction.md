# Fix(pages-router): restore Content-Length and ETag for /_next/data/ JSON responses

## Problem

Pages Router JSON data responses (`/_next/data/<buildId>/...`) are missing `Content-Length` and `ETag` headers when served from cache or after revalidation. This is a regression that breaks CDN-side compression for self-hosted deployments (e.g., CloudFront requires `Content-Length` to compress origin responses on-the-fly).

The issue relates to how `RenderResult` determines whether a response is "dynamic" (streaming) or "static" (complete). The `RenderResult.isDynamic` getter returns `true` when `typeof this.response !== 'string'`. When a `Buffer` is passed to the `RenderResult` constructor instead of a string, `isDynamic` returns `true`, which causes `sendRenderResult` in `send-payload.ts` to skip `Content-Length` and `ETag` generation and use `Transfer-Encoding: chunked` instead.

## Expected Behavior

- `/_next/data/<buildId>/page.json` responses should include `Content-Length` and `ETag` headers
- HTML responses from cache should also include these headers
- The `RenderResult.isDynamic` check should correctly identify string responses as static (not dynamic)

## Files to Look At

- `packages/next/src/server/route-modules/pages/pages-handler.ts` — handles data requests and cached HTML responses; look for `RenderResult` constructor calls related to `result.value.pageData` and `previousCacheEntry.value.html`
- `packages/next/src/server/render-result.ts` — contains the `isDynamic` getter with pattern `return typeof this.response !== 'string'`
- `packages/next/src/server/send-payload.ts` — contains `sendRenderResult` which checks `isDynamic` and uses `generateETag` for non-dynamic responses
- `AGENTS.md` — contains documentation for `pnpm new-test` command syntax that needs updating

## Required Code Patterns

When investigating `pages-handler.ts`, ensure the `RenderResult` constructor receives a string directly:
- For JSON data responses: the constructor should receive `JSON.stringify(result.value.pageData)` directly (not wrapped in `Buffer.from()`). The test verifies the pattern: `new RenderResult(JSON.stringify(result.value.pageData),` is present.
- For cached HTML: the constructor should receive `previousCacheEntry.value.html` directly (not wrapped in `Buffer.from()`). The test verifies the pattern: `new RenderResult(previousCacheEntry.value.html,` is present.

The buggy patterns to find and fix:
- `Buffer.from(JSON.stringify(result.value.pageData))` should be replaced with just `JSON.stringify(result.value.pageData)`
- `Buffer.from(previousCacheEntry.value.html)` should be replaced with just `previousCacheEntry.value.html`

## Required Documentation Update

In `AGENTS.md`, update the `pnpm new-test` command syntax documentation. The test verifies the pattern `pnpm new-test -- --args` is present. The correct syntax for non-interactive mode is:
```
pnpm new-test -- --args <appDir> <name> <type>
```

The old incorrect syntax to find and replace:
```
pnpm new-test --args true my-feature e2e
```

Should be updated to:
```
pnpm new-test -- --args true my-feature e2e
```
