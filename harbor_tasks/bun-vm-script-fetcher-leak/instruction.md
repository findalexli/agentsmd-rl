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

## Technical Context

The issue is in `src/bun.js/bindings/NodeVMScriptFetcher.h`. This file contains the `NodeVMScriptFetcher` C++ class which has:

- A back-reference member (`m_owner`) storing a pointer to the owning JavaScript object
- An `owner()` getter method that returns this back-reference
- An `owner(JSC::VM&, JSC::JSValue)` setter method
- A constructor `NodeVMScriptFetcher(JSC::VM&, JSC::JSValue, JSC::JSValue)`

The class extends `JSC::ScriptFetcher`, is in the `Bun` namespace, and includes a `dynamicImportCallback()` method. Related headers in the same directory include `NodeVM.h`, `NodeVMScript.h`, and `NodeVMSourceTextModule.h`.

## Requirements

The fix must satisfy all of the following:

1. **Uncollectable root prevention**: The `m_owner` back-reference must not form a GC root that prevents the owning object from being collected. The reference type used for `m_owner` must allow the owning object to be collected when no other references remain.

2. **Owner accessor safety**: The `owner()` accessor must handle the case where the owning object has already been collected — it must return a safe JSValue fallback rather than a null or invalid reference.

3. **Owner assignment validation**: When setting the owner reference in the constructor or setter, the code must verify the value is a valid GC cell before storing it. Non-cell values should clear the stored reference rather than be stored.

4. **Header dependencies**: The implementation requires including appropriate JSC weak-reference headers to support the chosen reference type.
