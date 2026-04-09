# Fix Content-Length/ETag regression for Pages Router data responses

## Problem

In the Next.js Pages Router, `/_next/data/` JSON responses (and ISR fallback HTML responses) are missing `Content-Length` and `ETag` headers. This is a regression introduced in v15.4.0 that breaks CDN-side compression for self-hosted deployments (e.g., CloudFront requires `Content-Length` to compress origin responses).

The root cause is in the pages handler: the response body for data requests and cached HTML is being wrapped in a `Buffer` before being passed to `RenderResult`. Since `RenderResult.isDynamic` checks `typeof this.response !== 'string'`, a `Buffer` input causes it to be treated as a dynamic stream, which skips `Content-Length` and `ETag` generation and falls back to `Transfer-Encoding: chunked`.

## Expected Behavior

`/_next/data/` JSON responses and ISR fallback HTML responses should include proper `Content-Length` and `ETag` headers, just like other static responses. The response body should be passed as a plain string to `RenderResult`, not wrapped in `Buffer.from()`.

## Files to Look At

- `packages/next/src/server/route-modules/pages/pages-handler.ts` — the handler constructs `RenderResult` for both data requests and cached HTML; look at how the response body is constructed for `isNextDataRequest` and the ISR fallback path

## Documentation Update

After fixing the code, update the project's `AGENTS.md` to correct the `pnpm new-test` command syntax. The current documentation shows an incorrect invocation format that doesn't properly forward arguments to the underlying script. Check both the "Generate tests non-interactively" section and the "Test Gotchas" section for the smoke testing tip.
