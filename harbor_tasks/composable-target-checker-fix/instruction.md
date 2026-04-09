# Fix Compose Target Checker Inference

## Problem

The Compose compiler plugin's target applier checker is not correctly detecting mismatched composable calls in certain nested scenarios. Specifically, when composables with different target appliers (e.g., Vector vs UI) are nested, some diagnostic warnings that should be emitted are being missed.

The issue is in the `callableInferenceNodeOf` function in the Compose compiler plugin for Kotlin's FIR (K2) frontend.

## Relevant Files

- `plugins/compose/compiler-hosted/src/main/java/androidx/compose/compiler/plugins/kotlin/k2/ComposableTargetChecker.kt`

## What You Need to Know

1. **LazySchemeStorage caching**: The `LazySchemeStorage<Node>.getOrPut` method only returns the same scheme for nodes whose `element` properties are structurally equal. This means the `element` property of inference nodes is critical for correct scheme association.

2. **FirCallableElementInferenceNode**: This node class needs to properly identify its kind and element for correct diagnostic generation.

3. **callableInferenceNodeOf**: This function creates inference nodes for callable elements (functions, lambdas, etc.) and needs to ensure the resulting nodes have `element` properties that are suitable for scheme caching.

## Expected Behavior

After the fix:
- `FirCallableElementInferenceNode.kind` should correctly identify as a function
- `callableInferenceNodeOf` should return nodes with proper `element` properties that enable correct scheme caching
- The diagnostic tests (especially `testDifferentWrapperTypes`) should correctly detect and report mismatched composable target appliers

## Testing

The project uses Gradle for building. You can run the relevant tests with:

```bash
./gradlew :plugins:compose:compiler-hosted:integration-tests --tests "*ComposableTargetCheckerTests.testDifferentWrapperTypes" -q
```

Or compile the module with:

```bash
./gradlew :plugins:compose:compiler-hosted:compileKotlin -q
```

## Notes

- This is a Kotlin compiler plugin for the Jetpack Compose framework
- The fix involves handling different FIR element types (FirFunctionCall, FirAnonymousFunction, etc.) appropriately
- Look at how `parameterInferenceNodeOrNull` is currently being used and consider whether early returns would be clearer
