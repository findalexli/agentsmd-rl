# Bun.Glob.scan() visits directories twice at `**/X` boundaries

## Bug Description

When `Bun.Glob.scan()` processes patterns containing `**/X/...` (e.g., `**/node_modules/**/*.js`), directories under the `**/X` boundary are being opened and read twice. This causes redundant `openat + readdir + close` syscalls, and since the traversal recurses, every descendant of the boundary directory is visited twice.

## How to Reproduce

Use a glob pattern like `**/node_modules/**/*.js` on a large directory tree (e.g., a Next.js project). Observe that the scan takes roughly 2x longer than it should, and tracing reveals duplicate `readdir` calls for the same directories.

The issue is in `src/glob/GlobWalker.zig`. When the walker is at a `**` component (say index 0) and encounters a directory that matches the next literal component (say `node_modules` at index 1), there are two valid NFA interpretations:

1. **Advance**: `node_modules` matches — jump past it to index 2 and continue matching
2. **Keep going**: `**` matches zero or more dirs — stay at index 0 in case there's a deeper match

The current implementation handles this by pushing **two separate `WorkItem`s** for the same directory path — one at the original index and one at the advanced index. Each `WorkItem` triggers its own `openat + readdir + close` cycle, and since both recurse, the entire subtree under that boundary gets walked twice.

## Relevant Files

- `src/glob/GlobWalker.zig` — The `WorkItem` struct, the directory iteration loop, and the `matchPatternDir` function that decides how to handle `**/X` boundaries
- `src/collections/bit_set.zig` — Bit set utilities that may be relevant for tracking multiple states

## Expected Behavior

Each directory should be opened and read exactly once, regardless of how many NFA states are active at that point in the traversal. The standard approach is to carry a **set** of active component indices per work item, so that when a boundary is crossed, both indices are tracked together and the directory is iterated only once.

## Constraints

- Correctness must be preserved: all matches found by the old code must still be found
- Patterns without `**/X` boundaries (e.g., `**/*.ts`) should be unaffected
- The solution should handle arbitrarily deep patterns (130+ components)
