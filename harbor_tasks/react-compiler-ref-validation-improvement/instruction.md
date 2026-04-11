# React Compiler: Improve ref validation for non-mutating functions

## Problem

The React Compiler's ref validation is too strict for certain non-mutating functions like `PanResponder.create()`. When a component uses `PanResponder.create()` with callbacks that access refs, the compiler incorrectly reports a ref access error.

For example, this code should be valid but currently fails compilation:

```javascript
const panResponder = useMemo(
  () =>
    PanResponder.create({
      onPanResponderTerminate: () => {
        onDragEndRef.current();  // This triggers a false positive error
      },
    }),
  []
);
```

The issue is that `PanResponder.create()` is known to freeze its arguments (it doesn't mutate them during render), but the current validation logic doesn't recognize this pattern.

## Expected Behavior

Functions with known aliasing signatures that include both `Freeze` and `ImmutableCapture` effects on the same operand should allow ref access in callbacks. The compiler should:

1. Check if a function has known aliasing effects
2. For `ImmutableCapture` effects, verify if the same operand also has a `Freeze` effect
3. If both effects exist, allow direct ref access validation instead of blocking it

## Files to Look At

- `packages/babel-plugin-react-compiler/src/Validation/ValidateNoRefAccessInRender.ts` — The main validation pass that needs to be updated to handle effect-based ref validation for non-hook functions
- `packages/snap/src/sprout/shared-runtime-type-provider.ts` — Where `PanResponder` type signatures are defined with `Freeze` and `ImmutableCapture` effects
- `packages/snap/src/sprout/shared-runtime.ts` — Where `PanResponder` runtime mock is defined

## Additional Context

This fix should also:
1. Update the `error.validate-mutate-ref-arg-in-render` test fixture to use a proper mutating function (instead of `console.log`)
2. Add a new test fixture `panresponder-ref-in-callback` demonstrating the fixed behavior
3. Add linting and formatting documentation to the compiler's CLAUDE.md file

Read the CLAUDE.md file in the compiler directory for more context on the aliasing effects system and how validation passes work.
