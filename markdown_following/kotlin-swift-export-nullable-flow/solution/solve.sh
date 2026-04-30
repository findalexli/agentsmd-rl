#!/bin/bash
set -e

cd /workspace/kotlin

# Apply the gold patch for nullable Flow support
cat <<'PATCH' | git apply -
diff --git a/native/swift/swift-export-standalone-integration-tests/coroutines/testData/execution/sequences/sequences.kt b/native/swift/swift-export-standalone-integration-tests/coroutines/testData/execution/sequences/sequences.kt
index aa596bf2b31c8..67ca1c6c5dc76 100644
--- a/native/swift/swift-export-standalone-integration-tests/coroutines/testData/execution/sequences/sequences.kt
+++ b/native/swift/swift-export-standalone-integration-tests/coroutines/testData/execution/sequences/sequences.kt
@@ -27,6 +27,8 @@ object CurrentSubject {

 fun testRegular(): Flow<Elem> = flowOf(Element1, Element2, Element3)

+fun testNullable(): Flow<Elem?> = flowOf(Element1, null, Element2, null, Element3)
+
 fun testEmpty(): Flow<Elem> = flowOf()

 fun testString(): Flow<String> = flowOf("hello", "any", "world")
diff --git a/native/swift/swift-export-standalone-integration-tests/coroutines/testData/execution/sequences/sequences.swift b/native/swift/swift-export-standalone-integration-tests/coroutines/testData/execution/sequences/sequences.swift
index 1b253423149c0..43361be040211 100644
--- a/native/swift/swift-export-standalone-integration-tests/coroutines/testData/execution/sequences/sequences.swift
+++ b/native/swift/swift-export-standalone-integration-tests/coroutines/testData/execution/sequences/sequences.swift
@@ -22,6 +22,25 @@ func testRegular() async {
     #expect(actual == .success(expected))
 }

+@Test
+@MainActor
+func testNullable() async {
+    let expected: [Elem?] = [Element1.shared, nil, Element2.shared, nil, Element3.shared]
+
+    let task = Task<[Elem?], any Error>.detached {
+        var actual: [Elem?] = []
+        for try await element in testNullable().asAsyncSequence() {
+            actual.append(element)
+        }
+        return actual
+    }
+
+    let actual = await task.result
+
+    #expect(!task.isCancelled)
+    #expect(actual == .success(expected))
+}
+
 @Test
 @MainActor
 func testString() async {
diff --git a/native/swift/swift-export-standalone/resources/swift/KotlinCoroutineSupport.h b/native/swift/swift-export-standalone/resources/swift/KotlinCoroutineSupport.h
index 9a91cfd60ef7b..3bab2f1334aa2 100644
--- a/native/swift/swift-export-standalone/resources/swift/KotlinCoroutineSupport.h
+++ b/native/swift/swift-export-standalone/resources/swift/KotlinCoroutineSupport.h
@@ -11,7 +11,7 @@ void __root___SwiftJob_cancelExternally(void *);

 void _kotlin_swift_SwiftFlowIterator_cancel(void * self);

-void _kotlin_swift_SwiftFlowIterator_next(void * self, int32_t (^continuation)(void * _Nullable ), int32_t (^exception)(void * _Nullable ), void * cancellation);
+void _kotlin_swift_SwiftFlowIterator_next(void * self, int32_t (^continuation)(bool, void * _Nullable ), int32_t (^exception)(void * _Nullable ), void * cancellation);

 void *_kotlin_swift_SwiftFlowIterator_init_allocate();

diff --git a/native/swift/swift-export-standalone/resources/swift/KotlinCoroutineSupport.kt b/native/swift/swift-export-standalone/resources/swift/KotlinCoroutineSupport.kt
index f050d9c5669a7..8469effb6125c 100644
--- a/native/swift/swift-export-standalone/resources/swift/KotlinCoroutineSupport.kt
+++ b/native/swift/swift-export-standalone/resources/swift/KotlinCoroutineSupport.kt
@@ -102,6 +102,7 @@ class SwiftFlowIterator<T> private constructor(
 ): FlowCollector<T> {
     private object Retry
     private class Throw(val exception: Throwable)
+    inner class Value(val value: T)

     private sealed interface State {
         // State transitions:
@@ -158,7 +159,7 @@ class SwiftFlowIterator<T> private constructor(
                         if (!this@SwiftFlowIterator.state.compareAndSet(state, newState)) {
                             continuation.resume(Retry) // state changed; continue the outer loop
                         } else {
-                            state.continuation.resume(value) // continue the consumer
+                            state.continuation.resume(Value(value)) // continue the consumer
                         }
                     }.handleActions<Unit> { continue@loop }
                 }
@@ -171,7 +172,7 @@ class SwiftFlowIterator<T> private constructor(
     }

     @Suppress("UNCHECKED_CAST")
-    public suspend fun next(): T? {
+    public suspend fun next(): Value? {
         loop@while (true) {
             when (val state = this@SwiftFlowIterator.state.load()) {
                 is State.Ready<*> -> {
@@ -183,7 +184,7 @@ class SwiftFlowIterator<T> private constructor(
                         } else {
                             this.launch(state.flow)
                         }
-                    }?.handleActions<T> { continue@loop }
+                    }?.handleActions<Value> { continue@loop }
                 }
                 is State.AwaitingConsumer -> {
                     return suspendCancellableCoroutine<Any?> { continuation ->
@@ -193,7 +194,7 @@ class SwiftFlowIterator<T> private constructor(
                         } else {
                             state.continuation.resume(Unit) // continue the producer
                         }
-                    }?.handleActions<T> { continue@loop }
+                    }?.handleActions<Value> { continue@loop }
                 }
                 is State.AwaitingProducer -> {
                     error("KotlinFlowIterator doesn't support concurrent receivers")
@@ -233,9 +234,10 @@ public fun SwiftFlowIterator_cancel(self: kotlin.native.internal.NativePtr): Uni
 public fun SwiftFlowIterator_next(self: kotlin.native.internal.NativePtr, continuation: kotlin.native.internal.NativePtr, exception: kotlin.native.internal.NativePtr, cancellation: kotlin.native.internal.NativePtr): Unit {
     val __self = kotlin.native.internal.ref.dereferenceExternalRCRef(self) as SwiftFlowIterator<kotlin.Any?>
     val __continuation = run {
-        val kotlinFun = convertBlockPtrToKotlinFunction<(kotlin.native.internal.NativePtr)->Unit>(continuation);
-        { arg0: kotlin.Any? ->
-            val _result = kotlinFun(if (arg0 == null) kotlin.native.internal.NativePtr.NULL else kotlin.native.internal.ref.createRetainedExternalRCRef(arg0))
+        val kotlinFun = convertBlockPtrToKotlinFunction<(kotlin.Boolean, kotlin.native.internal.NativePtr)->Unit>(continuation);
+        { arg0: kotlin.Boolean, arg1: kotlin.Any? ->
+            val _arg1 = if (arg1 == null) kotlin.native.internal.NativePtr.NULL else kotlin.native.internal.ref.createRetainedExternalRCRef(arg1)
+            val _result = kotlinFun(arg0, _arg1)
             _result
         }
     }
@@ -250,7 +252,11 @@ public fun SwiftFlowIterator_next(self: kotlin.native.internal.NativePtr, contin
     CoroutineScope(__cancellation + Dispatchers.Default).launch(start = CoroutineStart.UNDISPATCHED) {
         try {
             val _result = __self.next()
-            __continuation(_result)
+            if (_result == null) {
+                __continuation(false, null)
+            } else {
+                __continuation(true, _result.value)
+            }
         } catch (error: CancellationException) {
             __cancellation.cancel()
             __exception(null)
@@ -272,4 +278,4 @@ public fun __root___SwiftFlowIterator_init_initialize__TypesOfArguments__Swift_U
     val ____kt = kotlin.native.internal.ref.dereferenceExternalRCRef(__kt)!!
     val __flow = kotlin.native.internal.ref.dereferenceExternalRCRef(flow) as kotlinx.coroutines.flow.Flow<kotlin.Any?>
     kotlin.native.internal.initInstance(____kt, SwiftFlowIterator<kotlin.Any?>(__flow))
-}
\ No newline at end of file
+}
diff --git a/native/swift/swift-export-standalone/resources/swift/KotlinCoroutineSupport.swift b/native/swift/swift-export-standalone/resources/swift/KotlinCoroutineSupport.swift
index 913a3ec294919..a9b91d6764981 100644
--- a/native/swift/swift-export-standalone/resources/swift/KotlinCoroutineSupport.swift
+++ b/native/swift/swift-export-standalone/resources/swift/KotlinCoroutineSupport.swift
@@ -162,9 +162,14 @@ public final class KotlinFlowIterator<Element>: KotlinRuntime.KotlinBase, AsyncI
                         }
                         cancellation = KotlinCoroutineSupport.KotlinTask(currentTask!)

-                        let _: () = _kotlin_swift_SwiftFlowIterator_next(self.__externalRCRef(), { arg0 in
+                        let _: () = _kotlin_swift_SwiftFlowIterator_next(self.__externalRCRef(), { arg0, arg1 in
                                 return {
-                                    continuation(arg0.flatMap(KotlinRuntime.KotlinBase.__createBridgeable(externalRCRef:)) as! Element?);
+                                    if arg0 {
+                                        let element = arg1.flatMap(KotlinRuntime.KotlinBase.__createBridgeable(externalRCRef:)) as! Element
+                                        continuation(.some(element))
+                                    } else {
+                                        continuation(.none)
+                                    }
                                     return 0
                                 }()
                         }, { arg0 in
PATCH

echo "Patch applied successfully"
