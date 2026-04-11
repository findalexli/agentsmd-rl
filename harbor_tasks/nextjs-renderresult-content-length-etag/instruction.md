# Fix Pages Router Content-Length and ETag Headers

## Problem

Pages Router JSON responses at `/_next/data/<BUILD_ID>/...` are missing `Content-Length` and `ETag` headers. This breaks CDN-side compression (e.g., CloudFront requires `Content-Length` to compress responses on-the-fly).

The issue is in `packages/next/src/server/route-modules/pages/pages-handler.ts`. When constructing `RenderResult` for data requests, the code wraps the response with `Buffer.from()`:

```typescript
new RenderResult(Buffer.from(JSON.stringify(result.value.pageData)), ...)
```

Since `RenderResult.isDynamic` checks `typeof this.response !== 'string'`, passing a `Buffer` causes it to return `true`, making `sendRenderResult` treat the response as a dynamic stream and skip `Content-Length` and `ETag` generation.

## Expected Behavior

- Data requests (`/_next/data/`) should return with `Content-Length` and `ETag` headers
- `RenderResult` should receive the JSON string directly, not wrapped in `Buffer.from()`
- Similar issue exists for cached HTML responses - also remove `Buffer.from()` there

## Files to Look At

- `packages/next/src/server/route-modules/pages/pages-handler.ts` — Pages Router request handler with the Buffer.from bug

## Additional Task: Update AGENTS.md

This PR also includes a documentation fix in `AGENTS.md`. The `pnpm new-test` command syntax needs updating:

The command for non-interactive test generation needs a separator (`--`) before the `--args` flag. Review and update the `pnpm new-test` examples in `AGENTS.md` to use the correct syntax.

**What to look for in AGENTS.md:**
- Find any instances of `pnpm new-test --args ...` (without the `--` separator)
- Update them to use `pnpm new-test -- --args ...` (with the separator)
- This applies to all examples showing the non-interactive test generation pattern

## Summary

1. Fix the code: Remove `Buffer.from()` wrappers when constructing `RenderResult` for data requests and cached HTML
2. Fix the docs: Update `pnpm new-test` command syntax in `AGENTS.md` to use `-- --args`
