# [compiler] Improved ref validation for non-mutating functions

## Problem

The React Compiler validation pass that prevents ref access during render reports false positive errors for some function calls that are safe. For example, React Native provides a `PanResponder` API whose `PanResponder.create()` method freezes its configuration argument and does not invoke callbacks during render. However, passing callbacks that access refs to `PanResponder.create()` still triggers "ref access in render" errors.

The existing test fixture for validating mutate-ref-arg-in-render uses `console.log(ref.current)` which does not properly test mutating ref access — it should use the `mutate()` function from the shared runtime instead.

## Expected Behavior

The validation should distinguish safe from unsafe function calls by consulting the function known aliasing effects on its operands:

- Functions that **freeze** their input (like `PanResponder.create`) should allow ref access in callbacks passed to them — the operand is frozen and the callback is never invoked during render.
- Functions that **mutate** their input should continue to use stricter validation.

In the aliasing effects system:
- The `Freeze` effect indicates a function that freezes its operand, making ref access in callbacks safe.
- The `ImmutableCapture` effect represents capturing a value immutably. When `ImmutableCapture` co-occurs with `Freeze` on the same operand (as in `PanResponder.create` known signature), the operand is safely frozen. When `ImmutableCapture` appears alone (as in downgraded defaults for already-frozen operands), the function is unknown and ref access should still be flagged.
- The `Create` effect describes creating a new value, where the returned value kind should be `Frozen` for freeze-returning functions.
- The compiler should avoid reporting duplicate errors for the same ref access operand.

The existing validation branches must remain intact: the `isRefLValue` check for the `mergeRefs` pattern, and the `interpolatedAsJsx` check for JSX child ref handling. The three validation functions (`validateNoDirectRefValueAccess`, `validateNoRefPassedToFunction`, `validateNoRefValueAccess`) must all still be called.

The shared runtime, which provides test scaffolding used by the compiler fixture system, must gain a `PanResponder` object whose `create` method returns its input argument (modeling the freeze behavior). The shared runtime must continue to export the existing `typedMutate` function and `typedLog` as its default export.

The associated type provider must include a `PanResponder` type definition with the aliasing effects described above: `Freeze`, `ImmutableCapture`, `Create`, and return kind `Frozen`.

A new compiler fixture demonstrating the `PanResponder.create` pattern with ref access in a callback must be added, using `useRef` to create a ref and passing a callback that accesses the ref to `PanResponder.create`. The fixture must import from `shared-runtime` and have a corresponding expected-output file.

The `error.validate-mutate-ref-arg-in-render` fixture must be updated to import `mutate` from `shared-runtime` and call `mutate(ref.current)` instead of the current `console.log(ref.current)`.

The compiler documentation (the CLAUDE.md file inside the compiler directory) must be updated to include both the lint command and the prettier formatting command.

## Code Style Requirements

- **Lint**: Run `yarn workspace babel-plugin-react-compiler lint` to check code style. Lint must pass with zero errors.
- **Formatting**: Run `yarn prettier-all` from the repository root directory to format all files before committing.
