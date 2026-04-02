# React Compiler Minimization Tool Bug

## Problem

The React Compiler's snapshot minimization tool (`compiler/packages/snap/src/minimize.ts`) is not correctly preserving error equivalence when minimizing failing test cases. Specifically, the tool compares compiler errors by their `category` and `reason` fields only, but ignores the `description` field. This can cause the minimizer to produce reduced test cases that have different error descriptions than the original, making debugging misleading.

## Expected Behavior

The minimization tool should consider `description` as part of error identity when determining if two errors "match" during the reduction process. Additionally, the minimizer should support more aggressive reduction strategies for function parameters and destructuring patterns (both array and object patterns).

## Files to Modify

- `compiler/packages/snap/src/minimize.ts`

## Key Areas to Update

1. **Error type definitions**: The `CompileErrors` type and `error.details` type need to include `description` as a `string | null` field
2. **Error extraction**: When mapping error details, the `description` field should be preserved
3. **Error comparison**: The `errorsMatch` function needs to compare the `description` field in addition to `category` and `reason`
4. **New minimization strategies**: Add generators for removing function parameters, array pattern elements, and object pattern properties

## Background on the Minimizer

The snapshot minimizer (`yarn snap minimize`) reduces failing compiler test cases to their smallest form that still reproduces the original error. It works by applying various simplification strategies iteratively, checking if the error signature remains the same after each transformation.

The existing strategies include removing statements, call arguments, array elements, object properties, JSX attributes, etc. The fix should add three new strategies to handle function parameters and destructuring patterns.

## Output

After the fix, the minimizer should:
- Preserve `description` when extracting error details
- Only accept minimized versions that match the original error including description
- Support additional reduction strategies for function parameters and destructuring
