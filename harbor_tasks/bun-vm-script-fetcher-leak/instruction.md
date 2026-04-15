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

## Implementation Requirements

The fix must satisfy all of the following requirements:

1. **Header includes**: The solution must include the JavaScriptCore weak reference headers:
   - `#include <JavaScriptCore/Weak.h>`
   - `#include <JavaScriptCore/WeakInlines.h>`

2. **Owner reference type**: The member field storing the back-reference to the owner must use `Weak<SomeType>` instead of `Strong<SomeType>` to avoid creating a GC root that prevents collection.

3. **Owner getter null check**: The `owner()` accessor must check whether the weak reference is still alive before returning it. If the referenced object has been collected, the getter must return a safe fallback value using one of:
   - `jsUndefined()`
   - `jsNull()`
   - `JSValue()` (empty/undefined JSValue)

4. **Owner setter guards**: When setting the owner via setter method or constructor, the code must verify the value is a valid GC cell before creating the weak reference. Use `isCell()` or `isObject()` checks on the `JSValue` before assignment to `Weak<>`.

5. **Regression test**: Add a test that verifies `vm.Script`, `vm.compileFunction`, and `vm.SourceTextModule` objects are properly garbage-collected when no longer referenced.

## Where to look

The leak is in the Bun JavaScriptCore bindings related to script fetching. Look for classes that extend `JSC::ScriptFetcher` and hold back-references to script/function/module wrapper objects. The problematic code creates uncollectable reference cycles between the fetcher and its owner.
