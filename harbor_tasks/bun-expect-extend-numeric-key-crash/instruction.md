# Bug: `expect.extend` crashes with numeric index keys

## Summary

Calling `expect.extend()` with an object that has numeric keys representing valid array indices causes a crash in Bun's test runner. The crash manifests as an assertion failure in `JSObjectInlines.h` around line 451.

## Reproduction

```js
const v1 = { 1073741820: Request };
Bun.jest().expect.extend(v1);
```

Running this code crashes the process instead of extending the expect object with the custom matcher.

## Requirements

The fix must ensure that custom matchers can be registered even when the input object contains numeric keys like `1073741820`. The solution must satisfy all of the following:

1. **All three registration targets must be handled**: `expect_proto`, `expect_constructor`, and `expect_static_proto`

2. **Safe property-setting methods**: Use one of these approaches on all three targets:
   - `putMayBeIndex()` — a method that handles both string keys and numeric index keys
   - `initFast()` with a boolean parameter to skip index properties during iteration
   - `isIndex()` or `parseIndex()` checks with `continue`/`break`/`return` to skip index properties

3. **Core logic must be preserved**: The solution must retain:
   - Property iteration using `JSPropertyIterator`
   - Wrapper function creation via `Bun__JSWrappingFunction__create`
   - The `applyCustomMatcher` callback setup

4. **Unsafe methods to avoid**: Do not use bare `.put()` calls for registering properties on the targets, as this method internally asserts that property names are not valid array indices.

## Acceptable read-only methods

The following methods can be used for reading/checking but not for setting properties: `get`, `has`, `contains`, `count`, `next`, `keys`, `iterator`, `len`, `ptr`, `items`, `reset`, `deinit`, `init`, `format`.

## Relevant files

- `src/bun.js/test/expect.zig` — contains the `expect.extend` implementation
