# Swift Export: Support nullable Unit/Void types

## Problem

The Kotlin compiler's Swift Export feature does not properly handle nullable Unit types (`Unit?`). When exporting Kotlin functions that return `Unit?` or accept `Unit?` parameters to Swift, the type bridging system currently produces incorrect results.

When an `AsVoid` type (representing non-nullable `Unit`) is encountered inside an `Optional` wrapper, the system does not have proper handling and may generate a `TODO("not yet supported")` error.

## Required Changes

After your fix, the following specific strings must be present in `TypeBridging.kt`:

### Bridge Type Definition

A new bridge definition must exist with these exact properties:
- Named: `AsOptionalVoid`
- Swift type expression: `SirNominalType(SirSwiftModule.optional, listOf(SirNominalType(SirSwiftModule.void)))`
- Kotlin type: `KotlinType.Boolean`
- C type: `CType.Bool`

### Value Conversion Expressions

The bridge must implement value conversions with these exact expressions:

**For Kotlin sources (`inKotlinSources`):**
- `swiftToKotlin` must return: `(if ($valueExpression) Unit else null)`
- `kotlinToSwift` must return: `($valueExpression != null)`

**For Swift sources (`inSwiftSources`):**
- `swiftToKotlin` must return: `($valueExpression != nil)`
- `kotlinToSwift` must return: `($valueExpression ? () : nil)`

### Bridge Selection Logic

The `bridgeNominalType` function must contain this pattern when handling Optional wrappers:
- `is AsVoid -> AsOptionalVoid`

### NS Collection Bridging

The `bridgeAsNSCollectionElement` function must contain:
- `is AsOptionalVoid -> AsObjCBridgedOptional(bridge.swiftType)`

### Error Messages

The following error handling patterns must exist:
- When `AsVoid` is incorrectly used inside `AsOptionalWrapper`, the error message must be: `"AsOptionalVoid must be used for AsVoid"`
- When checking for double-wrapped optional bridges, the pattern must be: `is AsOptionalWrapper, AsOptionalNothing, AsOptionalVoid -> error`

Additionally, `AsVoid` must not appear in the `TODO("not yet supported")` list within `AsOptionalWrapper`.

## Verification

After implementing the fix:
- Functions returning `Unit?` in Kotlin are correctly bridged to Swift functions returning `Void?`
- Functions accepting `Unit?` in Kotlin are correctly bridged to Swift functions accepting `Void?`
- The type bridging system handles nullable Unit types without generating TODO errors
