# FFI linkSymbols / viewSource crash on non-object property values

## Bug Description

`Bun.FFI.linkSymbols()` and `Bun.FFI.viewSource()` crash when the input object has non-object property values (numbers, strings, booleans).

The `generateSymbols` function in `src/bun.js/api/ffi.zig` iterates over all properties of the input object and passes each value to `generateSymbolForFunction`, which calls `.get()` / `.getTruthy()` on the value. These methods assert that the target is a JS object.

The existing validation only checks for null/undefined/empty values, which doesn't catch primitive values like numbers, strings, or booleans. When such a value reaches `generateSymbolForFunction`, the assertion fails and the process panics.

## Reproduction

```js
// Any of these crash with "panic: reached unreachable code"
Bun.FFI.linkSymbols({ foo: 42 });
Bun.FFI.viewSource({ myFunc: "not_an_object" });
Bun.FFI.viewSource({ myFunc: true });
```

Expected behavior: these should throw a `TypeError` explaining that an object was expected for the given key, not crash the process.

## Relevant Files

- `src/bun.js/api/ffi.zig` — the `generateSymbols` function contains the validation logic that needs to be strengthened

## Additional Context

There are also three error cleanup paths in `src/bun.js/api/ffi.zig` (in the `print`, `open`, and `linkSymbols` entry points) where `symbols` are freed on error but `arg_types` inside each function entry are not deallocated, causing a memory leak on error paths.
