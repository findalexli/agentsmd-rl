# Support @ObjCName Annotation in Swift Export

## Problem Description

The Kotlin Swift Export feature currently doesn't support the `@ObjCName` annotation, which allows Kotlin developers to specify custom names for their declarations when exported to Swift/Objective-C. This annotation is crucial for providing better Swift-friendly APIs.

The `@ObjCName` annotation has three parameters:
- `name`: The Objective-C name
- `swiftName`: The Swift name (optional, can use "_" for empty parameter names)
- `isExact`: Whether the name is exact (used for nested classes)

## What Needs to Be Done

You need to add support for reading and applying `@ObjCName` annotations in the Swift Export pipeline. The annotation should affect:

1. **Class/object/interface names** - When exporting a class with `@ObjCName`, use the specified name instead of the Kotlin name
2. **Function parameter names** - Support custom parameter names and argument labels via `swiftName` and `name` parameters
3. **Property names** - Support custom property names in the exported Swift interface

## Key Files to Modify

Focus on these files in the `native/swift/` directory:

1. **`sir-providers/src/org/jetbrains/kotlin/sir/providers/utils/AnalysisApiUtils.kt`**
   - Add a data class to hold the parsed `@ObjCName` annotation values
   - Add an extension property on `KaDeclarationSymbol` to extract the annotation
   - Handle the special case where `swiftName = "_"` should be treated as empty string
   - You'll need to use `ClassId.topLevel(FqName("kotlin.native.ObjCName"))` to identify the annotation

2. **`sir-providers/src/org/jetbrains/kotlin/sir/providers/impl/SirDeclarationNamerImpl.kt`**
   - Use the new annotation extension to get custom names before falling back to default naming
   - The `getName()` function should check for the annotation first

3. **`sir-light-classes/src/org/jetbrains/sir/lightclasses/utils/TypeTranslationUtils.kt`**
   - Update `translateParameters()` to extract and apply custom parameter names from the annotation
   - Both `argumentName` and `parameterName` in `SirParameter` should respect the annotation

4. **`sir-light-classes/src/org/jetbrains/sir/lightclasses/nodes/SirProtocolFromKtSymbol.kt`**
   - Update the `name` property to use the new naming logic
   - Change from `ktSymbol.name.asString()` to a method that considers `@ObjCName`

## Implementation Notes

- The annotation class is `kotlin.native.ObjCName` in the `kotlin.native` package
- To parse annotation arguments, you'll need to work with `KaAnnotationValue.ConstantValue`
- The `swiftName` parameter takes priority over `name` for Swift export, but `name` is used for Objective-C
- When `swiftName` is "_", it means the parameter should have no explicit name (empty string)
- The extension property should return null if the annotation is not present on the symbol

## Expected Behavior

After implementing this feature:
- A class annotated with `@ObjCName("ObjCClass", "SwiftClass")` should export as `SwiftClass` in Swift
- A parameter annotated with `@ObjCName("objCParam", "swiftParam")` should use those names in the exported interface
- The underscore handling should allow parameters without explicit labels: `@ObjCName(swiftName = "_")`

## References

- The `@ObjCName` annotation is defined in the Kotlin standard library for native targets
- Look at how other annotations like `Throws` are already handled in `AnalysisApiUtils.kt` for patterns
- You can find test data in `swift-export-standalone-integration-tests/simple/testData/generation/annotations/`
