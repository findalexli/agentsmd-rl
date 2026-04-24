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

The error message mentions `expectedCounts.@set is not a function` (or similar for `@delete`). This occurs in the `compareBranch` function when processing array arguments. The crash prevents array comparisons from working at all.

## Constraints (from src/js/CLAUDE.md and src/js/AGENTS.md)

- Modules under `src/js/` are NOT ES modules — use `require()`, not `import`
- Use `.$call` and `.$apply`, never `.call` or `.apply`
- `require()` calls must use string literals only, not dynamic expressions
- Do not delete existing code references that appear to be working
- Do not delete functions or their core comparison logic
- The file must pass syntax validation and formatting checks