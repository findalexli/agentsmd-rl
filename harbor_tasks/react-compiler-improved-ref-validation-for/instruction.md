# [compiler] Improved ref validation for non-mutating functions

## Problem

The React Compiler's `ValidateNoRefAccessInRender` validation pass reports "ref access in render" errors for some function calls that are safe. For example, React Native's `PanResponder.create()` freezes its config argument and doesn't call callbacks during render, yet the compiler still flags ref access in callbacks passed to such functions. The result is false positive errors for safe patterns.

The existing test fixture `error.validate-mutate-ref-arg-in-render` uses `console.log(ref.current)` which doesn't properly test mutating ref access — it should use `mutate(ref.current)` from the shared runtime.

## Expected Behavior

The validation should correctly distinguish safe from unsafe function calls based on what aliasing effects the function is known to have on its operands:
- Functions that freeze their input (like `PanResponder.create`) should allow ref access in callbacks passed to them
- Functions that mutate their input should use stricter validation

The fix should handle functions with known aliasing effects without breaking existing validation for hooks, JSX children, or the `mergeRefs` pattern.

## Files to Modify

**ValidateNoRefAccessInRender.ts** — Add a new branch in the validation logic that handles non-hook function calls by examining their aliasing effects. When a function has known effects like Freeze, use that information to determine whether ref access in callbacks is safe.

**error.validate-mutate-ref-arg-in-render.js** — Update to use `mutate(ref.current)` instead of `console.log(ref.current)` to properly test mutating ref access.

**shared-runtime.ts** — Add a `PanResponder` object with a `create` method that returns its input argument (modeling React Native's freeze behavior).

**shared-runtime-type-provider.ts** — Add a `PanResponder` type definition with aliasing effects that reflect freeze semantics (config is frozen, and the returned object is also frozen).

**panresponder-ref-in-callback.js** — Add a new test fixture demonstrating the PanResponder pattern with ref access in a callback, plus a corresponding `.expect.md` file.

**compiler/CLAUDE.md** — Document the lint and prettier commands for the compiler:
- `yarn workspace babel-plugin-react-compiler lint`
- `yarn prettier-all`

## Verification Criteria

**ValidateNoRefAccessInRender.ts** must handle non-hook function calls by examining their known aliasing effects. The implementation should recognize when ImmutableCapture co-occurs with Freeze (indicating a known-safe freezing function like PanResponder.create) and apply direct-ref validation in that case. Use a deduplication mechanism to avoid reporting duplicate errors for the same ref access.

The existing validation branches must remain intact: the `isRefLValue` check for the mergeRefs pattern and the `interpolatedAsJsx` check for JSX child ref handling.

**shared-runtime.ts** must continue to export `typedMutate` and `typedLog` as default, and also export a `PanResponder` object with a `create` method that returns its input argument.

**shared-runtime-type-provider.ts** must include a `PanResponder` type definition with aliasing effects including `Freeze`, `Create`, and `ImmutableCapture`. The return value kind should be `Frozen`.

**error.validate-mutate-ref-arg-in-render.js** fixture must import `mutate` from `shared-runtime` and call `mutate(ref.current)` instead of `console.log(ref.current)`.

**panresponder-ref-in-callback.js** fixture must import `PanResponder` and `Stringify` from `shared-runtime`, call `PanResponder.create` with a callback that accesses a ref, and have a corresponding `.expect.md` file.

**compiler/CLAUDE.md** must document both the lint command and the prettier command.
