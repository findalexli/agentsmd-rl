# Swift Export: Support Flow in Contravariant Positions

## Problem

The Swift Export feature in the Kotlin compiler currently only handles `kotlinx.coroutines.flow.Flow<T>` types correctly when they appear in covariant positions (return types). When a `Flow<T>` appears in a contravariant position (function parameter), the export fails or produces incorrect results.

## Affected Files

1. `native/swift/sir-providers/src/org/jetbrains/kotlin/sir/providers/impl/SirTypeProviderImpl.kt`
   - The Flow type interception logic is restricted to covariant positions only
   - The companion object is private, preventing access from other files

2. `native/swift/sir-providers/src/org/jetbrains/kotlin/sir/providers/impl/SirVisibilityCheckerImpl.kt`
   - Flow types are not recognized as supported types in `hasUnboundInputTypeParameters()`

## What Needs to Change

In `SirTypeProviderImpl.kt`:
- Remove the variance position restriction (`ctx.currentPosition == SirTypeVariance.COVARIANT`) from the Flow type interception logic so Flow types are handled in all positions
- Change the companion object from `private` to `internal` to allow `SirVisibilityCheckerImpl` to access `FLOW_CLASS_IDS`

In `SirVisibilityCheckerImpl.kt`:
- Add a check for Flow types using `SirTypeProviderImpl.FLOW_CLASS_IDS` in `hasUnboundInputTypeParameters()` to recognize them as supported types

## How to Verify

After the fix:
- The `sir-providers` module should compile successfully
- Flow types in function parameters should be properly exported to Swift
- The test case with `consume_flow(flow: Flow<Foo>)` should work correctly

## Context

This is part of the Swift Export feature (KT-84226) which enables exporting Kotlin coroutines Flow types to Swift's async sequences. The fix ensures Flow types work consistently whether they are used as return types or function parameters.
