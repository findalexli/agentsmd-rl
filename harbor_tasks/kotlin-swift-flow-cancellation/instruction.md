# Fix Swift Flow Collection Cancellation

## Problem

The Swift export for Kotlin coroutines Flow has improper cancellation behavior. When collecting a Kotlin `Flow` as a Swift `AsyncSequence`, the flow collection is not properly cancelled in two critical scenarios:

1. **Iterator deinitialization**: When the `KotlinFlowSequence.Iterator` is deallocated, the underlying flow collection continues running instead of being cancelled.

2. **Async task cancellation**: When an async task calling `next()` on the iterator is cancelled, the flow collection is not properly torn down.

This causes flows to continue executing (and potentially emitting values) even after their consumers have been destroyed or their consuming tasks have been cancelled, leading to resource leaks and unexpected behavior.

## Relevant Files

- `native/swift/swift-export-standalone/resources/swift/KotlinCoroutineSupport.kt` - Kotlin side of the flow iterator implementation
- `native/swift/swift-export-standalone/resources/swift/KotlinCoroutineSupport.swift` - Swift side that wraps the Kotlin iterator

## Required Behavior

### Kotlin Side (`KotlinCoroutineSupport.kt`)

The `SwiftFlowIterator` class must:
- Maintain a shared `CoroutineScope` field with a default value (using any appropriate context such as `EmptyCoroutineContext` or `Dispatchers.Default`)
- The `cancel()` method must call `.cancel(CancellationException(...))` on the stored coroutine scope (not call `complete()` directly)
- The `State.Ready` handling block in `next()` must register a cancellation callback using `continuation.invokeOnCancellation { ... }` that calls `cancel()`
- The `State.AwaitingConsumer` handling block in `next()` must similarly register an `invokeOnCancellation` callback that calls `cancel()`
- The `launch()` method must use the stored coroutine scope's `.launch { ... }` rather than creating a new `CoroutineScope` for each invocation

### Swift Side (`KotlinCoroutineSupport.swift`)

The `KotlinFlowSequence` must:
- Have a nested `Iterator` class conforming to `AsyncIteratorProtocol` with a `deinit` that cancels the underlying Kotlin iterator
- The `Iterator.deinit` must call `_kotlin_swift_SwiftFlowIterator_cancel` on the wrapped `KotlinFlowIterator` instance
- The `makeAsyncIterator()` method must return this `Iterator` wrapper type (not a bare `KotlinFlowIterator`)
- The `KotlinFlowIterator` class must have `internal` visibility (not `public`) so only the `Iterator` wrapper is publicly accessible
- The `KotlinFlowIterator` class must NOT have a `deinit` (the cancellation logic belongs in the Swift `Iterator` wrapper)

## Expected Behavior After Fix

- Flow collection stops when the iterator is deallocated
- Flow collection stops when an async call to `next()` is cancelled
- The coroutine scope is properly shared and cancelled as a unit
- No behavioral changes for normal (non-cancelled) flow consumption

## Related

Issue: KT-85159
