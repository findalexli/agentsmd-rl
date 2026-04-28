# Fix(pages-router): restore Content-Length and ETag for /_next/data/ JSON responses

## Problem

Pages Router JSON data responses (`/_next/data/<buildId>/...`) are missing `Content-Length` and `ETag` headers when served from cache or after revalidation. This is a regression that breaks CDN-side compression for self-hosted deployments (e.g., CloudFront requires `Content-Length` to compress origin responses on-the-fly).

The issue relates to how `RenderResult` determines whether a response is "dynamic" (streaming) or "static" (complete). The `RenderResult.isDynamic` getter (in `packages/next/src/server/render-result.ts`) returns `true` when `typeof this.response !== 'string'`. When a non-string value is passed to the `RenderResult` constructor, `isDynamic` returns `true`, which causes `sendRenderResult` in `send-payload.ts` to skip `Content-Length` and `ETag` generation (via `generateETag`) and use `Transfer-Encoding: chunked` instead.

## Expected Behavior

- `/_next/data/<buildId>/page.json` responses should include `Content-Length` and `ETag` headers
- HTML responses from cache should also include these headers
- `RenderResult` constructor should receive plain string values so that `typeof this.response !== 'string'` evaluates to `false` and `sendRenderResult` can properly generate response headers

## Files to Examine

- `packages/next/src/server/route-modules/pages/pages-handler.ts` — exports `export const getHandler` and uses `isNextDataRequest` to identify data requests. Constructs `RenderResult` objects for data and cached HTML responses. Look at how `result.value.pageData` and `previousCacheEntry.value.html` are passed to `new RenderResult(` calls. The correct construction pattern for JSON data should be `new RenderResult(JSON.stringify(result.value.pageData),` and for cached HTML should be `new RenderResult(previousCacheEntry.value.html,`. Values should not be wrapped in `Buffer.from` before being passed to the constructor.
- `packages/next/src/server/render-result.ts` — defines `export default class RenderResult` with `toUnchunkedString` method and `isDynamic` getter that checks `typeof this.response !== 'string'`
- `packages/next/src/server/send-payload.ts` — `sendRenderResult` function that checks `isDynamic` and calls `generateETag`
- `AGENTS.md` — project documentation, including `pnpm new-test` command usage

## AGENTS.md Updates

The `AGENTS.md` file documents the `pnpm new-test` command. The documentation should use the correct syntax `pnpm new-test -- --args` (with the `--` separator between `new-test` and `--args`). The incorrect syntax `pnpm new-test --args true my-feature e2e` (missing the double-dash separator) should not be present.

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `prettier (JS/TS/JSON/Markdown formatter)`
- `eslint (JS/TS linter)`
