# Fix Compose Compiler Duplicate $stable Field Issue

## Problem

When a Kotlin object (declared with `object` keyword) defines a composable method that is invoked from a different source file, the Compose compiler plugin generates a JVM bytecode verification error:

```
Duplicate field name "$stable" with signature "I" in class file
```

This occurs because the compiler incorrectly adds a `$stable` property to track object stability, even though Kotlin objects (including companion objects) are inherently singletons and always stable.

## Expected Behavior

1. **Stability Inference**: The compiler must recognize that Kotlin objects (both regular objects and companion objects) are inherently stable singletons. When analyzing type stability, an `isObject` check should return `Stability.Stable`, similar to how enum classes and enum entries are handled. The existing baseline marker in the stability inference code is:
   ```
   if (declaration.isEnumClass || declaration.isEnumEntry) return Stability.Stable
   ```

2. **IR Lowering for Object References**: When determining if an expression is static, the compiler should treat all objects (not just companion objects) as static. This requires checking `symbol.owner.isObject` instead of only checking for companion objects.

3. **Generated IR Output**: The transformed IR for composable calls on objects should use literal stability flags (e.g., `0b0110`) instead of `Object.%stable` references (like `MaterialTheme.%stable`, `BoxScope.%stable`, `HasDefault.%stable`, etc.).

## Test Requirements

Add the following test methods:

1. **`testObjectTypesAreStable`** in `ComposerParamTransformTests.kt`
   - Purpose: Verify that composable method invocations on objects treat the object type as stable without generating `Object.%stable` references in the IR output

2. **`testNoStablePropertyOnCompanionObjects`** in `RunComposableTests.kt`
   - Purpose: Verify that companion objects do not get duplicate `$stable` properties that cause JVM bytecode verification errors

## Golden File Requirements

### New Golden Files to Create

Create golden files for `testObjectTypesAreStable` at these exact paths:
- `plugins/compose/compiler-hosted/integration-tests/src/jvmTest/resources/golden/androidx.compose.compiler.plugins.kotlin.ComposerParamTransformTests/testObjectTypesAreStable[useFir = false].txt`
- `plugins/compose/compiler-hosted/integration-tests/src/jvmTest/resources/golden/androidx.compose.compiler.plugins.kotlin.ComposerParamTransformTests/testObjectTypesAreStable[useFir = true].txt`

These golden files must:
- Contain `// Source` and `// Transformed IR` sections
- NOT contain `Object.%stable` references
- Use literal stability flags like `0b0110` for object receivers

### Existing Golden Files to Update

The following golden files must have `.%stable` references (such as `BoxScope.%stable`, `States.A.%stable`, `MaterialTheme.%stable`, `HasDefault.%stable`, `NoDefault.%stable`, `MultipleDefault.%stable`, `BottomSheetDefaults.%stable`) replaced with literal stability flags:

- `plugins/compose/compiler-hosted/integration-tests/src/jvmTest/resources/golden/androidx.compose.compiler.plugins.kotlin.ContextParametersTransformTests/testMemoizationContextParameters.txt`
- `plugins/compose/compiler-hosted/integration-tests/src/jvmTest/resources/golden/androidx.compose.compiler.plugins.kotlin.ControlFlowTransformTests/testComposablePropertyDelegate[useFir = false].txt`
- `plugins/compose/compiler-hosted/integration-tests/src/jvmTest/resources/golden/androidx.compose.compiler.plugins.kotlin.ControlFlowTransformTests/testComposablePropertyDelegate[useFir = true].txt`
- `plugins/compose/compiler-hosted/integration-tests/src/jvmTest/resources/golden/androidx.compose.compiler.plugins.kotlin.DefaultParamTransformTests/testDefaultArgsOnInvoke[useFir = false].txt`
- `plugins/compose/compiler-hosted/integration-tests/src/jvmTest/resources/golden/androidx.compose.compiler.plugins.kotlin.DefaultParamTransformTests/testDefaultArgsOnInvoke[useFir = true].txt`
- `plugins/compose/compiler-hosted/integration-tests/src/jvmTest/resources/golden/androidx.compose.compiler.plugins.kotlin.LambdaMemoizationTransformTests/composableLambdaInInlineDefaultParam[useFir = false].txt`
- `plugins/compose/compiler-hosted/integration-tests/src/jvmTest/resources/golden/androidx.compose.compiler.plugins.kotlin.LambdaMemoizationTransformTests/composableLambdaInInlineDefaultParam[useFir = true].txt`

## Implementation Notes

The fix involves:
1. Modifying stability inference logic to recognize objects as inherently stable
2. Updating static expression detection to treat all objects (not just companion objects) as static
3. Creating test methods to verify the behavior
4. Updating golden files to reflect the corrected IR output with literal stability flags

For reference, the compiler plugin source is located at `plugins/compose/compiler-hosted/src/main/java/androidx/compose/compiler/plugins/kotlin/` with analysis logic in the `analysis/` subdirectory and lowering transformations in the `lower/` subdirectory.
