# Fix Compose Compiler Duplicate $stable Field Issue

## Problem

When a Kotlin object (declared with `object` keyword) defines a composable method that is invoked from a different source file, the Compose compiler plugin generates a JVM bytecode verification error:

```
Duplicate field name "$stable" with signature "I" in class file
```

This occurs because the compiler incorrectly adds a `$stable` property to track object stability, even though Kotlin objects (including companion objects) are inherently singletons and always stable.

## Expected Behavior

The Compose compiler should recognize that Kotlin objects (both regular objects and companion objects) are inherently stable singletons. The following specific requirements must be met:

### 1. Stability Inference

When analyzing type stability, the compiler should treat objects as stable. The stability inference code at `plugins/compose/compiler-hosted/src/main/java/androidx/compose/compiler/plugins/kotlin/analysis/Stability.kt` currently contains this baseline marker:

```
if (declaration.isEnumClass || declaration.isEnumEntry) return Stability.Stable
```

The stability inference logic should be updated to also return `Stability.Stable` for objects. The resulting code must contain:

```
if (declaration.isObject) return Stability.Stable
```

### 2. IR Lowering for Object References

When determining if an expression is static, the compiler currently only checks for companion objects. The lowering code at `plugins/compose/compiler-hosted/src/main/java/androidx/compose/compiler/plugins/kotlin/lower/AbstractComposeLowering.kt` should treat all objects (not just companion objects) as static.

The resulting code must contain:

```
if (symbol.owner.isObject) true
```

### 3. Generated IR Output

The transformed IR for composable calls on objects should use literal stability flags (e.g., `0b0110`) instead of `Object.%stable` references (like `MaterialTheme.%stable`, `BoxScope.%stable`, `HasDefault.%stable`, etc.).

## Test Requirements

Add the following test methods:

1. **`testObjectTypesAreStable`** in `ComposerParamTransformTests.kt` (located at `plugins/compose/compiler-hosted/integration-tests/src/jvmTest/kotlin/androidx/compose/compiler/plugins/kotlin/ComposerParamTransformTests.kt`)
   - Purpose: Verify that composable method invocations on objects treat the object type as stable without generating `Object.%stable` references in the IR output

2. **`testNoStablePropertyOnCompanionObjects`** in `RunComposableTests.kt` (located at `plugins/compose/compiler-hosted/integration-tests/src/jvmTest/kotlin/androidx/compose/compiler/plugins/kotlin/RunComposableTests.kt`)
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

## Implementation Scope

The fix involves changes in:
- `plugins/compose/compiler-hosted/src/main/java/androidx/compose/compiler/plugins/kotlin/analysis/Stability.kt` - stability inference logic
- `plugins/compose/compiler-hosted/src/main/java/androidx/compose/compiler/plugins/kotlin/lower/AbstractComposeLowering.kt` - static expression detection
- Test files and golden files as specified above

The compiler plugin source is located at `plugins/compose/compiler-hosted/src/main/java/androidx/compose/compiler/plugins/kotlin/` with analysis logic in the `analysis/` subdirectory and lowering transformations in the `lower/` subdirectory.
