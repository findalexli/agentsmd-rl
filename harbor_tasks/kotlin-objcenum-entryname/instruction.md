# Task: Add Support for ObjCEnum.EntryName Annotation

## Problem

When porting Kotlin code to Objective-C, developers need fine-grained control over NS_ENUM entry names. Currently, the Kotlin/Native ObjC export header generator only supports `@ObjCName` for renaming enum entries. However, this has limitations:

1. Using `@ObjCName` to rename NSEnum entries requires escaping, leading to unnecessarily escaped names for fully qualified enum literal names
2. There's no way to specify different names specifically for the generated NS_ENUM enumerators while keeping other naming unchanged

## Goal

Implement support for a new `@ObjCEnum.EntryName` annotation that allows developers to specify custom names for NS_ENUM entries separately from the standard `@ObjCName` annotation behavior.

## Requirements

### 1. Annotation Definition

Add a new nested annotation class `EntryName` inside `ObjCEnum` that:
- Has a required `name` parameter for the Objective-C entry name
- Has an optional `swiftName` parameter for the Swift entry name
- Is targeted at `AnnotationTarget.FIELD` (for enum entries)
- Has binary retention

The annotation should be defined in:
- `libraries/stdlib/src/kotlin/annotations/NativeAnnotations.kt` (expect declaration)
- `kotlin-native/runtime/src/main/kotlin/kotlin/native/Annotations.kt` (actual implementation)

### 2. Compiler Integration

Register the new annotation's fully qualified name (`kotlin.native.ObjCEnum.EntryName`) in:
- `native/base/src/main/kotlin/org/jetbrains/kotlin/backend/konan/KonanFqNames.kt`

### 3. K1 (Legacy Frontend) Support

Implement resolution logic in:
- `native/objcexport-header-generator/impl/k1/src/org/jetbrains/kotlin/backend/konan/objcexport/ObjCExportNamer.kt`

Add a data class to hold the resolved annotation values and an extension function to extract them from enum entry descriptors.

Update the translator to use the new annotation when building NSEnum entries.

### 4. K2 (Analysis API) Support

Implement resolution logic in:
- `native/objcexport-header-generator/impl/analysis-api/src/org/jetbrains/kotlin/objcexport/resolveObjCNameAnnotation.kt`

Add a data class and resolution function similar to the existing `resolveObjCNameAnnotation()`.

Add a `getNSEnumEntryName()` helper function in:
- `native/objcexport-header-generator/impl/analysis-api/src/org/jetbrains/kotlin/objcexport/translateEnumMembers.kt`

Update `translateToNSEnum.kt` to use the new helper instead of directly calling `getEnumEntryName()`.

### 5. Behavior

The `@ObjCEnum.EntryName` annotation should:
- Override the implied enum entry name
- Override any `@ObjCName` annotation on the entry (for NSEnum generation)
- Not affect the Kotlin-side enum entry name or the ObjC property name (only the NSEnum enumerator name)
- Apply the NSEnum type name prefix to the `name` parameter (capitalizing the first character)
- Use `swiftName` for Swift-specific naming if provided

### 6. Documentation

Update the KDoc for `ObjCEnum` to mention:
- That enum literals are prefixed with the type name in Objective-C
- That the `EntryName` annotation can be used to customize the enumerator names

### 7. Test Data

Update the existing test data in:
- `native/objcexport-header-generator/testData/headers/enumClassWithObjCEnumAndRenamedLiterals/Foo.kt`
- `native/objcexport-header-generator/testData/headers/enumClassWithObjCEnumAndRenamedLiterals/!enumClassWithObjCEnumAndRenamedLiterals.h`

Add test cases demonstrating:
- EntryName with only `name` parameter
- EntryName with both `name` and `swiftName` parameters
- EntryName overriding ObjCName
- Combination of EntryName and ObjCName annotations

### 8. Binary Compatibility

Update the binary compatibility validator API dump in:
- `libraries/tools/binary-compatibility-validator/klib-public-api/kotlin-stdlib.api`

## Files to Modify

Key files (in order of importance):
1. `libraries/stdlib/src/kotlin/annotations/NativeAnnotations.kt` - Add EntryName expect declaration
2. `kotlin-native/runtime/src/main/kotlin/kotlin/native/Annotations.kt` - Add EntryName actual implementation
3. `native/base/src/main/kotlin/org/jetbrains/kotlin/backend/konan/KonanFqNames.kt` - Register FqName
4. `native/objcexport-header-generator/impl/k1/src/org/jetbrains/kotlin/backend/konan/objcexport/ObjCExportNamer.kt` - K1 resolution
5. `native/objcexport-header-generator/impl/k1/src/org/jetbrains/kotlin/backend/konan/objcexport/ObjCExportTranslator.kt` - K1 usage
6. `native/objcexport-header-generator/impl/analysis-api/src/org/jetbrains/kotlin/objcexport/resolveObjCNameAnnotation.kt` - K2 resolution
7. `native/objcexport-header-generator/impl/analysis-api/src/org/jetbrains/kotlin/objcexport/translateEnumMembers.kt` - K2 helper
8. `native/objcexport-header-generator/impl/analysis-api/src/org/jetbrains/kotlin/objcexport/translateToNSEnum.kt` - K2 usage
9. `native/objcexport-header-generator/testData/headers/enumClassWithObjCEnumAndRenamedLiterals/Foo.kt` - Test data
10. `native/objcexport-header-generator/testData/headers/enumClassWithObjCEnumAndRenamedLiterals/!enumClassWithObjCEnumAndRenamedLiterals.h` - Expected output
11. `libraries/tools/binary-compatibility-validator/klib-public-api/kotlin-stdlib.api` - Binary compatibility

## Validation

After implementing the changes:
1. The project should compile successfully (`./gradlew :native:objcexport-header-generator:compileKotlin`)
2. The header generator tests should pass (`./gradlew :native:objcexport-header-generator:test`)
3. The generated headers should show the renamed NSEnum entries based on `@ObjCEnum.EntryName` annotations

## Notes

- The annotation should be `@Target(AnnotationTarget.FIELD)` since it's applied to enum entries
- The `EntryName` annotation takes priority over `ObjCName` for NSEnum generation
- The NSEnum type name prefix is always added to the entry name (with first character capitalized)
- For Swift, no prefix is added (as is the current behavior)
