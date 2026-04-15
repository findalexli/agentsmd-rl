# Bug: `assert.partialDeepStrictEqual` crashes on array inputs with "TypeError: expectedCounts.@set is not a function"

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

## Error Details

The error message specifically mentions `expectedCounts.@set is not a function` (or similar for `@delete`). This occurs because the implementation uses a map instance with a null prototype, and direct method calls like `map.$set(key, value)` or `map.$delete(key)` fail since the methods cannot be found on the null prototype chain.

## Required Fix Pattern

In Bun's JavaScript runtime (`src/js/`), method calls on objects with null prototypes must use prototype-based invocation with Bun's `.$call` or `.$apply` intrinsics. The fix MUST:

1. Extract or use `SafeMap.prototype.set` and `SafeMap.prototype.delete` references
2. Invoke these using Bun's `.$call` or `.$apply` syntax: `SafeMap.prototype.set.$call(mapInstance, key, value)` or `SafeMap.prototype.delete.$call(mapInstance, key)`
3. You need at least 3 such prototype-based calls (for set operations, initialization, and delete operations in the counting logic)

**CRITICAL**: Use `.$call` and `.$apply`, never plain `.call` or `.apply`. For example:
- CORRECT: `SafeMap.prototype.set.$call(expectedCounts, key, value)`
- WRONG: `SafeMap.prototype.set.call(expectedCounts, key, value)`

## Expected Behavior

`assert.partialDeepStrictEqual` should work with array inputs the same way it works with object inputs, without throwing `TypeError: expectedCounts.@set is not a function`.

## Files to Investigate

- `src/js/node/assert.ts` - Look for array comparison logic and any code using `expectedCounts` with map operations

## Constraints (from src/js/CLAUDE.md)

- Modules under `src/js/` are NOT ES modules — use `require()`, not `import`
- Use `.$call` and `.$apply`, never `.call` or `.apply`
- `require()` calls must use string literals only, not dynamic expressions
