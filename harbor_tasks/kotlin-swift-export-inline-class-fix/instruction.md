# Task: Fix Swift Export Crash with Inline Classes and Reference Types

## Problem Description

The Swift Export feature in the Kotlin compiler crashes when generating Swift bridge code for inline classes (value classes) that contain reference types. When an inline class wraps a reference type (like a regular class), the generated initialization code fails because of a type mismatch.

The generated code uses `createUninitializedInstance<T>()` calls that need an explicit cast to `Any?` when `T` is an inline class with reference types.

## Required Changes

### 1. Fix the Code Generation

The code generation in the Swift Export bridge code generator must detect when it's generating initialization code for an inline class and ensure the generated code includes the necessary cast. The relevant code is in:

- `native/swift/sir-light-classes/src/org/jetbrains/sir/lightclasses/nodes/SirInitFromKtSymbol.kt`

The fix must add the string `" as Any?"` after `createUninitializedInstance<...>()` calls when the containing class is an inline class (value class).

The source code must include:
- Import: `org.jetbrains.kotlin.analysis.api.components.containingDeclaration`
- The string `isInline` used in the `bridges` property section
- The literal string `" as Any?"` in the generated code output

### 2. Update Golden Files

Update these golden result files to include the `as Any?` cast for inline class allocation patterns:
- `native/swift/swift-export-standalone-integration-tests/simple/testData/generation/classes/golden_result/main/main.kt`
- `native/swift/swift-export-standalone-integration-tests/simple/testData/generation/type_reference/golden_result/main/main.kt`
- `native/swift/swift-export-standalone-integration-tests/simple/testData/generation/typealiases/golden_result/main/main.kt`

The golden files should show patterns like:
- `createUninitializedInstance<INLINE_CLASS>()` becoming `createUninitializedInstance<INLINE_CLASS>() as Any?`
- `createUninitializedInstance<INLINE_CLASS_WITH_REF>()` becoming `createUninitializedInstance<INLINE_CLASS_WITH_REF>() as Any?`
- `createUninitializedInstance<ignored.VALUE_CLASS>()` becoming `createUninitializedInstance<ignored.VALUE_CLASS>() as Any?`

### 3. Create Regression Test Data

Create test data files in `native/swift/swift-export-standalone-integration-tests/simple/testData/execution/valueClass/`:

**valueClass.kt** must contain:
- A class named `Foo` with a property `val x: Int`
- A value class named `Bar` that wraps a reference type: `val foo: Foo`

**valueClass.swift** must contain:
- A test function named `inlineClassWithRef` that creates instances of the value class

### 4. Update Generated Test Class

Update `native/swift/swift-export-standalone-integration-tests/simple/tests-gen/org/jetbrains/kotlin/swiftexport/standalone/test/SwiftExportExecutionTestGenerated.java` to include:
- A test method named `testValueClass()`
- The annotation `@TestMetadata("valueClass")` on this method

## References

- YouTrack issue: KT-85050
