# Fix: Defer dynamic import() of unknown node: modules to runtime

## Problem

When a CJS file is `require()`d, Bun's linker eagerly resolves all import records, including dynamic `import()` expressions. For unknown `node:` prefixed modules (like `node:sqlite`), the linker fails at transpile time instead of deferring to runtime.

This causes Next.js builds with Turbopack + `cacheComponents: true` + Better Auth to fail, because Kysely's dialect detection code uses `import("node:sqlite")` inside a try/catch that gracefully handles the module not being available.

Additionally, there's a use-after-poison bug in `addResolveError`: the `Location.line_text` is a slice into arena-allocated source contents, but the arena is reset before `processFetchLog` processes the error, causing a crash when `Location.clone` tries to dupe the freed memory.

## Expected Behavior

1. Dynamic `import()` of unknown `node:` modules should be deferred to runtime (like `.require` and `.require_resolve`)
2. `addResolveError` should always dupe `line_text` from the source to prevent use-after-poison
3. Code should follow the convention of using `bun.strings.*` instead of `std.mem.*` for string operations

## Files to Change

- `src/linker.zig` — Add `.dynamic` to the deferral condition in `whenModuleNotFound`
- `src/logger.zig` — Change `addResolveError` to pass `true` for dupe parameter
- `src/s3/credentials.zig` — Replace `std.mem.indexOfAny` with `strings.indexOfAny`

## Reference

- Issue: #25707
- See `src/CLAUDE.md` for Bun API conventions (use `bun.strings` over `std.mem`)
