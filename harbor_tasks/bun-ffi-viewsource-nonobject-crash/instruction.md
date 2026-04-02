# Bug: `Bun.FFI.viewSource()` crashes when symbol descriptor values are not objects

## Description

Calling `Bun.FFI.viewSource()` with a symbol map that contains non-object values (such as numbers, strings, or booleans) as symbol descriptors causes a debug assertion failure (crash) instead of producing a proper error.

The `generateSymbols` function in `src/bun.js/api/ffi.zig` iterates over the symbol map entries and checks each value with `isEmptyOrUndefinedOrNull()` before passing it to `generateSymbolForFunction`. However, this check is insufficient — non-object values like numbers or strings pass through, and the subsequent call chain (`value.getTruthy()` -> `value.get()`) asserts that the target is an object, leading to a panic on non-object inputs.

Additionally, several error-return paths in the FFI functions (`print`, `open`, `linkSymbols`) leak memory because they free the symbol keys but not the `arg_types` arrays that were already allocated for each parsed symbol.

## Reproducer

```js
Bun.FFI.viewSource({ myFunc: 42 });
// or
Bun.FFI.viewSource({ myFunc: "not_an_object" });
// or
Bun.FFI.viewSource({ myFunc: true });
```

All of these crash instead of throwing a TypeError.

## Expected Behavior

When a symbol descriptor value is not an object, `Bun.FFI.viewSource()` should throw a `TypeError` with a message like `Expected an object for key "myFunc"` instead of crashing.

## Files to Investigate

- `src/bun.js/api/ffi.zig` — the `generateSymbols` function, specifically the value validation check around line 1420 before calling `generateSymbolForFunction`, and the error-return cleanup paths in `print`, `open`, and `linkSymbols`
