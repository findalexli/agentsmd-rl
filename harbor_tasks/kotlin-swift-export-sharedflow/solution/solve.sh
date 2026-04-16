#!/bin/bash
set -e

cd /workspace/kotlin

# Check if already applied (idempotency check)
if grep -q "kotlinTypedMutableSharedFlowImpl" native/swift/sir-providers/src/org/jetbrains/kotlin/sir/providers/utils/KotlinRuntimeModule.kt 2>/dev/null; then
    echo "Patch already applied, skipping"
    exit 0
fi

# Apply the gold patch
git apply <<'PATCH'
diff --git a/native/swift/sir-light-classes/src/org/jetbrains/sir/lightclasses/nodes/SirProtocolFromKtSymbol.kt b/native/swift/sir-light-classes/src/org/jetbrains/sir/lightclasses/nodes/SirProtocolFromKtSymbol.kt
index 29485fa81bbfd..afe805787540f 100644
--- a/native/swift/sir-light-classes/src/org/jetbrains/sir/lightclasses/nodes/SirProtocolFromKtSymbol.kt
+++ b/native/swift/sir-light-classes/src/org/jetbrains/sir/lightclasses/nodes/SirProtocolFromKtSymbol.kt
@@ -403,14 +403,22 @@ internal class SirFlowFromKtSymbol(

     internal companion object {
         val FLOW_CLASS_ID = ClassId.fromString("kotlinx/coroutines/flow/Flow")
+        val SHARED_FLOW_CLASS_ID = ClassId.fromString("kotlinx/coroutines/flow/SharedFlow")
+        val MUTABLE_SHARED_FLOW_CLASS_ID = ClassId.fromString("kotlinx/coroutines/flow/MutableSharedFlow")
         val STATE_FLOW_CLASS_ID = ClassId.fromString("kotlinx/coroutines/flow/StateFlow")
         val MUTABLE_STATE_FLOW_CLASS_ID = ClassId.fromString("kotlinx/coroutines/flow/MutableStateFlow")

-        val CLASS_IDS = listOf(FLOW_CLASS_ID, STATE_FLOW_CLASS_ID, MUTABLE_STATE_FLOW_CLASS_ID)
+        val CLASS_IDS = listOf(
+            FLOW_CLASS_ID,
+            SHARED_FLOW_CLASS_ID, MUTABLE_SHARED_FLOW_CLASS_ID,
+            STATE_FLOW_CLASS_ID, MUTABLE_STATE_FLOW_CLASS_ID,
+        )
     }

     private val supportProtocol = when (ktSymbol.classId) {
         FLOW_CLASS_ID -> KotlinCoroutineSupportModule.kotlinFlow
+        SHARED_FLOW_CLASS_ID -> KotlinCoroutineSupportModule.kotlinSharedFlow
+        MUTABLE_SHARED_FLOW_CLASS_ID -> KotlinCoroutineSupportModule.kotlinMutableSharedFlow
         STATE_FLOW_CLASS_ID -> KotlinCoroutineSupportModule.kotlinStateFlow
         MUTABLE_STATE_FLOW_CLASS_ID -> KotlinCoroutineSupportModule.kotlinMutableStateFlow
         else -> throw IllegalArgumentException("Unsupported flow kind: ${ktSymbol.classId}")
diff --git a/native/swift/sir-providers/src/org/jetbrains/kotlin/sir/providers/impl/BridgeProvider/TypeBridging.kt b/native/swift/sir-providers/src/org/jetbrains/kotlin/sir/providers/impl/BridgeProvider/TypeBridging.kt
index 47d4f3a733eeb..cfacba2c84d05 100644
--- a/native/swift/sir-providers/src/org/jetbrains/kotlin/sir/providers/impl/BridgeProvider/TypeBridging.kt
+++ b/native/swift/sir-providers/src/org/jetbrains/kotlin/sir/providers/impl/BridgeProvider/TypeBridging.kt
@@ -488,6 +488,8 @@ internal sealed class Bridge(
         private val structType = SirNominalType(
             typeDeclaration = when (swiftType.typedProtocol) {
                 KotlinCoroutineSupportModule.kotlinTypedFlow -> KotlinCoroutineSupportModule.kotlinTypedFlowImpl
+                KotlinCoroutineSupportModule.kotlinTypedSharedFlow -> KotlinCoroutineSupportModule.kotlinTypedSharedFlowImpl
+                KotlinCoroutineSupportModule.kotlinTypedMutableSharedFlow -> KotlinCoroutineSupportModule.kotlinTypedMutableSharedFlowImpl
                 KotlinCoroutineSupportModule.kotlinTypedStateFlow -> KotlinCoroutineSupportModule.kotlinTypedStateFlowImpl
                 KotlinCoroutineSupportModule.kotlinTypedMutableStateFlow -> KotlinCoroutineSupportModule.kotlinTypedMutableStateFlowImpl
                 else -> error("Unsupported typed flow type: ${swiftType.typedProtocol}")
diff --git a/native/swift/sir-providers/src/org/jetbrains/kotlin/sir/providers/impl/SirTypeProviderImpl.kt b/native/swift/sir-providers/src/org/jetbrains/kotlin/sir/providers/impl/SirTypeProviderImpl.kt
index dc17fe1461c1a..991dea8b8fb39 100644
--- a/native/swift/sir-providers/src/org/jetbrains/kotlin/sir/providers/impl/SirTypeProviderImpl.kt
+++ b/native/swift/sir-providers/src/org/jetbrains/kotlin/sir/providers/impl/SirTypeProviderImpl.kt
@@ -95,6 +95,8 @@ public class SirTypeProviderImpl(
                                     if (translatedElement !is SirErrorType && translatedElement !is SirUnsupportedType) {
                                         return@withSessions SirTypedFlowType(
                                             typedProtocol = when (kaType.classId) {
+                                                SHARED_FLOW_CLASS_ID -> KotlinCoroutineSupportModule.kotlinTypedSharedFlow
+                                                MUTABLE_SHARED_FLOW_CLASS_ID -> KotlinCoroutineSupportModule.kotlinTypedMutableSharedFlow
                                                 STATE_FLOW_CLASS_ID -> KotlinCoroutineSupportModule.kotlinTypedStateFlow
                                                 MUTABLE_STATE_FLOW_CLASS_ID -> KotlinCoroutineSupportModule.kotlinTypedMutableStateFlow
                                                 else -> KotlinCoroutineSupportModule.kotlinTypedFlow
@@ -265,10 +267,16 @@ public class SirTypeProviderImpl(

     internal companion object {
         val FLOW_CLASS_ID = ClassId.fromString("kotlinx/coroutines/flow/Flow")
+        val SHARED_FLOW_CLASS_ID = ClassId.fromString("kotlinx/coroutines/flow/SharedFlow")
+        val MUTABLE_SHARED_FLOW_CLASS_ID = ClassId.fromString("kotlinx/coroutines/flow/MutableSharedFlow")
         val STATE_FLOW_CLASS_ID = ClassId.fromString("kotlinx/coroutines/flow/StateFlow")
         val MUTABLE_STATE_FLOW_CLASS_ID = ClassId.fromString("kotlinx/coroutines/flow/MutableStateFlow")

-        val FLOW_CLASS_IDS = listOf(FLOW_CLASS_ID, STATE_FLOW_CLASS_ID, MUTABLE_STATE_FLOW_CLASS_ID)
+        val FLOW_CLASS_IDS = listOf(
+            FLOW_CLASS_ID,
+            SHARED_FLOW_CLASS_ID, MUTABLE_SHARED_FLOW_CLASS_ID,
+            STATE_FLOW_CLASS_ID, MUTABLE_STATE_FLOW_CLASS_ID,
+        )
     }
 }

diff --git a/native/swift/sir-providers/src/org/jetbrains/kotlin/sir/providers/impl/StandaloneSirTypeNamer.kt b/native/swift/sir-providers/src/org/jetbrains/kotlin/sir/providers/impl/StandaloneSirTypeNamer.kt
index 22bf4689158aa..a1ee022591b30 100644
--- a/native/swift/sir-providers/src/org/jetbrains/kotlin/sir/providers/impl/StandaloneSirTypeNamer.kt
+++ b/native/swift/sir-providers/src/org/jetbrains/kotlin/sir/providers/impl/StandaloneSirTypeNamer.kt
@@ -65,6 +65,8 @@ internal object StandaloneSirTypeNamer : SirTypeNamer {
         is SirNominalType -> kotlinFqName(type)
         is SirTypedFlowType -> when (type.typedProtocol) {
             KotlinCoroutineSupportModule.kotlinTypedFlow -> "kotlinx.coroutines.flow.Flow<${kotlinParametrizedName(type.elementType)}>"
+            KotlinCoroutineSupportModule.kotlinTypedSharedFlow -> "kotlinx.coroutines.flow.SharedFlow<${kotlinParametrizedName(type.elementType)}>"
+            KotlinCoroutineSupportModule.kotlinTypedMutableSharedFlow -> "kotlinx.coroutines.flow.MutableSharedFlow<${kotlinParametrizedName(type.elementType)}>"
             KotlinCoroutineSupportModule.kotlinTypedStateFlow -> "kotlinx.coroutines.flow.StateFlow<${kotlinParametrizedName(type.elementType)}>"
             KotlinCoroutineSupportModule.kotlinTypedMutableStateFlow -> "kotlinx.coroutines.flow.MutableStateFlow<${kotlinParametrizedName(type.elementType)}>"
             else -> error("TypedFlowType $type can not be named")
diff --git a/native/swift/sir-providers/src/org/jetbrains/kotlin/sir/providers/utils/KotlinRuntimeModule.kt b/native/swift/sir-providers/src/org/jetbrains/kotlin/sir/providers/utils/KotlinRuntimeModule.kt
index 7751893815c20..d9c96a4deb1cf 100644
--- a/native/swift/sir-providers/src/org/jetbrains/kotlin/sir/providers/utils/KotlinRuntimeModule.kt
+++ b/native/swift/sir-providers/src/org/jetbrains/kotlin/sir/providers/utils/KotlinRuntimeModule.kt
@@ -138,6 +138,42 @@ public object KotlinCoroutineSupportModule : SirModule() {
         visibility = SirVisibility.PUBLIC
     }.initializeParentForSelfAndChildren(KotlinCoroutineSupportModule)

+    public val kotlinSharedFlow: SirProtocol = buildProtocol {
+        origin = KotlinRuntimeElement()
+        name = "KotlinSharedFlow"
+        visibility = SirVisibility.PUBLIC
+    }.initializeParentForSelfAndChildren(KotlinCoroutineSupportModule)
+
+    public val kotlinTypedSharedFlow: SirProtocol = buildProtocol {
+        origin = KotlinRuntimeElement()
+        name = "KotlinTypedSharedFlow"
+        visibility = SirVisibility.PUBLIC
+    }.initializeParentForSelfAndChildren(KotlinCoroutineSupportModule)
+
+    public val kotlinTypedSharedFlowImpl: SirStruct = buildStruct {
+        origin = KotlinRuntimeElement()
+        name = "_KotlinTypedSharedFlowImpl"
+        visibility = SirVisibility.PUBLIC
+    }.initializeParentForSelfAndChildren(KotlinCoroutineSupportModule)
+
+    public val kotlinMutableSharedFlow: SirProtocol = buildProtocol {
+        origin = KotlinRuntimeElement()
+        name = "KotlinMutableSharedFlow"
+        visibility = SirVisibility.PUBLIC
+    }.initializeParentForSelfAndChildren(KotlinCoroutineSupportModule)
+
+    public val kotlinTypedMutableSharedFlow: SirProtocol = buildProtocol {
+        origin = KotlinRuntimeElement()
+        name = "KotlinTypedMutableSharedFlow"
+        visibility = SirVisibility.PUBLIC
+    }.initializeParentForSelfAndChildren(KotlinCoroutineSupportModule)
+
+    public val kotlinTypedMutableSharedFlowImpl: SirStruct = buildStruct {
+        origin = KotlinRuntimeElement()
+        name = "_KotlinTypedMutableSharedFlowImpl"
+        visibility = SirVisibility.PUBLIC
+    }.initializeParentForSelfAndChildren(KotlinCoroutineSupportModule)
+
     public val kotlinStateFlow: SirProtocol = buildProtocol {
         origin = KotlinRuntimeElement()
         name = "KotlinStateFlow"
diff --git a/native/swift/swift-export-standalone/resources/swift/KotlinCoroutineSupport.swift b/native/swift/swift-export-standalone/resources/swift/KotlinCoroutineSupport.swift
index a9b91d6764981..ad5e959952103 100644
--- a/native/swift/swift-export-standalone/resources/swift/KotlinCoroutineSupport.swift
+++ b/native/swift/swift-export-standalone/resources/swift/KotlinCoroutineSupport.swift
@@ -68,11 +68,68 @@ public struct _KotlinTypedFlowImpl<Element>: KotlinTypedFlow {
     }
 }

-public protocol KotlinStateFlow: KotlinFlow {
+public protocol KotlinSharedFlow: KotlinFlow {
+    var replayCache: [(any KotlinRuntimeSupport._KotlinBridgeable)?] { get }
+}
+
+public protocol KotlinTypedSharedFlow<Element>: KotlinTypedFlow { }
+
+extension KotlinTypedSharedFlow {
+    public var wrapped: any KotlinSharedFlow { _flow as! (any KotlinSharedFlow) }
+
+    public var replayCache: [Element] { wrapped.replayCache as! [Element] }
+}
+
+public struct _KotlinTypedSharedFlowImpl<Element>: KotlinTypedSharedFlow {
+    public let _flow: any KotlinFlow
+
+    public init(_ flow: any KotlinSharedFlow) {
+        self._flow = flow
+    }
+}
+
+public protocol KotlinMutableSharedFlow: KotlinSharedFlow {
+    var subscriptionCount: any KotlinTypedStateFlow<Int32> { get }
+    func emit(value: (any KotlinRuntimeSupport._KotlinBridgeable)?) async throws
+    func resetReplayCache()
+    func tryEmit(value: (any KotlinRuntimeSupport._KotlinBridgeable)?) -> Bool
+}
+
+public protocol KotlinTypedMutableSharedFlow<Element>: KotlinTypedSharedFlow { }
+
+extension KotlinTypedMutableSharedFlow {
+    public var wrapped: any KotlinMutableSharedFlow { _flow as! (any KotlinMutableSharedFlow) }
+
+    public var subscriptionCount: any KotlinTypedStateFlow<Int32> {
+        wrapped.subscriptionCount
+    }
+
+    public func emit(value: Element) async throws {
+        try await wrapped.emit(value: value as! (any KotlinRuntimeSupport._KotlinBridgeable)?)
+    }
+
+    public func resetReplayCache() {
+        wrapped.resetReplayCache()
+    }
+
+    public func tryEmit(value: Element) -> Bool {
+        wrapped.tryEmit(value: value as! (any KotlinRuntimeSupport._KotlinBridgeable)?)
+    }
+}
+
+public struct _KotlinTypedMutableSharedFlowImpl<Element>: KotlinTypedMutableSharedFlow {
+    public let _flow: any KotlinFlow
+
+    public init(_ flow: any KotlinMutableSharedFlow) {
+        self._flow = flow
+    }
+}
+
+public protocol KotlinStateFlow: KotlinSharedFlow {
     var value: (any KotlinRuntimeSupport._KotlinBridgeable)? { get }
 }

-public protocol KotlinTypedStateFlow<Element>: KotlinTypedFlow { }
+public protocol KotlinTypedStateFlow<Element>: KotlinTypedSharedFlow { }

 extension KotlinTypedStateFlow {
     public var wrapped: any KotlinStateFlow { _flow as! (any KotlinStateFlow) }
@@ -88,18 +145,26 @@ public struct _KotlinTypedStateFlowImpl<Element>: KotlinTypedStateFlow {
     }
 }

-public protocol KotlinMutableStateFlow: KotlinStateFlow {
+public protocol KotlinMutableStateFlow: KotlinStateFlow, KotlinMutableSharedFlow {
     var value: (any KotlinRuntimeSupport._KotlinBridgeable)? { get set }
+    func compareAndSet(expect: (any KotlinRuntimeSupport._KotlinBridgeable)?, update: (any KotlinRuntimeSupport._KotlinBridgeable)?) -> Bool
 }

-public protocol KotlinTypedMutableStateFlow<Element>: KotlinTypedStateFlow { }
+public protocol KotlinTypedMutableStateFlow<Element>: KotlinTypedStateFlow, KotlinTypedMutableSharedFlow { }

 extension KotlinTypedMutableStateFlow {
     public var wrapped: any KotlinMutableStateFlow { _flow as! (any KotlinMutableStateFlow) }

     public var value: Element {
         get { wrapped.value as! Element }
-        set { wrapped.value = newValue as! (any KotlinRuntimeSupport._KotlinBridgeable)? }
+        nonmutating set { wrapped.value = newValue as! (any KotlinRuntimeSupport._KotlinBridgeable)? }
+    }
+
+    public func compareAndSet(expect: Element, update: Element) -> Bool {
+        wrapped.compareAndSet(
+            expect: expect as! (any KotlinRuntimeSupport._KotlinBridgeable)?,
+            update: update as! (any KotlinRuntimeSupport._KotlinBridgeable)?
+        )
     }
 }

PATCH

echo "Patch applied successfully"

# Commit the changes so that git status is clean (for pass-to-pass tests)
git add -A
git -c user.email="test@example.com" -c user.name="Test User" commit -m "Apply SharedFlow support patch" || true
