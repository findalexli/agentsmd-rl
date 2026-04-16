# Bun.Glob.scan() visits directories twice

## Bug Description

When `Bun.Glob.scan()` processes patterns containing `**/X/...` (e.g., `**/node_modules/**/*.js`), directories under the `**/X` boundary are being opened and read twice. This causes redundant `openat + readdir + close` syscalls, and since the traversal recurses, every descendant of the boundary directory is visited twice.

## Expected Fix

The walker must be able to track multiple active states when processing a directory, so that a single `readdir` call evaluates all pending pattern states instead of re-opening the directory for each state.

## Constraints

- Correctness must be preserved: all matches found by the original code must still be found
- Patterns without `**/X` boundaries (e.g., `**/*.ts`) should be unaffected
- The solution should handle arbitrarily deep patterns (130+ components)
- Code must use `bun.*` APIs instead of `std.*` equivalents
- No `@import()` inside functions
- Memory allocations must use proper cleanup with `defer`
- New code must use `bun.handleOom()` not `catch bun.outOfMemory()`

## Relevant Files

- `src/glob/GlobWalker.zig` — glob walker implementation
- `src/collections/bit_set.zig` — bit set utilities

## Verification

The existing repository tests serve as behavioral verification:
- `bun scripts/glob-sources.mjs` — exercises the Glob API scanning thousands of source files; output contains "Globbed" and "sources"
- `bun ./test/internal/ban-words.test.ts` — validates code quality rules
- `bunx tsc --noEmit` — validates TypeScript correctness
- Other repository CI checks (package-json-lint, int_from_float, sort-imports)