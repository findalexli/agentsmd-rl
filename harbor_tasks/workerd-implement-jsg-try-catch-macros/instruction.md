# Implement JSG_TRY / JSG_CATCH Exception Handling Macros

## Problem

The `jsg` layer currently uses `js.tryCatch()` with lambda callbacks for exception handling. This pattern is verbose, doesn't compose well with control flow (e.g., returning from the outer function is awkward inside a lambda), and blocks future coroutine support with `co_await` on `jsg::Promise`.

## Goal

Replace the `js.tryCatch()` lambda pattern with cleaner macros that provide the same exception handling functionality but with improved ergonomics and composition.

## Required Behavior

The new exception handling macros should:

1. Automatically convert both JavaScript exceptions (`JsExceptionThrown`) and KJ exceptions (`kj::Exception`) to `jsg::Value`
2. Set up proper try/catch infrastructure on construction
3. Support nested usage (inner try/catch inside outer try/catch)
4. Support optional `ExceptionToJsOptions` as a configuration argument
5. Be `if-else` friendly (usable inside `if` blocks without extra braces)

## Expected Usage Pattern

The macros should enable code like:
```cpp
JSG_TRY(js) {
  someCodeThatMightThrow();
} JSG_CATCH(exception) {
  return js.rejectedPromise<void>(kj::mv(exception));
}
```

## Implementation Locations

- Define the macros in `src/workerd/jsg/jsg.h`
- Implement supporting functionality in `src/workerd/jsg/jsg.c++`
- Update documentation in `src/workerd/jsg/README.md` to reflect the new patterns

## Migration Scope

Migrate the existing `js.tryCatch()` call sites in these files to use the new macros:
- `src/workerd/api/crypto/crypto.c++`
- `src/workerd/api/memory-cache.c++`
- `src/workerd/api/messagechannel.c++`
- `src/workerd/api/streams/standard.c++`
- `src/workerd/api/urlpattern-standard.c++`
- `src/workerd/api/urlpattern.c++`
- `src/workerd/jsg/modules-new.c++`

## Documentation Updates

After implementing the code changes, update the relevant documentation in `src/workerd/jsg/README.md` to:
- Document the new exception handling macros
- Update the exception handling guidance to reflect current best practices (`js.error()`, `js.throwException()`)
- Include usage examples showing the recommended patterns