# Fix Swift Export Flow with nullable elements

## Problem

Kotlin's Swift export feature has a bug when handling `Flow<T?>` with nullable elements. The `SwiftFlowIterator` class in the coroutine support library cannot properly distinguish between:
1. A null value emitted by the flow
2. The end of the flow (no more values)

Both cases were represented as `null` in the callback type `T?`, causing the flow to terminate prematurely when encountering null elements.

## Expected Behavior

After the fix, a `Flow<Elem?>` that emits `[Element1, null, Element2, null, Element3]` should correctly produce all 5 elements (including the nulls) when consumed from Swift via `asAsyncSequence()`.

## Design Requirements

The protocol between Kotlin and Swift needs to distinguish "a null value in the flow" from "the flow is complete." This requires wrapping values and adding a boolean presence flag to the interop callback.

### Kotlin Bridge (KotlinCoroutineSupport.kt)

The `SwiftFlowIterator` class must include an `inner class Value(val value: T)` to wrap emitted elements. This wrapper separates the two null cases: a null `Value?` means end-of-flow, while a `Value?` with a null `value` field means a null element was emitted.

Expected interface signatures and usage in the Kotlin support file:
- The `next()` function signature must be `public suspend fun next(): Value?`
- In `emit()`, values are wrapped before resuming the continuation: `state.continuation.resume(Value(value))`
- The state machine requires `handleActions<Value>` for consumer/producer await transitions
- In the `SwiftFlowIterator_next` bridge, the `__continuation` callback receives two arguments (a boolean flag and the value):
  - End of flow: `__continuation(false, null)`
  - Has a value: `__continuation(true, _result.value)`
- The function type in the bridge must be `convertBlockPtrToKotlinFunction<(kotlin.Boolean, kotlin.native.internal.NativePtr)->Unit>`

### C Header (KotlinCoroutineSupport.h)

The C header includes `#include <Foundation/Foundation.h>` and is wrapped with `NS_ASSUME_NONNULL_BEGIN` / `NS_ASSUME_NONNULL_END`.

The continuation callback declaration must accept a boolean presence flag alongside the nullable pointer: `int32_t (^continuation)(bool, void * _Nullable )`

### Swift Support (KotlinCoroutineSupport.swift)

The Swift side of the callback must:
- Accept two arguments in the closure: `{ arg0, arg1 in`
- Check the boolean flag before unwrapping: `if arg0 {`
- Pass non-nil values to the async sequence: `continuation(.some(element))`
- Signal end-of-sequence when the flag is false: `continuation(.none)`

### Test Data

Add test coverage for nullable flows in the integration test data files (sequences.kt and sequences.swift):
- A Kotlin function `fun testNullable(): Flow<Elem?> = flowOf(Element1, null, Element2, null, Element3)` returning a flow with interleaved null elements
- A corresponding Swift test function `func testNullable()` that collects elements via `.asAsyncSequence()` into an array and asserts the expected result including nulls

## Code Style Requirements

The Swift support file must pass `swift-format lint` without errors.

## Context

The `SwiftFlowIterator` class implements the producer-consumer pattern for Kotlin Flows exposed to Swift. It uses a state machine with atomic state transitions to coordinate between:
- `State.Ready` — Has a value ready to emit
- `State.AwaitingConsumer` — Waiting for Swift to call next()
- `State.AwaitingProducer` — Waiting for Kotlin flow to emit

## Reference

YouTrack issue: KT-84485
