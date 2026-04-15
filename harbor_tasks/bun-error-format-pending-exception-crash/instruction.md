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

Four error-creation functions need this fix:
1. A generic error creation function that should return a generic Error instance from its catch block
2. A TypeError creation function that should return a TypeError-typed instance from its catch block
3. A SyntaxError creation function that should return a SyntaxError-typed instance from its catch block
4. A RangeError creation function that should return a RangeError-typed instance from its catch block

Note: There is a separate DOMException creation function that should NOT be modified.
