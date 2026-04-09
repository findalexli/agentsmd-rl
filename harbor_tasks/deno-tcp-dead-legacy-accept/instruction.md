# Remove dead legacy TCP server accept path

## Problem

The `TCP` class in `ext/node/polyfills/internal_binding/tcp_wrap.ts` contains a legacy server accept code path that uses `Deno.listen()` and `Deno.Listener.accept()`. This code is unreachable — the `bind()` and `bind6()` methods always set `kUseNativeWrap = true` before `listen()` is called, so the `if (!this[kUseNativeWrap])` branch in `listen()` can never execute.

This dead code:
- Inflates the file with ~130 lines of unused methods (`#listenLegacy`, `#accept`, `#acceptBackoff`) and fields (`#listener`, `#acceptBackoffDelay`)
- Causes `tcp_wrap.ts` to appear in the Deno API violation tracker (`tools/lint_plugins/no_deno_api_in_polyfills.ts`) with 3 expected violations that are no longer needed
- Imports symbols (`delay`, `INITIAL_ACCEPT_BACKOFF_DELAY`, `MAX_ACCEPT_BACKOFF_DELAY`) that are only used by the dead path

## Expected Behavior

The dead legacy server accept path should be fully removed, including:
- The `kUseNativeWrap` guard in `listen()` and its fallback to the legacy path
- All dead private methods and fields
- The legacy close logic in `_onClose()` that references the removed `#listener`
- The `ref()`/`unref()` calls to the removed `#listener`
- Unused imports
- The lint plugin violation entry for `tcp_wrap.ts`

**Note:** The client-side connect path (`#legacyConnect`) is still needed and must NOT be removed.

## Files to Look At

- `ext/node/polyfills/internal_binding/tcp_wrap.ts` — The Node.js TCP polyfill with the dead server accept code
- `tools/lint_plugins/no_deno_api_in_polyfills.ts` — Lint plugin tracking Deno API usage violations; `tcp_wrap.ts` entry needs updating
