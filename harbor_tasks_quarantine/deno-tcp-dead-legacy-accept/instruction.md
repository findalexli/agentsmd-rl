# Remove dead legacy TCP server accept path

## Problem

The `TCP` class in `ext/node/polyfills/internal_binding/tcp_wrap.ts` contains a legacy server accept code path that is unreachable. The `bind()` and `bind6()` methods always enable the native wrap path before `listen()` is called, so any alternative server accept logic in `listen()` can never execute.

This dead code inflates the file with unreachable server accept logic — private methods, state fields, imports, and branching logic that serve no purpose. It also causes `tcp_wrap.ts` to appear in the Deno API violation tracker (`tools/lint_plugins/no_deno_api_in_polyfills.ts`) with expected violations that should not be there, since the only Deno API usage comes from the dead code path.

## Expected Behavior

All dead legacy server accept code and its supporting infrastructure should be fully removed from `tcp_wrap.ts`. Any imports that become unused as a result should be cleaned up. The lint plugin's `EXPECTED_VIOLATIONS` should be updated to reflect that `tcp_wrap.ts` no longer has violations.

The file should retain its core structure: the `TCP` class export, the `listen()` method, and all client-side connect functionality.

**Note:** The client-side connect path is still needed and must NOT be removed.

## Files

- `ext/node/polyfills/internal_binding/tcp_wrap.ts` — The Node.js TCP polyfill with the dead server accept code
- `tools/lint_plugins/no_deno_api_in_polyfills.ts` — Lint plugin tracking Deno API usage violations
