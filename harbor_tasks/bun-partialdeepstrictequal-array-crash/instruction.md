# Bug: `assert.partialDeepStrictEqual` crashes on array inputs

## Description

When calling `assert.partialDeepStrictEqual` from `node:assert/strict` with array arguments, Bun throws a `TypeError` instead of performing the comparison.

## Reproduction

```js
import assert from "node:assert/strict";
assert.partialDeepStrictEqual(["foo"], ["foo"]);
// TypeError: expectedCounts.@set is not a function
```

The same crash happens for any array inputs:

```js
assert.partialDeepStrictEqual(["foo", "bar", "baz"], ["foo", "baz"]);
// TypeError: expectedCounts.@set is not a function
```

## Root Cause

The issue is in `src/js/node/assert.ts`, in the `compareBranch` function. The array comparison branch uses a `SafeMap` instance to count expected elements. However, `SafeMap` instances have their prototype set to `null` by `makeSafe()`, which breaks the resolution of certain private methods on the map instance. The code calls methods directly on the map instance, but since the prototype chain has been severed, those method lookups fail at runtime.

The existing code already handles this correctly for some `SafeMap` operations (like `has` and `get`) by extracting uncurried prototype references and calling them explicitly. The array branch is missing the same treatment for two other `SafeMap` methods that it uses.

## Expected Behavior

`assert.partialDeepStrictEqual` should work with array inputs the same way it works with object inputs, without throwing.

## Files to Investigate

- `src/js/node/assert.ts` — the `compareBranch` function, specifically the array handling branch around the `expectedCounts` map usage
