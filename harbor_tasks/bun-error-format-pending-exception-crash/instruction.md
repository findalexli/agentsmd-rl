# Bun crashes when error message formatting triggers a JS exception

## Bug Description

When Bun's error-creation functions format an error message, the `{f}` formatter may call
into JavaScript — for example, via `Symbol.toPrimitive`. If the formatting itself throws a
JavaScript exception (such as "Cannot convert a symbol to a string"), the catch branch
returns a fallback format string but **leaves the exception pending on the VM**.

When the error-throwing path subsequently tries to throw the newly created error via
`throwValue` → `JSC__VM__throwError`, it hits an internal `assertNoException` check
and crashes because there is already a pending exception on the VM.

## Reproduction

```js
const v = /foo/;
v[Symbol.toPrimitive] = Symbol;
try { Bun.jest().expect(v).toBeFalse(); } catch {}
```

Running this script causes Bun to crash with an assertion failure instead of
gracefully handling the error.

## Expected Behavior

After fixing, error creation functions that encounter a JS exception during message
formatting should complete gracefully without crashing — the pending exception must
be cleared before the fallback error is returned.

## Requirements

The fix must ensure that:

1. When a JS exception occurs during message formatting in the error functions
   in `src/bun.js/bindings/JSGlobalObject.zig`, the pending exception is cleared
   before returning from the catch block.

2. The four error-creation functions in `src/bun.js/bindings/JSGlobalObject.zig`
   should return appropriately-typed error instances in their exception-handling paths:
   - `createErrorInstance` — may return generic Error instances
   - `createTypeErrorInstance` — should return TypeError-typed instances
   - `createSyntaxErrorInstance` — should return SyntaxError-typed instances
   - `createRangeErrorInstance` — should return RangeError-typed instances

3. The `createDOMExceptionInstance` function in `src/bun.js/bindings/JSGlobalObject.zig`
   should NOT be modified per the specification.

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `prettier (JS/TS/JSON/Markdown formatter)`
