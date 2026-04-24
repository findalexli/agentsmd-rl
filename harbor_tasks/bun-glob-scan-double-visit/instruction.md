# Bun.Glob.scan() visits directories twice

## Bug Description

When `Bun.Glob.scan()` processes patterns containing `**/X/...` (e.g., `**/node_modules/**/*.js`), directories under the `**/X` boundary are visited twice, causing duplicate entries in results and redundant syscalls.

Running `bun scripts/glob-sources.mjs` (which exercises the Glob API on thousands of source files) produces output containing the literal strings `Globbed` and `sources`. If directories are visited twice, these counts will be inflated or the scan will behave incorrectly.

## Constraints

- The fix must allow the glob walker to evaluate multiple pending pattern states simultaneously so that no directory is opened more than once per entry
- All matches found by the original code must still be found
- The solution must handle patterns with many components (arbitrary depth, 130+ components)
- Code must use `bun.*` APIs instead of `std.*` equivalents
- No `@import()` inside functions
- Memory allocations must use proper cleanup with `defer`
- New code must use `bun.handleOom()` not `catch bun.outOfMemory()`

## Relevant Files

- `src/glob/GlobWalker.zig` — glob walker implementation; contains the `WorkItem` struct that tracks traversal state
- `src/collections/bit_set.zig` — bit set utilities (AutoBitSet type)

## Verification

- `bun scripts/glob-sources.mjs` — exercises the Glob API; output must contain `Globbed` and `sources`
- `bun ./test/internal/ban-words.test.ts` — validates code quality rules
- `bunx tsc --noEmit` — validates TypeScript correctness
- Other repository CI checks (package-json-lint, int_from_float, sort-imports)