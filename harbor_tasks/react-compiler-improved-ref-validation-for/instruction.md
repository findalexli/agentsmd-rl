# [compiler] Improved ref validation for non-mutating functions

## Problem

The React Compiler's `ValidateNoRefAccessInRender` validation pass reports "ref access in render" errors for some function calls that are safe. For example, React Native's `PanResponder.create()` freezes its config argument and doesn't call callbacks during render, yet the compiler still flags ref access in callbacks passed to such functions. The existing test fixture `error.validate-mutate-ref-arg-in-render` uses `console.log(ref.current)` which doesn't properly test mutating ref access.

## Expected Behavior

The validation should correctly distinguish safe from unsafe function calls based on what effects the function is known to have on its operands. Functions that freeze their input (like `PanResponder.create`) should allow ref access in callbacks passed to them. Functions that mutate their input should use stricter validation.

## Files to Modify/Add

- `compiler/packages/babel-plugin-react-compiler/src/Validation/ValidateNoRefAccessInRender.ts` — update validation to consider aliasing effects
- `compiler/packages/babel-plugin-react-compiler/src/__tests__/fixtures/compiler/error.validate-mutate-ref-arg-in-render.js` — update to use `mutate(ref.current)` from shared-runtime
- `compiler/packages/babel-plugin-react-compiler/src/__tests__/fixtures/compiler/panresponder-ref-in-callback.js` — add new fixture for PanResponder pattern with an `expect.md` file
- `compiler/packages/snap/src/sprout/shared-runtime-type-provider.ts` — add PanResponder type with appropriate aliasing effects
- `compiler/packages/snap/src/sprout/shared-runtime.ts` — add PanResponder runtime export
- `compiler/CLAUDE.md` — document lint and formatting commands

## Verification Criteria

The following patterns must be present in the modified files:

**ValidateNoRefAccessInRender.ts** must contain:
- A switch/case handling for effect kinds including an `ImmutableCapture` case
- A `visitedEffects` set for deduplicating validation errors
- Logic that checks for `hookKind == null` and `instr.effects` to handle non-hook function calls with known effects
- Handlers for effect kinds including at least `Mutate`, `MutateTransitive`, and `MutateConditionally`
- An `isRefLValue` check for the mergeRefs pattern
- An `interpolatedAsJsx` check for JSX child ref handling

**shared-runtime.ts** must:
- Continue to export `typedMutate` and `typedLog` as default
- Export a `PanResponder` object with a `create` method that returns its input argument

**shared-runtime-type-provider.ts** must:
- Include a `PanResponder` type definition with aliasing effects including `Freeze`, `Create`, and `ImmutableCapture`
- The return value kind should be `Frozen`

**error.validate-mutate-ref-arg-in-render.js** fixture must:
- Import `mutate` from `shared-runtime`
- Call `mutate(ref.current)` instead of `console.log(ref.current)`

**panresponder-ref-in-callback.js** fixture must:
- Import `PanResponder` and `Stringify` from `shared-runtime`
- Call `PanResponder.create` with a callback that accesses a ref
- Have a corresponding `.expect.md` file

**compiler/CLAUDE.md** must document:
- `yarn workspace babel-plugin-react-compiler lint`
- `yarn prettier-all`
