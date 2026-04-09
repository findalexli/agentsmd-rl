# Fix Swift Flow Collection Cancellation

## Problem

The Swift export for Kotlin coroutines Flow has improper cancellation behavior. When collecting a Kotlin `Flow` as a Swift `AsyncSequence`, the flow collection is not properly cancelled in two critical scenarios:

1. **Iterator deinitialization**: When the `KotlinFlowSequence.Iterator` is deallocated, the underlying flow collection continues running instead of being cancelled.

2. **Async task cancellation**: When an async task calling `next()` on the iterator is cancelled, the flow collection is not properly torn down.

This causes flows to continue executing (and potentially emitting values) even after their consumers have been destroyed or their consuming tasks have been cancelled, leading to resource leaks and unexpected behavior.

## Relevant Files

- `native/swift/swift-export-standalone/resources/swift/KotlinCoroutineSupport.kt` - Kotlin side of the flow iterator implementation
- `native/swift/swift-export-standalone/resources/swift/KotlinCoroutineSupport.swift` - Swift side that wraps the Kotlin iterator

## Key Components to Modify

### Kotlin Side (`KotlinCoroutineSupport.kt`)

The `SwiftFlowIterator` class needs to:
1. Maintain a `CoroutineScope` that is shared across all flow operations (instead of creating a new scope for `launch()`)
2. Ensure the `cancel()` method cancels this scope to stop flow collection
3. Register cancellation handlers using `invokeOnCancellation` in the two `suspendCancellableCoroutine` blocks (for `State.Ready` and `State.AwaitingConsumer` states) so that coroutine cancellation also triggers flow cancellation

### Swift Side (`KotlinCoroutineSupport.swift`)

The flow sequence implementation needs to:
1. Introduce a new `Iterator` class that wraps `KotlinFlowIterator` and handles cancellation in its `deinit`
2. Make `KotlinFlowIterator` internal (currently public) since it should only be accessed through the new `Iterator` wrapper
3. Move the cancellation logic from `KotlinFlowIterator.deinit` to the new `Iterator.deinit`
4. Have `makeAsyncIterator()` return the new `Iterator` type instead of `KotlinFlowIterator` directly

## Expected Behavior After Fix

- Flow collection stops when the iterator is deallocated
- Flow collection stops when an async call to `next()` is cancelled
- The coroutine scope is properly shared and cancelled as a unit
- No behavioral changes for normal (non-cancelled) flow consumption

## Related

Issue: KT-85159
