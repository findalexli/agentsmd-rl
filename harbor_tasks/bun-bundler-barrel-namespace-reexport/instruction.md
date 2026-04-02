# Barrel optimization drops exports through namespace re-exports

## Bug description

When the bundler's barrel optimization encounters a package with `sideEffects: false` that re-exports namespace imports, the re-exported functions are silently dropped from the bundle output.

Specifically, the pattern:

```ts
// utils/index.ts (sideEffects: false)
import * as typed from './arrays/typed/index.js';
export { typed };
```

…causes `typed.toDataView` (and any other exports from the `./arrays/typed/index.js` barrel) to be undefined at runtime in the bundled output. The problem is that when the BFS propagation in the barrel optimization reaches a re-exported namespace import like the above, it doesn't recognize that the underlying import is a star import (`import *`). Instead, it propagates to the target module with the wrong mode, causing the target barrel's own re-exports to be incorrectly deferred.

## Reproduction

Set up a workspace with:

1. A `@test/utils` package (`sideEffects: false`) that does:
   - `import * as typed from './arrays/typed/index.js'` then `export { typed }`
   - The `./arrays/typed/index.js` itself re-exports: `export { toDataView } from './misc.js'`

2. A `@test/codec` package that imports `{ typed }` from `@test/utils` and calls `typed.toDataView(data)`

3. An app entry that uses both packages

Bundle with `bun build --target bun` and run the output. `toDataView` will be `undefined`, causing a runtime error.

## Relevant files

- `src/bundler/barrel_imports.zig` — the `BarrelExportResolution` struct and the `scheduleBarrelDeferredImports` function's BFS loop
- Look at how `resolveBarrelExport` returns resolution data and how it's used during BFS queue propagation
