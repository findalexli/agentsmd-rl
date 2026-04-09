# Fix(pages-router): restore Content-Length and ETag for /_next/data/ JSON responses

## Problem

Pages Router JSON data responses (`/_next/data/<buildId>/...`) are missing `Content-Length` and `ETag` headers when served from cache or after revalidation. This is a regression from v15.4.0 that breaks CDN-side compression for self-hosted deployments (e.g., CloudFront requires `Content-Length` to compress origin responses on-the-fly).

The root cause: PR #80189 introduced `Buffer.from(JSON.stringify(result.value.pageData))` when building the data response. Since `RenderResult.isDynamic` checks `typeof this.response !== 'string'`, passing a `Buffer` (not a string) caused it to return `true`, making `sendRenderResult` treat the response as a dynamic stream — skipping `Content-Length` and `ETag` generation and falling back to `Transfer-Encoding: chunked`.

## Expected Behavior

- `/_next/data/<buildId>/page.json` responses should include `Content-Length` and `ETag` headers
- HTML responses from cache should also include these headers
- The `isDynamic` check should correctly identify string responses as static

## Files to Look At

- `packages/next/src/server/route-modules/pages/pages-handler.ts` — contains the `Buffer.from()` wrappers that need to be removed (lines 529-530 and 743-744 in the original)
- `AGENTS.md` — contains documentation for `pnpm new-test` command syntax that needs updating (line 148-150)

## Changes Needed

1. In `pages-handler.ts`: Remove `Buffer.from()` wrapper when constructing `RenderResult` for:
   - JSON data responses (`/_next/data/` requests)
   - HTML from cached entries

2. In `AGENTS.md`: Update `pnpm new-test` documentation to use `-- --args` instead of just `--args`
