#!/bin/bash
set -e

cd /workspace/kotlin

# Idempotency check - verify if already applied
if grep -q "kotlinx_coroutines_launch" native/swift/sir-providers/src/org/jetbrains/kotlin/sir/providers/impl/BridgeProvider/SirBridgeProviderImpl.kt 2>/dev/null; then
    echo "Patch already applied, skipping..."
    exit 0
fi

# Apply the gold patch
patch -p1 <<'PATCH'
diff --git a/native/swift/sir-providers/src/org/jetbrains/kotlin/sir/providers/impl/BridgeProvider/SirBridgeProviderImpl.kt b/native/swift/sir-providers/src/org/jetbrains/kotlin/sir/providers/impl/BridgeProvider/SirBridgeProviderImpl.kt
index 7d58340d69664..20986c74bc733 100644
--- a/native/swift/sir-providers/src/org/jetbrains/kotlin/sir/providers/impl/BridgeProvider/SirBridgeProviderImpl.kt
+++ b/native/swift/sir-providers/src/org/jetbrains/kotlin/sir/providers/impl/BridgeProvider/SirBridgeProviderImpl.kt
@@ -357,7 +357,7 @@ private fun BridgeFunctionDescriptor.createKotlinBridge(
         val errorParameter = errorParameter ?: error("Async function must have an error parameter")
         add(
             """
-            CoroutineScope(__${cancellation.name.kotlinIdentifier} + Dispatchers.Default).launch(start = CoroutineStart.UNDISPATCHED) {
+            CoroutineScope(__${cancellation.name.kotlinIdentifier} + Dispatchers.Default).kotlinx_coroutines_launch(start = CoroutineStart.UNDISPATCHED) {
                 try {
                     val $resultName = $callSite
                     __${continuation.name}(${resultName})
@@ -477,17 +477,24 @@ private fun BridgeFunctionDescriptor.cDeclaration() = buildString {
     append(";")
 }

-private fun BridgeFunctionDescriptor.additionalImports(): List<String> = listOfNotNull(
-    (extensionReceiverParameter != null && selfParameter == null && !kotlinFqName.parent().isRoot).ifTrue {
-        "$name as $safeImportName"
-    },
-    isAsync.ifTrue {
-        "kotlinx.coroutines.*"
-    },
-)
+private fun BridgeFunctionDescriptor.additionalImports(): List<String> = buildList {
+    if (extensionReceiverParameter != null && selfParameter == null && !kotlinFqName.parent().isRoot) {
+        add("$name as $safeImportName")
+    }
+    if (isAsync) {
+        add("kotlinx.coroutines.CancellationException")
+        add("kotlinx.coroutines.CoroutineScope")
+        add("kotlinx.coroutines.CoroutineStart")
+        add("kotlinx.coroutines.Dispatchers")
+        add(FqName("kotlinx.coroutines.launch").let { "$it as ${it.safeImportName}" })
+    }
+}

 private val BridgeFunctionDescriptor.safeImportName: String
-    get() = kotlinFqName.pathSegments().joinToString(separator = "_") { it.asString().replace("_", "__") }
+    get() = kotlinFqName.safeImportName
+
+private val FqName.safeImportName: String
+    get() = pathSegments().joinToString(separator = "_") { it.asString().replace("_", "__") }

 private fun String.prependIndentToTrailingLines(indent: String): String = this.lines().let { lines ->
     lines.singleOrNull() ?: buildString {
PATCH

echo "Patch applied successfully!"
