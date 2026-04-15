# Swift Export: Support nullable Unit/Void types

## Problem

The Kotlin compiler's Swift Export feature does not properly handle nullable Unit types (`Unit?`). When exporting Kotlin functions that return `Unit?` or accept `Unit?` parameters to Swift, the type bridging system currently produces incorrect results.

The file `native/swift/sir-providers/src/org/jetbrains/kotlin/sir/providers/impl/BridgeProvider/TypeBridging.kt` contains the type bridging logic. Currently, when an `AsVoid` type (representing non-nullable `Unit`) is encountered inside an `Optional` wrapper, the system does not have proper handling and may produce a `TODO("not yet supported")` error.

## Required Changes

After your fix, the following specific strings must be present in `TypeBridging.kt`:

### New Bridge Type

A new bridge object definition must exist with these exact properties:
- Named exactly: `object AsOptionalVoid`
- Swift type expression: `SirNominalType(SirSwiftModule.optional, listOf(SirNominalType(SirSwiftModule.void)))`
- Kotlin type: `KotlinType.Boolean`
- C type: `CType.Bool`

### Value Conversion Expressions

The new bridge must implement value conversions with these exact expressions:

**For Kotlin sources (`inKotlinSources`):**
- `swiftToKotlin` must return exactly: `(if ($valueExpression) Unit else null)`
- `kotlinToSwift` must return exactly: `($valueExpression != null)`

**For Swift sources (`inSwiftSources`):**
- `swiftToKotlin` must return exactly: `($valueExpression != nil)`
- `kotlinToSwift` must return exactly: `($valueExpression ? () : nil)`

### Bridge Selection Logic

The `bridgeNominalType` function must contain this exact pattern when handling Optional wrappers:
- `is AsVoid -> AsOptionalVoid`

### NS Collection Bridging

The `bridgeAsNSCollectionElement` function must contain:
- `is AsOptionalVoid -> AsObjCBridgedOptional(bridge.swiftType)`

### Error Messages

The following error handling patterns must exist:
- When `AsVoid` is incorrectly used inside `AsOptionalWrapper`, the error message must be exactly: `"AsOptionalVoid must be used for AsVoid"`
- When checking for double-wrapped optional bridges, the pattern must be: `is AsOptionalWrapper, AsOptionalNothing, AsOptionalVoid -> error`

Additionally, `AsVoid` must not appear in the `TODO("not yet supported")` list within `AsOptionalWrapper`.

## Verification

After implementing the fix:
- Functions returning `Unit?` in Kotlin are correctly bridged to Swift functions returning `Void?`
- Functions accepting `Unit?` in Kotlin are correctly bridged to Swift functions accepting `Void?`
- The type bridging system handles nullable Unit types without generating TODO errors
