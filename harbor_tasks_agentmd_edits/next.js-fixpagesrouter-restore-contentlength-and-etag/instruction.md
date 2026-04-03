# Fix Pages Router: restore Content-Length and ETag for /_next/data/ JSON responses

## Problem

Since v15.4.0, `/_next/data/<buildId>/*.json` responses from the Pages Router are missing `Content-Length` and `ETag` headers. Instead, the server sends `Transfer-Encoding: chunked`. This breaks CDN-side compression for self-hosted deployments — for example, CloudFront requires `Content-Length` to compress origin responses on-the-fly.

The root cause is in the Pages Router handler: when constructing `RenderResult` for the JSON data response, the value is wrapped with `Buffer.from()`. Because `RenderResult.isDynamic` checks `typeof this.response !== 'string'`, passing a `Buffer` (not a `string`) causes the response to be treated as a dynamic stream, which skips `Content-Length` and `ETag` generation in `sendRenderResult`.

The same wrapping issue also affects the ISR fallback code path in the same file.

## Expected Behavior

`/_next/data/` JSON responses should include `Content-Length` and `ETag` headers, as they did before the regression. The `RenderResult` constructor should receive a `string`, not a `Buffer`.

## Also

The project's `AGENTS.md` documents a `pnpm new-test` command for non-interactive test generation, but the documented syntax is incorrect — it's missing the `--` separator needed to forward arguments through pnpm. All instances of this command in AGENTS.md should be corrected.

## Files to Look At

- `packages/next/src/server/route-modules/pages/pages-handler.ts` — Pages Router request handler, constructs `RenderResult` for data responses
- `AGENTS.md` — Agent development guide with test generation commands
