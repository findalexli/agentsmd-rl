#!/bin/bash
set -e

# Navigate to the repository
cd /workspace/kotlin

# Apply the fix for Swift Export Flow in contravariant positions
cat << 'PATCH' | git apply -
diff --git a/native/swift/sir-providers/src/org/jetbrains/kotlin/sir/providers/impl/SirTypeProviderImpl.kt b/native/swift/sir-providers/src/org/jetbrains/kotlin/sir/providers/impl/SirTypeProviderImpl.kt
index e120dc4c780ba..dc17fe1461c1a 100644
--- a/native/swift/sir-providers/src/org/jetbrains/kotlin/sir/providers/impl/SirTypeProviderImpl.kt
+++ b/native/swift/sir-providers/src/org/jetbrains/kotlin/sir/providers/impl/SirTypeProviderImpl.kt
@@ -87,7 +87,7 @@ public class SirTypeProviderImpl(
                             }

                             // Intercept Flow<T> for typed generic wrapping in covariant position
-                            if (kaType.classId in FLOW_CLASS_IDS && ctx.currentPosition == SirTypeVariance.COVARIANT) {
+                            if (kaType.classId in FLOW_CLASS_IDS) {
                                 val elementArg = kaType.typeArguments.singleOrNull()
                                 if (elementArg is KaTypeArgumentWithVariance) {
                                     val elementType = elementArg.type
@@ -263,7 +263,7 @@ public class SirTypeProviderImpl(
     private val SirNominalType.isTypealiasOntoFunctionalType: Boolean
         get() = (typeDeclaration as? SirTypealias)?.let { it.expandedType is SirFunctionalType } == true

-    private companion object {
+    internal companion object {
         val FLOW_CLASS_ID = ClassId.fromString("kotlinx/coroutines/flow/Flow")
         val STATE_FLOW_CLASS_ID = ClassId.fromString("kotlinx/coroutines/flow/StateFlow")
         val MUTABLE_STATE_FLOW_CLASS_ID = ClassId.fromString("kotlinx/coroutines/flow/MutableStateFlow")
diff --git a/native/swift/sir-providers/src/org/jetbrains/kotlin/sir/providers/impl/SirVisibilityCheckerImpl.kt b/native/swift/sir-providers/src/org/jetbrains/kotlin/sir/providers/impl/SirVisibilityCheckerImpl.kt
index 2dd3112b7a4a1..eda1a378c5668 100644
--- a/native/swift/sir-providers/src/org/jetbrains/kotlin/sir/providers/impl/SirVisibilityCheckerImpl.kt
+++ b/native/swift/sir-providers/src/org/jetbrains/kotlin/sir/providers/impl/SirVisibilityCheckerImpl.kt
@@ -253,6 +253,7 @@ private fun hasUnboundInputTypeParameters(
     isReturnType: Boolean
 ): Boolean = (type.fullyExpandedType as? KaClassType)?.let { classType ->
     if (sirSession.isTypeSupported(classType)) return@let false
+    if (classType.classId in SirTypeProviderImpl.FLOW_CLASS_IDS) return@let false
     if (classType is KaFunctionType) {
         return@let classType.parameterTypes.any {
             hasUnboundInputTypeParameters(it, false)
PATCH

# Idempotency check: verify the fix was applied
if grep -q "if (kaType.classId in FLOW_CLASS_IDS) {" \
    native/swift/sir-providers/src/org/jetbrains/kotlin/sir/providers/impl/SirTypeProviderImpl.kt; then
    echo "Fix applied successfully"
    exit 0
else
    echo "Failed to apply fix"
    exit 1
fi
