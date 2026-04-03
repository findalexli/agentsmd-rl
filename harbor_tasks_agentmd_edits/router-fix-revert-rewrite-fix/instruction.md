# Router URL Rewrite Causes Infinite Redirect Loops with i18n

## Problem

The router's `parseLocation` method computes `publicHref` by applying the output rewrite function. This causes infinite redirect loops when using i18n locale prefix rewriting (e.g., Paraglide). The server-side redirect check sees a mismatch between `publicHref` (output-rewritten) and what `buildLocation` computes, and triggers an endless redirect cycle.

Additionally, the i18n Paraglide example's `server.ts` incorrectly destructures and passes the middleware-transformed `request` to the TanStack Start handler instead of the original request. This compounds the URL rewriting issues.

## Expected Behavior

- `publicHref` in `parseLocation` should reflect the original URL as received from history, not a rewritten version. The output rewrite computation for `publicHref` should be removed — it was an incorrect approach to fixing URL consistency.
- The Paraglide middleware callback in `server.ts` should pass the original request to the handler, not the middleware-modified one.
- The example README documentation should be updated to reflect the correct `server.ts` middleware usage pattern. Any stale external links in the i18n example READMEs should also be cleaned up.

## Files to Look At

- `packages/router-core/src/router.ts` — the `parseLocation` method's `parse` function computes `publicHref` incorrectly via output rewrite
- `e2e/react-start/i18n-paraglide/src/server.ts` — middleware callback passes wrong request object
- `examples/react/start-i18n-paraglide/README.md` — documents the server.ts middleware pattern (needs updating)
- `examples/solid/start-i18n-paraglide/README.md` — same middleware documentation for Solid
- `examples/react/i18n-paraglide/README.md` — contains stale external link
- `examples/solid/i18n-paraglide/README.md` — contains stale external link
