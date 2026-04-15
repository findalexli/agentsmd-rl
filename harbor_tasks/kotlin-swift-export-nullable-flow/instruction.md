# Support Flow with nullable elements in Swift Export

## Problem

The Kotlin Swift Export feature currently does not properly support `Flow` types with nullable elements (e.g., `Flow<Elem?>`). When a Kotlin Flow emits null values, the interop layer between Kotlin coroutines and Swift async sequences cannot distinguish between:

1. A null value that was intentionally emitted by the flow
2. A null return indicating the flow has completed

This causes issues when iterating over Kotlin Flows with nullable element types from Swift code.

Related issue: KT-84485

## Files

The interop layer between Kotlin coroutines and Swift async sequences lives in:
- `native/swift/swift-export-standalone/resources/swift/KotlinCoroutineSupport.h` — C header defining the interop signatures
- `native/swift/swift-export-standalone/resources/swift/KotlinCoroutineSupport.kt` — Kotlin implementation of the flow iterator
- `native/swift/swift-export-standalone/resources/swift/KotlinCoroutineSupport.swift` — Swift side of the async sequence adapter

Test data:
- `native/swift/swift-export-standalone-integration-tests/coroutines/testData/execution/sequences/sequences.kt`
- `native/swift/swift-export-standalone-integration-tests/coroutines/testData/execution/sequences/sequences.swift`

## Existing Codebase Context

The codebase already contains these types and functions that must be preserved:

**Kotlin (`KotlinCoroutineSupport.kt`):**
- `class SwiftFlowIterator<T>` implementing `FlowCollector<T>` with methods `suspend fun next()` and `fun cancel()`
- `class SwiftJob` with `cancellationCallback`
- `@ExportedBridge` functions: `_kotlin_swift_SwiftFlowIterator_init_allocate`, `_kotlin_swift_SwiftFlowIterator_init_initialize`, `SwiftFlowIterator_next`, `SwiftFlowIterator_cancel`

**Header (`KotlinCoroutineSupport.h`):**
- Uses `NS_ASSUME_NONNULL_BEGIN` / `NS_ASSUME_NONNULL_END` guards
- Declares `_kotlin_swift_SwiftFlowIterator_next` with a `continuation` callback parameter, `_kotlin_swift_SwiftFlowIterator_cancel`, and `_kotlin_swift_SwiftFlowIterator_init_allocate`

**Swift (`KotlinCoroutineSupport.swift`):**
- Imports `KotlinRuntime` and `KotlinRuntimeSupport`
- `class KotlinFlowIterator<Element>` conforming to `AsyncIteratorProtocol` with `public func next()`
- `struct KotlinFlowSequence<Element>` conforming to `AsyncSequence` with `makeAsyncIterator`
- `class KotlinTask` with `cancelExternally` method

**Test data (`sequences.kt` / `sequences.swift`):**
- Existing test functions: `testRegular()`, `testEmpty()`, `testString()`
- Uses `Flow<Elem>` type

## Symptom

The Kotlin-to-Swift flow interop uses a callback-based protocol: when the Kotlin side calls the continuation callback with a value, the Swift side receives it; when the Kotlin side passes null, the Swift side interprets it as flow completion. However, for nullable element types (`Flow<Elem?>`), the Kotlin side legitimately emits null as an element value — and the current protocol has no way to convey "this null is an element, not completion" versus "this null means the flow is done."

Concretely, iterating `flowOf(Element1, null, Element2, null, Element3)` from Swift does not yield the five expected elements (`Element1`, `nil`, `Element2`, `nil`, `Element3`). Instead, null emitted values are misinterpreted as flow completion, terminating iteration prematurely.

All three interop files (`.h`, `.kt`, `.swift`) participate in this callback protocol and must be updated to resolve the ambiguity between emitted nulls and flow completion.

## Expected Behavior

When a Kotlin `Flow<Elem?>` emits null values, the Swift async sequence should properly yield `nil` elements to the Swift consumer. For example, a flow emitting `[Element1, null, Element2, null, Element3]` should be consumable from Swift and result in an array `[Element1.shared, nil, Element2.shared, nil, Element3.shared]`.

## Test Data Requirements

Add the following test cases to validate nullable Flow support:

In `sequences.kt`:
- A function `fun testNullable(): Flow<Elem?>` that returns a flow emitting interspersed elements and nulls (specifically `flowOf(Element1, null, Element2, null, Element3)`)

In `sequences.swift`:
- A function `func testNullable() async` annotated with `@Test` and `@MainActor`
- This test should declare an array of type `[Elem?]` and verify it equals `[Element1.shared, nil, Element2.shared, nil, Element3.shared]`
