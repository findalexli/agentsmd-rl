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

## Requirements

The fix must satisfy all of the following:

1. **Uncollectable root prevention**: The owner back-reference must not form a GC root that prevents the owning object from being collected.

2. **Owner accessor safety**: The `owner()` accessor must handle the case where the owning object has already been collected — it must return a safe fallback value rather than a null or invalid reference.

3. **Owner assignment validation**: When setting the owner reference, the code must verify the value is a valid GC cell before storing it.

4. **Regression test**: Add a test that verifies `vm.Script`, `vm.compileFunction`, and `vm.SourceTextModule` objects are properly garbage-collected when no longer referenced.