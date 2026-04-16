# Fix Swift Export Flow with nullable elements

## Problem

Kotlin's Swift export feature has a bug when handling `Flow<T?>` with nullable elements. The `SwiftFlowIterator` class in the coroutine support library cannot properly distinguish between:
1. A null value emitted by the flow
2. The end of the flow (no more values)

Both cases were represented as `null` in the callback type `T?`, causing the flow to terminate prematurely when encountering null elements.

## Affected Files

The fix needs to modify these files in `native/swift/swift-export-standalone/resources/swift/`:

1. **KotlinCoroutineSupport.kt** - Core Kotlin implementation
2. **KotlinCoroutineSupport.h** - C header for interop
3. **KotlinCoroutineSupport.swift** - Swift implementation

And test files in `native/swift/swift-export-standalone-integration-tests/coroutines/testData/execution/sequences/`:

4. **sequences.kt** - Add test for nullable flow
5. **sequences.swift** - Add Swift test for nullable flow

## Expected Behavior

After the fix, a `Flow<Elem?>` that emits `[Element1, null, Element2, null, Element3]` should correctly produce all 5 elements (including the nulls) when consumed from Swift via `asAsyncSequence()`.

## Implementation Requirements

The solution requires changing the callback protocol between Kotlin and Swift to use a boolean flag to indicate whether a value is present:

### KotlinCoroutineSupport.kt

Must include:
- An inner class named `Value` with a constructor parameter `val value: T`
- The `next()` function must have return type `Value?`
- The `emit()` function must call `state.continuation.resume(Value(value))`
- At least 2 calls to `handleActions<Value>` for state machine value handling
- In the C bridge function `SwiftFlowIterator_next`, calls to `__continuation` must pass two arguments: a boolean flag and the value
- When the result is null (end of flow), call `__continuation(false, null)`
- When the result has a value, call `__continuation(true, _result.value)`
- The `convertBlockPtrToKotlinFunction` type must include `kotlin.Boolean` as the first parameter: `convertBlockPtrToKotlinFunction<(kotlin.Boolean, kotlin.native.internal.NativePtr)->Unit>`

### KotlinCoroutineSupport.h

Must include:
- The continuation callback signature with a boolean parameter: `int32_t (^continuation)(bool, void * _Nullable )`

### KotlinCoroutineSupport.swift

Must include:
- A callback closure that accepts two arguments named `arg0` and `arg1`: `{ arg0, arg1 in`
- Check the boolean flag `arg0` before unwrapping the value: `if arg0 {`
- When the flag is true, pass the value via `continuation(.some(element))`
- When the flag is false, pass nil via `continuation(.none)`

## Context

The `SwiftFlowIterator` class implements the producer-consumer pattern for Kotlin Flows exposed to Swift. It uses a state machine with atomic state transitions to coordinate between:
- `State.Ready` - Has a value ready to emit
- `State.AwaitingConsumer` - Waiting for Swift to call next()
- `State.AwaitingProducer` - Waiting for Kotlin flow to emit

The issue is in how `null` values are handled - the protocol needs to distinguish "here's a null value" from "flow is complete".

## Reference

YouTrack issue: KT-84485
