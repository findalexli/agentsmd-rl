# Implement JSG_TRY / JSG_CATCH Exception Handling Macros

## Problem

The workerd codebase currently uses `js.tryCatch(tryBody, catchBody)` for exception handling in JSG code, where `tryBody` and `catchBody` are lambda functions. This lambda-based approach is awkward: it obscures control flow, makes early returns difficult, and doesn't compose well with nested exception handling. It also doesn't prepare well for future coroutine support with `co_await` on `jsg::Promise`.

Several files throughout the API layer (`crypto.c++`, `memory-cache.c++`, `messagechannel.c++`, `standard.c++`, `urlpattern.c++`, `urlpattern-standard.c++`, `modules-new.c++`) use this pattern extensively.

## Expected Behavior

Implement new `JSG_TRY` / `JSG_CATCH` macros that provide clean, statement-based exception handling syntax (similar to `KJ_TRY` / `KJ_CATCH`). The macros should:

1. Automatically convert both JavaScript exceptions (`JsExceptionThrown`) and KJ exceptions (`kj::Exception`) to `jsg::Value`
2. Support an optional `ExceptionToJsOptions` argument on `JSG_CATCH`
3. Work correctly when nested
4. Be compatible with `if`/`else` control flow (the "goto-dead-else-branch" pattern)

The implementation needs a `JsgCatchScope` helper class that manages the `v8::TryCatch` scope and exception conversion.

After implementing the macros, refactor existing `js.tryCatch()` call sites to use the new macros, and add tests covering basic usage, nested usage, options passing, and `TerminateExecution` propagation.

After making the code changes, update the relevant JSG documentation to reflect the new exception handling approach. The `src/workerd/jsg/README.md` should be updated to document the new macros and the recommended exception throwing workflow.

## Files to Look At

- `src/workerd/jsg/jsg.h` — where JSG macros are defined; add the new macros and helper class here
- `src/workerd/jsg/jsg.c++` — implementation of the helper class
- `src/workerd/jsg/function-test.c++` — add tests for the new macros
- `src/workerd/jsg/README.md` — JSG documentation that should be updated
- `src/workerd/api/crypto/crypto.c++` — refactor `js.tryCatch()` usage
- `src/workerd/api/streams/standard.c++` — refactor `js.tryCatch()` usage
- `src/workerd/jsg/modules-new.c++` — refactor `js.tryCatch()` usage
