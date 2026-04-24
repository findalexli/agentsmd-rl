# Bug: `bun build` crashes with index out of bounds when CSS entry points are mixed with JS

## Description

When using `bun build` (or `bun build --compile`) with a mix of CSS and JavaScript/TypeScript entry points, the bundler crashes with an "index out of bounds" panic or segfault. This commonly happens when glob expansion (e.g., `./public/**/*`) includes CSS files alongside JS/TS files.

For example, this crashes:

```bash
bun build --compile ./src/index.ts ./public/assets/index.css ./src/server.worker.ts --outfile build/app
```

The crash also reproduces via the JavaScript API:

```js
await Bun.build({
  entrypoints: ["src/index.ts", "public/assets/index.css", "src/server.worker.ts"],
  outdir: "build",
});
```

## Relevant Code

The issue is in `src/bundler/linker_context/computeChunks.zig`.

The `computeChunks` function creates JS chunks for entry points and later iterates over entry point bits to assign source files to chunks. The problem is in how entry point IDs are mapped to chunk indices — when some entry points are CSS-only (no JS chunk is created for them), there's a mismatch between the entry point ID space and the JS chunk array size, leading to an out-of-bounds access in the `Handler.next` method.

Look at the `Handler` struct and its `next` method near the bottom of `computeChunks.zig`.

## The Fix

CSS-only entry points (those with no JS output) must be handled gracefully — they must not cause an out-of-bounds access when `Handler.next` tries to look up a chunk index.

The solution adds an indirection layer:

1. A u32-based mapping structure is introduced (one of: a `[]u32` slice allocated to `entry_points.len`, a `u32` array field, or a `HashMap(u32, u32)`) that stores the mapping from entry point ID to chunk index.

2. When a JS chunk is created via `js_chunks.getOrPut()`, the mapping is updated at the entry point's index.

3. In `Handler.next`, the chunk index must be obtained by looking up the entry point ID through this mapping — not by using the entry point ID directly as a chunks array index.

4. A sentinel or guard value is used to mark CSS-only entry points that have no JS chunk. When `Handler.next` encounters such a sentinel, it must return early rather than proceeding to index into the chunks array.

The `Handler.next` method must NOT use the entry point ID parameter directly as a `chunks[]` index — doing so causes the out-of-bounds crash when CSS-only entry points are present.

## Related Issues

This affects users who use glob patterns to specify entry points (e.g., `./public/**/*` which may include CSS files) and users who explicitly list CSS files as entry points alongside JS files.

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `prettier (JS/TS/JSON/Markdown formatter)`
