# React Compiler Snapshot Minimizer Bug

## Problem

The React Compiler's snapshot minimizer (in the compiler's `snap` package, run via `yarn snap minimize`) has a bug in how it handles error descriptions during test case reduction. The tool reduces failing compiler test cases to their smallest form that still reproduces the original error, applying simplification strategies iteratively and checking whether the error signature is preserved after each transformation.

The bug manifests in two areas:

1. **Error comparison ignores descriptions.** When the minimizer checks whether a reduced test case still reproduces the original error, its comparison function considers only the `category` and `reason` fields of each error but ignores the `description` field. For example, an error with description `"Cannot call hook inside condition"` and another with description `"Cannot call hook inside loop"` are treated as matching when they share the same category and reason, even though their descriptions differ. This causes the minimizer to accept reduced test cases whose error descriptions differ from the original.

2. **Description is not preserved through the pipeline.** The `description` field is absent from the minimizer's error type definitions, is not carried through when error details are extracted and mapped for comparison, and is not checked during the error equivalence comparison. The field is silently dropped at every stage of the error-handling pipeline.

Additionally, the minimizer is missing reduction strategies for three common AST patterns.

## Expected Behavior

After the fix:

1. **Full error comparison.** Two errors should be considered equivalent only when they match on `category`, `reason`, AND `description`. For example, an error with description `"Cannot call hook inside condition"` must NOT match an error with description `"Cannot call hook inside loop"`, even if category and reason are identical.

2. **Description preserved end-to-end.** The `description` field (typed as `string | null`) must be included in the minimizer's error type definitions — it should appear as a typed property in at least two separate type annotations (one for the top-level error collection type, and one for the individual error detail type). When error details are mapped to error objects for comparison, each mapped error must explicitly carry over the `description` value from its source detail. The error equivalence comparison must also check the `description` field.

3. **Three new generator strategies.** Three new simplification strategies must be implemented as generator functions and registered in the `simplificationStrategies` array alongside existing ones (e.g., `removeStatements`, `removeCallArguments`). The strategies must be named exactly:
   - `removeFunctionParameters` — yields ASTs with function parameters removed one at a time
   - `removeArrayPatternElements` — yields ASTs with array destructuring pattern elements removed one at a time
   - `removeObjectPatternProperties` — yields ASTs with object destructuring pattern properties removed one at a time

   These should follow the same implementation pattern as existing strategies in the minimizer.

## Context

The relevant code is in the compiler's `snap` package. Existing strategies follow the naming pattern `remove<Structure>` (e.g., `removeStatements`, `removeCallArguments`, `removeArrayElements`, `removeObjectProperties`, `removeJSXAttributes`).
