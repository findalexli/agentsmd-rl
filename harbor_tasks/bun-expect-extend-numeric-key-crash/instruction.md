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

In `src/bun.js/test/expect.zig`, the `expect.extend` implementation iterates over the matchers object and registers each property. The current property-setting method asserts that the property name is not a valid array index, but numeric keys like `1073741820` are valid array indices, causing the assertion to fail.

The property iterator needs to be configured to skip index properties, or the property-setting calls need to use a method that can handle index properties.

## Relevant files

- `src/bun.js/test/expect.zig` — the `expect.extend` registration logic (look for the property iteration loop around the `JSPropertyIterator`)
