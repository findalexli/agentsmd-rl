# Bug Report: React Compiler ref validation applies wrong checks for non-hook function calls with known aliasing effects

## Problem

The React Compiler's `ValidateNoRefAccessInRender` pass incorrectly validates ref access when calling non-hook functions that have known aliasing effects. Currently, when a function call's lvalue is not a ref type, is not passed as JSX, and the call is not a hook, the validation falls through to a generic path that does not consider the specific aliasing effects of each operand. This means that operands which are only captured immutably (e.g., stored in an array without mutation) are incorrectly flagged as ref-access violations, producing false positive errors.

## Expected Behavior

When a non-hook function call has known aliasing effects, the compiler should use those effects to determine the appropriate validation for each operand individually. Operands that are only immutably captured (e.g., `ImmutableCapture`) should not trigger ref-access errors, since they do not actually expose the ref value during render.

## Actual Behavior

All operands of such function calls are validated uniformly with `validateNoRefValueAccess`, causing false positive errors when refs are passed to functions that only capture them immutably without accessing their values.

## Files to Look At

- `compiler/packages/babel-plugin-react-compiler/src/Validation/ValidateNoRefAccessInRender.ts`
