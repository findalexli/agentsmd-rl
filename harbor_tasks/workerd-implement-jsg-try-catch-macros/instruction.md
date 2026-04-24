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

Where `JSG_TRY(js)` takes a `jsg::Lock&` parameter (by convention named `js`), and `JSG_CATCH(exception)` introduces a `jsg::Value&` variable with the user-provided name.

## Implementation Requirements

### Macros

Define `JSG_TRY` and `JSG_CATCH` macros in `src/workerd/jsg/jsg.h` using `#define`.

### Supporting Class

The macros require a helper class to manage exception state. In `src/workerd/jsg/jsg.h`, declare a class named `JsgCatchScope` with:
- A constructor taking `jsg::Lock& js`
- A `catchException()` method accepting optional `ExceptionToJsOptions`
- A `getCaughtException()` method returning `jsg::Value&`

In `src/workerd/jsg/jsg.c++`, implement `JsgCatchScope::catchException()` to:
- Convert `JsExceptionThrown` to the caught V8 exception as `jsg::Value`
- Convert `kj::Exception` to a JavaScript error via `js.exceptionToJs()`

## Migration Scope

Migrate the existing `js.tryCatch()` call sites in these files to use the new macros:
- `src/workerd/api/crypto/crypto.c++`
- `src/workerd/api/memory-cache.c++`
- `src/workerd/api/messagechannel.c++`
- `src/workerd/api/streams/standard.c++`
- `src/workerd/api/urlpattern-standard.c++`
- `src/workerd/api/urlpattern.c++`
- `src/workerd/jsg/modules-new.c++`

At least 4 of these 7 files must be successfully migrated.

## Documentation Updates

After implementing the code changes, update the relevant documentation in `src/workerd/jsg/README.md` to:
- Document the `JSG_TRY` and `JSG_CATCH` macros with usage examples showing `JSG_TRY(js)` syntax
- Update the exception handling guidance to reflect current best practices (`js.error()`, `js.throwException()`)
- Include usage examples showing the recommended patterns

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `ruff format and ruff check`
