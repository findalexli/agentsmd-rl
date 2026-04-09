# Fix Compose Compiler Inline Lambda Group Handling

## Problem Description

The Compose compiler plugin has a bug when handling inline functions with multiple inline lambda parameters. When a non-composable inline function (like `thenIf`) contains two or more inline lambda parameters and is called from within a Composable function, the compiler doesn't properly wrap the lambda bodies with composition groups.

This causes incorrect behavior when:
1. The lambdas contain composable calls (like `remember { mutableStateOf(...) }`)
2. The control flow switches between branches (e.g., condition changes from true to false)
3. Early returns are present in the lambda bodies

The result is that state can be lost or incorrectly retained when recompositions happen after control flow changes.

## Files to Modify

**Primary file:**
- `plugins/compose/compiler-hosted/src/main/java/androidx/compose/compiler/plugins/kotlin/lower/ComposableFunctionBodyTransformer.kt`

This is the main IR transformer that handles Composable functions. You'll need to:

1. Track when an inline function call has multiple inline lambda parameters
2. Force group wrapping around the lambda bodies in these cases
3. Handle early returns correctly within these wrapped groups

## Context

The fix involves the `ComposableFunctionBodyTransformer` class which is responsible for:
- Transforming Composable function bodies
- Managing composition groups (start/end markers)
- Handling inline function calls and their lambda arguments
- Processing early returns in composable contexts

Key areas to understand:
- `Scope.CaptureScope` - tracks captured composable calls within inline lambdas
- `visitFunctionInScope()` - handles function body transformation
- Early return handling with `leavingInlinedLambda` flag
- Group management with `irStartReplaceGroup`/`irEndReplaceGroup`

## Related Resources

- Test file: `ControlFlowTransformTests.kt` - contains test cases for control flow transformations
- Runtime tests: `CompositionTests.kt` - contains runtime behavior tests
- The regression is tracked as b/479646393

## Expected Behavior

After the fix:
- Inline functions with multiple inline lambdas should have their lambda bodies wrapped in groups
- Early returns within these lambdas should properly end the groups before returning
- Control flow switching (true/false branches) should correctly retain/reset state per branch

## Agent Instructions

This is a compiler internals task. Follow the guidelines in:
- `.ai/guidelines.md` - general Kotlin development guidelines
- `compiler/AGENTS.md` - compiler architecture information

Use quiet mode (`-q`) when running Gradle to reduce output noise.
