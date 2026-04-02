# Bug: Pages Router /_next/data/ responses missing Content-Length and ETag headers

## Context

In the Next.js Pages Router, when serving `/_next/data/<buildId>/...json` responses (the JSON data requests used by client-side navigation), the response headers are missing `Content-Length` and `ETag`. Instead, the response uses `Transfer-Encoding: chunked`.

This is a regression — these headers were present in earlier versions. The issue breaks CDN-side compression for self-hosted deployments (e.g., CloudFront requires `Content-Length` to compress origin responses on-the-fly).

## Where to look

The data response is constructed in:
- `packages/next/src/server/route-modules/pages/pages-handler.ts`

The response is sent via `sendRenderResult()` in:
- `packages/next/src/server/send-payload.ts`

The key mechanism: `sendRenderResult` checks `result.isDynamic` — when the response is considered "dynamic", it skips setting `Content-Length` and `ETag` and falls back to streaming/chunked transfer encoding.

The `RenderResult` class determines whether a response is dynamic based on the type of its internal response value.

## Reproduction

1. Create a Next.js app with `getStaticProps` returning data
2. Build and start the production server
3. Request `/_next/data/<buildId>/index.json`
4. Observe: no `Content-Length` header, no `ETag` header, response uses `Transfer-Encoding: chunked`

The same issue also affects the ISR fallback code path where a cached HTML entry is reconstructed.

## Expected behavior

`/_next/data/` JSON responses (and ISR fallback HTML responses) should include `Content-Length` and `ETag` headers, matching the behavior of earlier versions.
