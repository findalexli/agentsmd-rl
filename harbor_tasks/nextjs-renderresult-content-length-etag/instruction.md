# Fix Pages Router Content-Length and ETag Headers

## Problem

Pages Router JSON responses at `/_next/data/<BUILD_ID>/...` are missing `Content-Length` and `ETag` headers. This breaks CDN-side compression (e.g., CloudFront requires `Content-Length` to compress responses on-the-fly).

When `RenderResult` is constructed with certain data types, the `isDynamic` getter may incorrectly return `true`, causing `sendRenderResult` to skip `Content-Length` and `ETag` generation even for cacheable responses.

## Expected Behavior

- Data requests (`/_next/data/`) should return with `Content-Length` and `ETag` headers
- Cached HTML responses should also include these headers
- The response type passed to `RenderResult` must be compatible with static/bufferable handling

## Files to Examine

- `packages/next/src/server/route-modules/pages/pages-handler.ts` — Pages Router request handler
- `packages/next/src/server/render-result.ts` — `RenderResult` class definition

## Additional Task: Update AGENTS.md

The `AGENTS.md` file in the repository root contains examples of the `pnpm new-test` command. Some of these examples show incorrect syntax for the non-interactive test generation pattern.

**What to look for in AGENTS.md:**
- Find any instances of `pnpm new-test --args` (without the `--` separator before `--args`)
- Update them to use `pnpm new-test -- --args` (with the `--` separator)
- This applies to all examples showing the non-interactive test generation pattern

## Summary

1. Fix the code: Ensure `RenderResult` is constructed with a type that does not trigger dynamic handling for data requests and cached HTML
2. Fix the docs: Update `pnpm new-test` command syntax in `AGENTS.md` to use `-- --args` before any arguments