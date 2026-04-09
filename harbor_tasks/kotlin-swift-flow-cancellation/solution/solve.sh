#!/bin/bash
set -e

cd /workspace/kotlin

# Check if already applied (idempotency check)
if grep -q "continuation.invokeOnCancellation { cancel() }" native/swift/swift-export-standalone/resources/swift/KotlinCoroutineSupport.kt; then
    echo "Patch already applied, skipping"
    exit 0
fi

# Apply the gold patch
cat <<'PATCH' | git apply -
diff --git a/native/swift/swift-export-standalone/resources/swift/KotlinCoroutineSupport.kt b/native/swift/swift-export-standalone/resources/swift/KotlinCoroutineSupport.kt
index 8469effb6125c..c174721359ca0 100644
--- a/native/swift/swift-export-standalone/resources/swift/KotlinCoroutineSupport.kt
+++ b/native/swift/swift-export-standalone/resources/swift/KotlinCoroutineSupport.kt
@@ -99,6 +99,7 @@ public fun __root___SwiftJob_setCallback(self: kotlin.native.internal.NativePtr,
 @OptIn(kotlin.concurrent.atomics.ExperimentalAtomicApi::class)
 class SwiftFlowIterator<T> private constructor(
     private val state: AtomicReference<SwiftFlowIterator.State>,
+    private val coroutineScope: CoroutineScope = CoroutineScope(EmptyCoroutineContext),
 ): FlowCollector<T> {
     private object Retry
     private class Throw(val exception: Throwable)
@@ -124,7 +125,7 @@ class SwiftFlowIterator<T> private constructor(

     public constructor(flow: Flow<T>) : this(state = AtomicReference(State.Ready<T>(flow)))

-    public fun cancel() = complete(CancellationException("Flow cancelled"))
+    public fun cancel() = coroutineScope.cancel(CancellationException("Flow cancelled"))

     @Suppress("UNCHECKED_CAST")
     public fun complete(error: Throwable?) {
@@ -178,6 +179,7 @@ class SwiftFlowIterator<T> private constructor(
                 is State.Ready<*> -> {
                     val state = state as State.Ready<T>
                     return suspendCancellableCoroutine<Any?> { continuation ->
+                        continuation.invokeOnCancellation { cancel() }
                         val newState = State.AwaitingProducer(continuation)
                         if (!this@SwiftFlowIterator.state.compareAndSet(state, newState)) {
                             continuation.resume(Retry) // state changed; continue the outer loop
@@ -188,6 +190,7 @@ class SwiftFlowIterator<T> private constructor(
                 }
                 is State.AwaitingConsumer -> {
                     return suspendCancellableCoroutine<Any?> { continuation ->
+                        continuation.invokeOnCancellation { cancel() }
                         val newState = State.AwaitingProducer(continuation)
                         if (!this@SwiftFlowIterator.state.compareAndSet(state, newState)) {
                             continuation.resume(Retry) // state changed; continue the outer loop
@@ -205,7 +208,7 @@ class SwiftFlowIterator<T> private constructor(
     }

     private fun launch(flow: Flow<T>) {
-        CoroutineScope(EmptyCoroutineContext).launch {
+        coroutineScope.launch {
             flow
                 .catch { complete(it) }
                 .collect(this@SwiftFlowIterator)
diff --git a/native/swift/swift-export-standalone/resources/swift/KotlinCoroutineSupport.swift b/native/swift/swift-export-standalone/resources/swift/KotlinCoroutineSupport.swift
index ad5e959952103..53795f4038218 100644
--- a/native/swift/swift-export-standalone/resources/swift/KotlinCoroutineSupport.swift
+++ b/native/swift/swift-export-standalone/resources/swift/KotlinCoroutineSupport.swift
@@ -184,8 +184,26 @@ public struct KotlinFlowSequence<Element>: AsyncSequence {
         self.flow = flow
     }

-    public func makeAsyncIterator() -> KotlinFlowIterator<Element> {
-        KotlinFlowIterator<Element>(flow)
+    public final class Iterator: AsyncIteratorProtocol {
+        public typealias Failure = any Error
+
+        private let iterator: KotlinFlowIterator<Element>
+
+        fileprivate init(_ flow: some KotlinFlow) {
+            iterator = KotlinFlowIterator(flow)
+        }
+
+        deinit {
+            _kotlin_swift_SwiftFlowIterator_cancel(iterator.__externalRCRef())
+        }
+
+        public func next() async throws -> Element? {
+            try await iterator.next()
+        }
+    }
+
+    public func makeAsyncIterator() -> Iterator {
+        Iterator(flow)
     }
 }

@@ -194,7 +212,7 @@ public struct KotlinFlowSequence<Element>: AsyncSequence {
 /// ## Discussion
 /// This type is a manually bridged counterpart to SwiftFlowIterator type in Kotlin
 /// It simply maps `next()` calls to its implementation in Kotlin.
-public final class KotlinFlowIterator<Element>: KotlinRuntime.KotlinBase, AsyncIteratorProtocol {
+internal final class KotlinFlowIterator<Element>: KotlinRuntime.KotlinBase, AsyncIteratorProtocol {
     public typealias Failure = any Error

     fileprivate init(_ flow: some KotlinFlow) {
@@ -203,10 +221,6 @@ public final class KotlinFlowIterator<Element>: KotlinRuntime.KotlinBase, AsyncI
         _kotlin_swift_SwiftFlowIterator_init_initialize(__kt, flow.__externalRCRef())
     }

-    deinit {
-        _kotlin_swift_SwiftFlowIterator_cancel(self.__externalRCRef())
-    }
-
     package override init(
         __externalRCRefUnsafe: Swift.UnsafeMutableRawPointer?,
         options: KotlinRuntime.KotlinBaseConstructionOptions
PATCH

echo "Patch applied successfully"
