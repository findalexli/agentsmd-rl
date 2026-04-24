# Fix Content-Length/ETag regression for Pages Router data responses

## Problem

In the Next.js Pages Router, `/_next/data/` JSON responses and ISR fallback HTML responses are missing `Content-Length` and `ETag` headers. This regression breaks CDN-side compression for self-hosted deployments (e.g., CloudFront requires `Content-Length` to compress origin responses).

## Expected Behavior

`/_next/data/` JSON responses and ISR fallback HTML responses should include proper `Content-Length` and `ETag` headers, just like other static responses.

## Where to Look

- `packages/next/src/server/route-modules/pages/pages-handler.ts` — the Pages Router handler; focus on how `RenderResult` is constructed for data requests and ISR fallback responses
- `AGENTS.md` — project documentation for test generation commands

## Content-Length / ETag Header Fix

The response body for Pages Router data requests and ISR fallback responses must be passed to `RenderResult` in a way that allows `Content-Length` and `ETag` headers to be generated. Inspect the `pages-handler.ts` code paths that construct `RenderResult` for:

1. The `isNextDataRequest` code path (around line 740 in the buggy code)
2. The ISR fallback path that uses `previousCacheEntry.value.html` (around line 526 in the buggy code)

For both paths, verify that the response body is in the correct form that enables header generation. Run `test_string_render_result_enables_headers` in the test suite to confirm the fix is correct.

## AGENTS.md Documentation Update

The `AGENTS.md` file documents the `pnpm new-test` command syntax in two places:

1. The **"Generate tests non-interactively"** section — verify the Format line uses the correct syntax to forward arguments to the script. The correct syntax must include a double-dash (`--`) separator: `pnpm new-test -- --args`. Check for a line starting with `Format: pnpm new-test` and verify it contains `-- --args`.

2. The **"Test Gotchas"** section — the smoke testing tip must also use the correct `pnpm new-test -- --args` syntax. Look for a line containing `Quick smoke testing` and verify it uses `-- --args` instead of just `--args`.

Both sections currently use the buggy form `pnpm new-test --args` (missing the `--` separator). These must be corrected to `pnpm new-test -- --args` in both locations.

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `eslint (JS/TS linter)`
