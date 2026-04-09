# Turbopack: createRequire(new URL) not resolving correctly

## Problem

Turbopack fails to resolve CommonJS modules when `createRequire` is called with a `new URL(...)` constructor pattern. When code uses:

```js
const require = createRequire(new URL('./sub/', import.meta.url))
const foo = require('./foo.js')
```

Turbopack emits a `Module not found: Can't resolve './sub/'` error. It incorrectly treats the URL-relative path as a module specifier rather than as a base directory for subsequent require() calls.

The simpler `createRequire(import.meta.url)` pattern works fine — only the `new URL(...)` variant is broken.

## Expected Behavior

Turbopack should resolve `require()` calls made through a `createRequire(new URL(relativePath, import.meta.url))` factory relative to the URL path, not the current module. This matches `@vercel/nft` behavior and Node.js semantics.

## Files to Look At

- `turbopack/crates/turbopack-ecmascript/src/analyzer/mod.rs` — the `WellKnownFunctionKind` enum and `value_visitor_inner` function which classifies JS expressions
- `turbopack/crates/turbopack-ecmascript/src/references/mod.rs` — the reference analysis that resolves require() calls to actual module paths
- `turbopack/crates/turbopack-tracing/tests/unit.rs` — node-file-trace test cases that were previously disabled due to this limitation
