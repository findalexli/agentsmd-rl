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

The issue is in the bundler's chunk computation logic in `src/bundler/linker_context/computeChunks.zig`.

The `computeChunks` function creates JS chunks for entry points and later iterates over entry point bits to assign source files to chunks. The problem is in how entry point IDs are mapped to chunk indices — when some entry points are CSS-only (no JS chunk is created for them), there's a mismatch between the entry point ID space and the JS chunk array size, leading to an out-of-bounds access.

Look at the `Handler` struct and its `next` method near the bottom of `computeChunks`, and how JS chunks are created for entry points in the main loop above it.

## Reproduction

Create a project with at least two JS/TS entry points and one CSS entry point, then bundle them together. The crash is deterministic when CSS entry points cause gaps in the JS chunk index space.

## Related Issues

This affects users who use glob patterns to specify entry points (e.g., `./public/**/*` which may include CSS files) and users who explicitly list CSS files as entry points alongside JS files.
