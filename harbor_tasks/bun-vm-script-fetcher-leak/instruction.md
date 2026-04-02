# Memory leak in `node:vm` APIs

## Bug Description

Every call to `vm.Script`, `vm.SourceTextModule`, and `vm.compileFunction` leaks the resulting JavaScript object. The objects are never garbage-collected, regardless of whether user code retains any reference to them.

## Reproduction

```js
const vm = require("node:vm");
const { heapStats } = require("bun:jsc");

const before = heapStats().objectTypeCounts.Script || 0;

for (let i = 0; i < 500; i++) {
  new vm.Script("1 + 1");
}

Bun.gc(true);
Bun.gc(true);

const after = heapStats().objectTypeCounts.Script || 0;
console.log(`Leaked Script objects: ${after - before}`);
// Expected: ~0 (objects should be GC'd)
// Actual: +500 (100% leak rate)
```

The same leak occurs with `vm.compileFunction("return 1")` (leaks `FunctionExecutable` objects) and `new vm.SourceTextModule("export const a = 1;")` (leaks `NodeVMSourceTextModule` objects).

## Where to look

The issue is in `src/bun.js/bindings/NodeVMScriptFetcher.h`. The `NodeVMScriptFetcher` class holds a back-reference to the owning script/function/module wrapper. This back-reference creates an uncollectable reference cycle:

```
Script (JSCell)
  -> m_source (SourceCode)
  -> SourceProvider
  -> SourceOrigin
  -> RefPtr<NodeVMScriptFetcher>
  -> back-reference to owner  <-- GC root, prevents collection
  -> Script (cycle!)
```

The back-reference is keeping the owner alive as a GC root, but the owner simultaneously keeps the fetcher alive through the source code chain. Neither can ever be freed.

## Requirements

1. Break the reference cycle so that `vm.Script`, `vm.SourceTextModule`, and `vm.compileFunction` results are properly garbage-collected when no user code retains a reference.
2. The `owner()` accessor must still return the correct value when the owner is reachable (e.g., during `import()` inside a running script).
3. If the owner has already been collected, `owner()` should return a safe fallback value.
4. Add a regression test that verifies the leak is fixed for `vm.Script`, `vm.compileFunction`, and `vm.SourceTextModule`.
