# Bun crashes when error message formatting triggers a JS exception

## Bug Description

When Bun's error-creation functions (`createErrorInstance`, `createTypeErrorInstance`,
`createSyntaxErrorInstance`, `createRangeErrorInstance`) format an error message, the
`{f}` formatter may call into JavaScript — for example, via `Symbol.toPrimitive`. If
the formatting itself throws a JavaScript exception (such as "Cannot convert a symbol
to a string"), the catch branch returns a fallback format string but **leaves the
exception pending on the VM**.

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

## Relevant Code

The bug is in `src/bun.js/bindings/JSGlobalObject.zig`. Look at the four
`create*ErrorInstance` functions — each has a `catch` branch that handles formatting
failures. The catch branches return a fallback error instance but do not clean up the
VM's exception state before doing so.

There are already other call sites in the same file that properly clear the exception
state in similar situations — look at the existing usage pattern for guidance.

Additionally, three of the four catch branches return a generic error instance type
instead of the specific error type matching their function name (e.g.,
`createTypeErrorInstance` should return a TypeError, not a generic Error).
