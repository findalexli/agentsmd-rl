# [compiler] Improved ref validation for non-mutating functions

## Problem

The React Compiler's `ValidateNoRefAccessInRender` validation pass incorrectly reports "ref access in render" errors for functions that are known to freeze their inputs. For example, React Native's `PanResponder.create()` creates an object designed for interaction handling — it freezes its config argument and doesn't call callbacks during render. However, the compiler still flags ref access in callbacks passed to such functions.

The current validation treats all non-hook, non-JSX-interpolated function call operands uniformly with `validateNoRefPassedToFunction`, without considering whether the function's aliasing effects indicate the operand is safely frozen.

Additionally, the existing test fixture `error.validate-mutate-ref-arg-in-render` uses `console.log(ref.current)` which doesn't properly test the mutating case — it should use `mutate(ref.current)` from the shared-runtime instead.

## Expected Behavior

The validation should use instruction-level aliasing effects to determine the appropriate validation for each operand:
- If an operand has both `Freeze` and `ImmutableCapture` effects, only check for direct ref value access (weaker check — the function freezes the input so callbacks won't be called during render)
- Mutation effects (`Mutate`, `MutateTransitive`, etc.) should use the stricter `validateNoRefPassedToFunction` check
- This refinement only applies to non-hook function calls with known aliasing effects (`instr.effects != null`)

Additionally, `compiler/CLAUDE.md` should document the linting and formatting commands.

## Files to Look At

- `compiler/packages/babel-plugin-react-compiler/src/Validation/ValidateNoRefAccessInRender.ts` — validation pass needing effects-based ref checks
- `compiler/packages/snap/src/sprout/shared-runtime-type-provider.ts` — needs PanResponder type with Freeze+ImmutableCapture aliasing
- `compiler/packages/snap/src/sprout/shared-runtime.ts` — needs PanResponder runtime export
- `compiler/packages/babel-plugin-react-compiler/src/__tests__/fixtures/compiler/` — test fixtures
- `compiler/CLAUDE.md` — add linting and formatting sections
