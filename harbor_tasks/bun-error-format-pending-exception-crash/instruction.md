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

## Scope

The four functions that create error instances in `src/bun.js/bindings/JSGlobalObject.zig`
are in scope: `createErrorInstance`, `createTypeErrorInstance`, `createSyntaxErrorInstance`,
`createRangeErrorInstance`.

The `createDOMExceptionInstance` function is **not** in scope and should not be modified.

## Valid Solution

A correct fix must satisfy all of the following:

1. The catch block in each of the four error functions clears any pending JS exception
   before returning the fallback error instance.
2. `createTypeErrorInstance` returns a TypeError-typed instance from its catch block.
3. `createSyntaxErrorInstance` returns a SyntaxError-typed instance from its catch block.
4. `createRangeErrorInstance` returns a RangeError-typed instance from its catch block.
5. `createErrorInstance` returns an appropriate generic error from its catch block.
