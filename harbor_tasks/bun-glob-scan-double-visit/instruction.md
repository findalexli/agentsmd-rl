# Bun.Glob.scan() visits directories twice at `**/X` boundaries

## Bug Description

When `Bun.Glob.scan()` processes patterns containing `**/X/...` (e.g., `**/node_modules/**/*.js`), directories under the `**/X` boundary are being opened and read twice. This causes redundant `openat + readdir + close` syscalls, and since the traversal recurses, every descendant of the boundary directory is visited twice.

## How to Reproduce

Use a glob pattern like `**/node_modules/**/*.js` on a large directory tree (e.g., a Next.js project). Observe that the scan takes roughly 2x longer than it should, and tracing reveals duplicate `readdir` calls for the same directories.

At `**/X` boundaries in the NFA traversal, there are two valid ways to interpret a matching directory: advancing past `X` to continue matching, or keeping the outer `**` alive in case there's a deeper match. The current implementation's handling of this ambiguity causes the same directory to be queued for processing twice, resulting in duplicate filesystem operations.

## Expected Behavior

Each directory should be opened and read exactly once, regardless of how many NFA states are active at that point in the traversal. The scan should complete in time proportional to the number of files and directories, not in time proportional to the number of active NFA states.

## Constraints

- Correctness must be preserved: all matches found by the original code must still be found
- Patterns without `**/X` boundaries (e.g., `**/*.ts`) should be unaffected
- The solution should handle arbitrarily deep patterns (130+ components)

## Relevant Files

- `src/glob/GlobWalker.zig` — The glob walker implementation
- `src/collections/bit_set.zig` — Bit set utilities used by the walker
