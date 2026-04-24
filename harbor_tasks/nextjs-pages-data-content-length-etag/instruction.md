# Bug: Pages Router /_next/data/ responses missing Content-Length and ETag headers

## Context

In the Next.js Pages Router, when serving `/_next/data/<buildId>/...json` responses (the JSON data requests used by client-side navigation), the response headers are missing `Content-Length` and `ETag`. Instead, the response uses `Transfer-Encoding: chunked`.

This is a regression — these headers were present in earlier versions. The issue breaks CDN-side compression for self-hosted deployments (e.g., CloudFront requires `Content-Length` to compress origin responses on-the-fly).

## Key files

The relevant code paths span these files in the Next.js server:

- `packages/next/src/server/route-modules/pages/pages-handler.ts` — the pages route handler that constructs responses for `/_next/data/` requests and handles ISR fallback. Uses `CachedRouteKind.PAGES` for cached route entries and the `generateEtags` config flag.
- `packages/next/src/server/send-payload.ts` — responsible for sending responses with header generation, including `Content-Length`, `ETag`, and `generateETag` for ETag computation.
- `packages/next/src/server/render-result.ts` — the `RenderResult` class used to represent response payloads.

## Reproduction

1. Create a Next.js app with `getStaticProps` returning data
2. Build and start the production server
3. Request `/_next/data/<buildId>/index.json`
4. Observe: no `Content-Length` header, no `ETag` header, response uses `Transfer-Encoding: chunked`

The same issue also affects the ISR fallback code path where a cached HTML entry is reconstructed and served.

## Expected behavior

`/_next/data/` JSON responses and ISR fallback HTML responses should include `Content-Length` and `ETag` headers, matching the behavior of earlier versions. The responses should not use chunked transfer encoding for these static/known-length payloads.

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `prettier (JS/TS/JSON/Markdown formatter)`
