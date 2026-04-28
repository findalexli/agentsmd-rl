# Bug: `assert.partialDeepStrictEqual` crashes on array inputs with TypeError

## Description

`assert.partialDeepStrictEqual` from `node:assert/strict` is a deep partial comparison function. For arrays, it verifies that the `expected` array is a subset of the `actual` array — elements in `expected` must each have a matching element in `actual`, but `actual` may contain additional elements. Duplicate elements are tracked by count: if `expected` has two `"foo"` entries, `actual` must also have at least two `"foo"` entries.

When calling `assert.partialDeepStrictEqual` with array arguments, Bun throws a `TypeError` instead of performing the comparison. The crash occurs because the implementation attempts to call methods directly on a `SafeMap` instance that has a null prototype, so those methods are not accessible.

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

Once fixed, these calls should complete without error, and the following should work correctly:

```js
// Subset check — pass (["foo"] is a subset of ["foo", "bar", "baz"])
assert.partialDeepStrictEqual(["foo", "bar", "baz"], ["foo", "baz"]);

// Duplicate handling — pass (expected has two "foo", actual has two "foo")
assert.partialDeepStrictEqual(["foo", "foo", "bar"], ["foo", "foo"]);

// Nested arrays — pass
assert.partialDeepStrictEqual([["a", "b"], ["c"]], [["a", "b"]]);

// Non-subset — should throw AssertionError
assert.throws(() => {
  assert.partialDeepStrictEqual(["foo"], ["bar"]);
});

// Expected has more of an element than actual — should throw
assert.throws(() => {
  assert.partialDeepStrictEqual(["foo"], ["foo", "foo"]);
});
```

## Error Details

The error message mentions `expectedCounts.@set is not a function` (or similar for `@delete`). This occurs in the `compareBranch` function when processing array arguments. The crash prevents all array comparisons from working.

The implementation creates an `expectedCounts` map to track element counts, then calls `.@set` and `.@delete` methods on it. The map is a `SafeMap`, which is a `Map` with its prototype set to `null`. Because `SafeMap` has no prototype, instance method calls like `.$set()` and `.$delete()` fail with `TypeError`.

The fix should ensure that `set` and `delete` operations on the `expectedCounts` map work correctly despite the null prototype.

## Constraints (from src/js/CLAUDE.md and src/js/AGENTS.md)

- Modules under `src/js/` are NOT ES modules — use `require()`, not `import`
- Use `.$call` and `.$apply`, never `.call` or `.apply`
- `require()` calls must use string literals only, not dynamic expressions
- Do not delete existing code references that appear to be working
- Do not delete functions or their core comparison logic
- The file must pass syntax validation and formatting checks (EditorConfig: UTF-8, LF endings, final newline, no trailing whitespace)
