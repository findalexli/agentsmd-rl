# Add `charset` to Content-Type for text-based MIME types

## Problem

The `@remix-run/mime` package can detect MIME types for file extensions, but there's no way to get a full `Content-Type` header value that includes `charset` for text-based types. For example, when serving a CSS file, the Content-Type should be `text/css; charset=utf-8`, not just `text/css`.

Currently, `createFileResponse` in `@remix-run/response` sets `Content-Type` directly from `file.type` (the raw MIME type), which means text-based responses are missing the `charset` parameter.

## Expected Behavior

1. A new `mimeTypeToContentType(mimeType)` function should convert a MIME type to a proper Content-Type header value, adding `; charset=utf-8` for text-based types:
   - All `text/*` types (except `text/xml`, which has built-in encoding declarations via `<?xml encoding="..."?>`)
   - `application/json` and `application/javascript`
   - All `+json` suffixed types (e.g., `application/ld+json`)
   - Binary types and types that already include `charset` should be returned unchanged

2. A new `detectContentType(extension)` function should combine MIME type detection with the charset logic — like `detectMimeType` but returning a full Content-Type value.

3. Both functions should be exported from `@remix-run/mime`.

4. `createFileResponse` in `@remix-run/response` should use the new conversion function so that served files automatically get proper charset headers.

## Files to Look At

- `packages/mime/src/lib/` — where MIME utility functions live
- `packages/mime/src/index.ts` — package exports
- `packages/response/src/lib/file.ts` — uses MIME types for file responses

After implementing the code changes, update the relevant package documentation to reflect the new API surface. The `@remix-run/mime` package README should document the new functions so users know they exist and how to use them.
