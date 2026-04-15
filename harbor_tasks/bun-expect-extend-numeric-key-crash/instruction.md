# Bug: `expect.extend` crashes with numeric index keys

## Summary

Calling `expect.extend()` with an object that has numeric keys (valid array indices) causes a crash in Bun's test runner. The crash occurs in `JSObjectInlines.h(451)` due to an assertion failure.

## Reproduction

```js
const v1 = { 1073741820: Request };
Bun.jest().expect.extend(v1);
```

Running this code crashes the process.

## Details

In `src/bun.js/test/expect.zig`, the `expect.extend` implementation iterates over the matchers object and registers each custom matcher. Registration sets properties on three target objects within the `extend` function:

- `expect_proto`
- `expect_constructor`
- `expect_static_proto`

The current registration uses `.put()` calls on each target. This method internally asserts the property name is not a valid array index. When a matcher object contains numeric keys like `1073741820`, the assertion fails and the process crashes.

The `extend` function body must also continue to:
- Create wrapper functions via `Bun__JSWrappingFunction__create`
- Set up the `applyCustomMatcher` callback
- Iterate over matcher properties

The fix must update property registration on all three targets to handle index properties safely, either by skipping index properties during iteration or by using a property-setting approach that supports index keys.

## Relevant files

- `src/bun.js/test/expect.zig` — the `expect.extend` registration logic
