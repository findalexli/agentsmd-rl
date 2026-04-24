# Bug: `Bun.FFI.viewSource()` crashes on non-object symbol descriptors

## Description

Calling `Bun.FFI.viewSource()` with a symbol map that contains non-object values (such as numbers, strings, or booleans) as symbol descriptors causes the process to abort instead of producing a proper error.

For example:
```js
Bun.FFI.viewSource({ myFunc: 42 });
Bun.FFI.viewSource({ myFunc: "not_an_object" });
Bun.FFI.viewSource({ myFunc: true });
```

All of these abort rather than throwing a TypeError.

Additionally, several FFI functions have imperfect cleanup in their error-return paths, which can leave allocated memory unreleased if an error occurs partway through.

## Expected Behavior

When a symbol descriptor value is not an object, `Bun.FFI.viewSource()` should throw a `TypeError` with a descriptive message instead of crashing.

## Scope

### File under investigation
- `src/bun.js/api/ffi.zig` — contains FFI symbol parsing logic

### Key identifiers that must be present (structural integrity)
The `ffi.zig` file must retain these identifiers as part of the fix validation:
- `pub const FFI = struct`
- `generateSymbols`
- `generateSymbolForFunction`
- `symbols_iter`
- `isEmptyOrUndefinedOrNull`
- `clearAndFree`

### Critical repository files (must exist and be non-empty)
- `build.zig`
- `CMakeLists.txt`
- `tsconfig.json`
- `package.json`
- `src/bun.js/api/ffi.zig`

### Patterns that must NOT appear in `ffi.zig`
The following banned patterns should not be present in the FFI source:
- `std.fs.Dir` — use `bun.sys` + `bun.FD` instead
- `std.fs.cwd` — use `bun.FD.cwd()` instead
- `std.debug.assert` — use `bun.assert` instead

### Files that must pass formatting/linting checks
The following files must pass prettier formatting checks:
- `test/js/bun/ffi/addr32.test.ts`
- `test/js/bun/ffi/cc.test.ts`
- `test/js/bun/ffi/ffi-error-messages.test.ts`
- `scripts/build.mjs`
- `scripts/build.ts`

### Behavioral test output schema
The `Bun.FFI.viewSource()` function, when called with valid symbol descriptors, must produce a result where:
- The output includes `RESULT_TYPE:object` (the return value is a JS object)
- The output includes `RESULT_LENGTH:` (the result has a `.length` property)

When given a non-object symbol descriptor (number, string, boolean), it must throw a `TypeError` with a descriptive message — not abort the process.

### Functions with error-path cleanup requirements
The FFI functions that handle symbol opening/linking/printing (`print`, `open`, `linkSymbols`) have error-return paths that must properly clean up any `arg_types` arrays that were partially allocated before the error occurred. At least two of these functions' error paths must include proper cleanup of allocated `arg_types` arrays before calling `clearAndFree`.
