# Swift Export: Don't export protocol members with DeprecationLevel.ERROR

## Problem Description

The Swift Export feature is incorrectly exporting members of Kotlin interfaces (which become Swift protocols) that are marked with `@Deprecated(level = DeprecationLevel.ERROR)`. These members should be marked as unavailable in the generated Swift code.

When a Kotlin interface member has `@Deprecated("message", level = DeprecationLevel.ERROR)`, it means the member is considered an error to use. The Swift Export should:
1. Detect when a declaration is in an interface (protocol)
2. Check if it has `DeprecationLevel.ERROR`
3. Mark it as `SirAvailability.Unavailable` instead of exporting it

## Files to Modify

### 1. SirVisibilityCheckerImpl.kt
**Location:** `native/swift/sir-providers/src/org/jetbrains/kotlin/sir/providers/impl/SirVisibilityCheckerImpl.kt`

This file contains the visibility checking logic. You need to add a check that:
- Gets the `deprecatedAnnotation` level
- Checks if the level is `DeprecationLevel.ERROR`
- Checks if the containing declaration is an `INTERFACE` (using `KaClassKind.INTERFACE`)
- Returns `SirAvailability.Unavailable("Protocol members with DeprecationLevel.ERROR are unsupported")` for such cases

You'll need to import `org.jetbrains.kotlin.analysis.api.components.containingDeclaration` to access the containing declaration.

### 2. SirAttribute.kt
**Location:** `native/swift/sir/src/org/jetbrains/kotlin/sir/SirAttribute.kt`

This file contains the `SirAttribute.Available` class which needs simplification:
- Remove the `obsoleted: Boolean = false` parameter from the constructor
- Update the `require()` calls in `init` to only check `deprecated || unavailable`
- Update the `arguments` list to not include the obsoleted argument
- Update `isUnusable` to only check `unavailable`

## Test Data

The test file at `native/swift/swift-export-standalone-integration-tests/simple/testData/generation/annotations/annotations.kt` has been updated with:
- `InterfaceWithDeprecatedMembers` - interface with various deprecation levels
- `ClassWithDeprecatedMembersFromInterface` - class implementing the interface

The expected golden result files show that `deprecatedErrorFunction` should NOT appear in the generated Swift protocol, but should appear in the class with `@available(*, unavailable, ...)`.

## Expected Behavior

After your fix:
1. Protocol members with `DeprecationLevel.ERROR` are not exported in the Swift protocol
2. Class implementations of such members are marked as unavailable in Swift
3. The `SirAttribute.Available` class no longer has the `obsoleted` parameter
4. All existing tests continue to compile

## References

- YouTrack Issue: KT-84317
- Look at how `DeprecationLevel.HIDDEN` is handled for a similar pattern
- The Analysis API provides `KaClassKind.INTERFACE` to detect interface types
