# Bug: `assert.partialDeepStrictEqual` crashes on array inputs with TypeError

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

The error message specifically mentions `expectedCounts.@set is not a function` (or similar for `@delete`). This occurs when processing array arguments. The crash prevents array comparisons from working at all.

## Affected Code

The implementation lives in `src/js/node/assert.ts` in the `compareBranch` function.

## Expected Behavior

`assert.partialDeepStrictEqual` should work with array inputs the same way it works with object inputs, without throwing `TypeError: expectedCounts.@set is not a function`.

## Constraints (from src/js/CLAUDE.md)

- Modules under `src/js/` are NOT ES modules — use `require()`, not `import`
- Use `.$call` and `.$apply`, never `.call` or `.apply`
- `require()` calls must use string literals only, not dynamic expressions
- Do not delete existing SafeMap prototype references (SafeMapPrototypeHas, SafeMapPrototypeGet)
- Do not delete the compareBranch function or its array comparison logic
- The partialDeepStrictEqual function must still exist
- The file must pass syntax validation and formatting checks