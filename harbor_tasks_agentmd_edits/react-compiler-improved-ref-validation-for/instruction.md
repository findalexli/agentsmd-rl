# Improved Ref Validation for Non-Mutating Functions

## Problem

The React Compiler's `ValidateNoRefAccessInRender` pass currently produces false positive "ref access in render" errors when a ref-capturing callback is passed to a function that is known to **not** call its arguments during render.

For example, React Native's `PanResponder.create()` accepts a config object with callbacks that may capture refs. These callbacks are only invoked during interaction handling, never during render. However, the compiler currently treats all function call operands uniformly — if any operand touches a ref, it reports an error, regardless of whether the function actually calls that operand during render.

The validation logic iterates over all operands of a function call and applies the same check to each one. It doesn't take advantage of the compiler's aliasing effects system, which already knows which functions freeze their inputs vs. mutate them.

## Expected Behavior

When a non-hook function call has known aliasing effects (via the type provider), the validation should use those effects to determine the appropriate check for each operand:

- **Freeze** effects on an operand → only check for direct ref value access (not ref-passing)
- **Mutate/Capture/Render** effects → check that refs aren't passed to the function
- **ImmutableCapture** combined with a **Freeze** on the same operand → treat as frozen (safe)
- **ImmutableCapture** without Freeze → treat as potentially unsafe (unknown function)

A concrete case: `PanResponder.create({onPanResponderTerminate: () => { myRef.current() }})` should compile without error because `PanResponder.create` freezes its config argument.

Meanwhile, passing `ref.current` to a function with mutation effects (like `mutate(ref.current)`) must still produce an error.

## Files to Look At

- `compiler/packages/babel-plugin-react-compiler/src/Validation/ValidateNoRefAccessInRender.ts` — the validation pass that needs the effects-based branching
- `compiler/packages/snap/src/sprout/shared-runtime-type-provider.ts` — register `PanResponder.create` with the correct aliasing signature
- `compiler/packages/snap/src/sprout/shared-runtime.ts` — add `PanResponder` runtime mock for test fixtures
- `compiler/packages/babel-plugin-react-compiler/src/__tests__/fixtures/compiler/` — add a fixture for the PanResponder case, update the existing mutate-ref fixture

After making the code changes, update the project's `compiler/CLAUDE.md` to document the linting and formatting commands available for the compiler package — these are useful developer workflows that aren't currently documented there.
