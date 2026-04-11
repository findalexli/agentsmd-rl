# Implement JSG_TRY / JSG_CATCH Exception Handling Macros

## Problem

The `jsg` layer currently uses `js.tryCatch()` with lambda callbacks for exception handling. This pattern is verbose, doesn't compose well with control flow (e.g., returning from the outer function is awkward inside a lambda), and blocks future coroutine support with `co_await` on `jsg::Promise`.

## Expected Behavior

Introduce `JSG_TRY` / `JSG_CATCH` macros in `src/workerd/jsg/jsg.h` that replace the `js.tryCatch()` lambda pattern. These macros should:

1. Automatically convert both JavaScript exceptions (`JsExceptionThrown`) and KJ exceptions (`kj::Exception`) to `jsg::Value`
2. Use a helper class (`JsgCatchScope`) that sets up a `v8::TryCatch` on construction
3. Support nested usage (inner `JSG_TRY`/`JSG_CATCH` inside outer `JSG_TRY`/`JSG_CATCH`)
4. Support optional `ExceptionToJsOptions` as a second argument to `JSG_CATCH`
5. Be `if-else` friendly (usable inside `if` blocks without extra braces)

The usage pattern should look like:
```cpp
JSG_TRY(js) {
  someCodeThatMightThrow();
} JSG_CATCH(exception) {
  return js.rejectedPromise<void>(kj::mv(exception));
}
```

## Implementation

- Add the `JsgCatchScope` helper class declaration in `jsg.h` and implementation in `jsg.c++`
- Define `#define JSG_TRY` and `#define JSG_CATCH` macros in `jsg.h`
- Migrate existing `js.tryCatch()` call sites across the codebase to use the new macros (crypto, memory-cache, messagechannel, streams, urlpattern, modules)

## Files to Look At

- `src/workerd/jsg/jsg.h` — where the macros and helper class should be defined
- `src/workerd/jsg/jsg.c++` — where `JsgCatchScope` methods should be implemented
- `src/workerd/api/crypto/crypto.c++` — uses `js.tryCatch()` in `DigestStream::dispose`
- `src/workerd/api/memory-cache.c++` — uses `js.tryCatch()` in `hackySerialize`
- `src/workerd/api/messagechannel.c++` — uses `js.tryCatch()` in `dispatchMessage`
- `src/workerd/api/streams/standard.c++` — uses `js.tryCatch()` in `maybeRunAlgorithm` and `write`
- `src/workerd/api/urlpattern-standard.c++` — uses `js.tryCatch()` in regex creation
- `src/workerd/api/urlpattern.c++` — uses `js.tryCatch()` in `compileRegex`
- `src/workerd/jsg/modules-new.c++` — uses `js.tryCatch()` in module handlers

After implementing the code changes, update the relevant documentation in `src/workerd/jsg/README.md` to document the new macros and update the exception handling guidance to reflect current best practices (`js.error()`, `js.throwException()`).
