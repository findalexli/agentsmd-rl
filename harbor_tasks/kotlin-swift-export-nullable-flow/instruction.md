# Support Flow with nullable elements in Swift Export

## Problem

The Kotlin Swift Export feature currently does not properly support `Flow` types with nullable elements (e.g., `Flow<Elem?>`). When a Kotlin Flow emits null values, the interop layer between Kotlin coroutines and Swift async sequences cannot distinguish between:

1. A null value that was intentionally emitted by the flow
2. A null return indicating the flow has completed

This causes issues when iterating over Kotlin Flows with nullable element types from Swift code.

## Files to Modify

The interop layer between Kotlin coroutines and Swift async sequences lives in these files:

1. `native/swift/swift-export-standalone/resources/swift/KotlinCoroutineSupport.h` - C header defining the interop signatures
2. `native/swift/swift-export-standalone/resources/swift/KotlinCoroutineSupport.kt` - Kotlin implementation of the flow iterator
3. `native/swift/swift-export-standalone/resources/swift/KotlinCoroutineSupport.swift` - Swift side of the async sequence adapter

## Test Files (for reference)

Test data is in:
- `native/swift/swift-export-standalone-integration-tests/coroutines/testData/execution/sequences/sequences.kt`
- `native/swift/swift-export-standalone-integration-tests/coroutines/testData/execution/sequences/sequences.swift`

## Expected Behavior

When a Kotlin `Flow<Elem?>` emits null values, the Swift async sequence should properly yield `nil` elements to the Swift consumer. For example, a flow emitting `[Element1, null, Element2, null, Element3]` should be consumable from Swift as an array `[Element1.shared, nil, Element2.shared, nil, Element3.shared]`.

## Hints

The fix requires changing the callback signature to include a boolean flag that indicates whether a value is present, allowing the consumer to distinguish between:
- `true, value` - a value (which may be null) is present
- `false, null` - the flow has completed

This affects both the Kotlin side (which produces values) and the Swift side (which consumes them).

## Related Issue

KT-84485
