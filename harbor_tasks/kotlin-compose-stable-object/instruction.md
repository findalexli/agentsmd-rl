# Fix Compose Compiler Object Stability Issue

## Problem

The Compose compiler plugin is incorrectly generating duplicate `$stable` properties on Kotlin objects (both regular objects and companion objects) when they are accessed from a different file than where they are defined.

This causes JVM bytecode verification errors like:
```
Duplicate field name "$stable" with signature "I" in class file C
```

## Context

When a composable method is defined inside an object and invoked from a different file, the compiler was adding a `$stable` property to track the object's stability. However, this was redundant since Kotlin objects are inherently singletons and always stable.

## Key Files to Examine

1. **`plugins/compose/compiler-hosted/src/main/java/androidx/compose/compiler/plugins/kotlin/analysis/Stability.kt`**
   - Contains the stability inference logic
   - Look for where types are classified as stable/unstable

2. **`plugins/compose/compiler-hosted/src/main/java/androidx/compose/compiler/plugins/kotlin/lower/AbstractComposeLowering.kt`**
   - Contains IR lowering transformations for Compose
   - Look for how object references are handled

## Expected Behavior

After the fix:
- Kotlin objects should be treated as inherently stable without adding `$stable` properties
- Companion objects and regular objects accessed across files should not trigger additional stability fields
- The golden test files should show literal stability flags (like `0b0110`) instead of `Object.%stable` references

## Test Files

The following test files help verify the fix:
- `ComposerParamTransformTests.kt` - Tests object types are stable
- `RunComposableTests.kt` - Regression test for companion objects
- `StaticExpressionDetectionTests.kt` - Tests for static expression detection

Golden files in `resources/golden/` directory show expected IR output.

## Reproduction

When an object is defined in one file and its composable method is called from another file, the compiler should:
1. Recognize the object type as stable
2. NOT add a `$stable` property to the object class
3. Use literal stability flags in the generated IR
