# Bug: `Error.captureStackTrace` missing async frames

## Summary

`Error.captureStackTrace(err)` produces a stack trace that is missing `at async <fn>` frames from the await chain, while `new Error()` includes them. This means users who rely on `Error.captureStackTrace` (which is a V8 compatibility API) get incomplete stack traces when working with async code.

## Reproduction

```js
async function innerAsync() {
  await new Promise(r => setImmediate(r));
  const err = new Error("async test");
  Error.captureStackTrace(err);
  return err;
}

async function outerAsync() {
  return await innerAsync();
}

const err = await outerAsync();
console.log(err.stack);
// Expected: should contain "at async outerAsync"
// Actual: only shows synchronous frames, "at async outerAsync" is missing
```

Additionally, when a `caller` argument is passed to `Error.captureStackTrace(err, caller)`, the async frames above the caller should be preserved, but they are also missing.

## Affected file

`src/bun.js/bindings/ErrorStackTrace.cpp` — specifically the `getFramesForCaller` function.

## Root cause

The current implementation of `getFramesForCaller` uses a hand-rolled `StackVisitor::visit` walk that only collects synchronous frames. Unlike the code path for `new Error()`, it does not collect async continuation frames from the await chain.

There is also a secondary issue: the `stackTraceLimit` is applied during the raw frame collection pass, before caller filtering. This means if the caller function sits deeper in the stack than the limit, all collected frames are above the caller and get removed, producing an empty trace.

## Expected behavior

1. `Error.captureStackTrace(err)` should include `at async <fn>` frames, matching what `new Error().stack` produces.
2. `Error.captureStackTrace(err, caller)` should filter out frames up to and including the caller, but preserve async parent frames.
3. When the caller is not found in the synchronous portion of the stack, all frames should be removed (matching V8 behavior).
4. `Error.stackTraceLimit` should be applied after caller removal, not before.
