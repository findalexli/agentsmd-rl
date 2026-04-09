#!/bin/bash
set -e

cd /workspace/kotlin

# Check if already applied (idempotency)
if grep -q "override val kind get() = NodeKind.Function" \
    plugins/compose/compiler-hosted/src/main/java/androidx/compose/compiler/plugins/kotlin/k2/ComposableTargetChecker.kt 2>/dev/null; then
    echo "Patch already applied, skipping."
    exit 0
fi

# Apply the gold patch
patch -p1 <<'PATCH'
diff --git a/plugins/compose/compiler-hosted/integration-tests/src/jvmTest/kotlin/androidx/compose/compiler/plugins/kotlin/analysis/ComposableTargetCheckerTests.kt b/plugins/compose/compiler-hosted/integration-tests/src/jvmTest/kotlin/androidx/compose/compiler/plugins/kotlin/analysis/ComposableTargetCheckerTests.kt
index fadac4a4f5b97..5097e4b2bdf56 100644
--- a/plugins/compose/compiler-hosted/integration-tests/src/jvmTest/kotlin/androidx/compose/compiler/plugins/kotlin/analysis/ComposableTargetCheckerTests.kt
+++ b/plugins/compose/compiler-hosted/integration-tests/src/jvmTest/kotlin/androidx/compose/compiler/plugins/kotlin/analysis/ComposableTargetCheckerTests.kt
@@ -18,6 +18,7 @@ package androidx.compose.compiler.plugins.kotlin.analysis

 import androidx.compose.compiler.plugins.kotlin.AbstractComposeDiagnosticsTest
 import androidx.compose.compiler.plugins.kotlin.Classpath
+import org.junit.Assume.assumeTrue
 import org.junit.Test

 class ComposableTargetCheckerTests(useFir: Boolean) : AbstractComposeDiagnosticsTest(useFir) {
@@ -497,8 +498,10 @@ class ComposableTargetCheckerTests(useFir: Boolean) : AbstractComposeDiagnosticsT
     )

     @Test
-    fun testDifferentWrapperTypes() = check(
-        """
+    fun testDifferentWrapperTypes() {
+        assumeTrue(useFir)
+        check(
+            """
             import androidx.compose.runtime.*

             @Retention(AnnotationRetention.BINARY)
@@ -536,13 +539,14 @@ class ComposableTargetCheckerTests(useFir: Boolean) : AbstractComposeDiagnosticsT

             @Composable fun T() {
                 MWrapper {
-                    NWrapper {
-                        N()
+                    ${firMisStart()}NWrapper${firEnd()} {
+                        ${firMisStart()}N${firEnd()}()
                     }
                 }
             }
         """
-    )
+        )
+    }

     @Test
     fun differentApplierInContainingFunction() = check(
diff --git a/plugins/compose/compiler-hosted/src/main/java/androidx/compose/compiler/plugins/kotlin/k2/ComposableTargetChecker.kt b/plugins/compose/compiler-hosted/src/main/java/androidx/compose/compiler/plugins/kotlin/k2/ComposableTargetChecker.kt
index dabbbb22b069d..8adb98c9c3e8e 100644
--- a/plugins/compose/compiler-hosted/src/main/java/androidx/compose/compiler/plugins/kotlin/k2/ComposableTargetChecker.kt
+++ b/plugins/compose/compiler-hosted/src/main/java/androidx/compose/compiler/plugins/kotlin/k2/ComposableTargetChecker.kt
@@ -50,6 +50,7 @@ private open class FirElementInferenceNode(element: FirElement) : FirInferenceNo
 }

 private class FirCallableElementInferenceNode(val callable: FirCallableSymbol<*>, element: FirElement) : FirElementInferenceNode(element) {
+    override val kind get() = NodeKind.Function
     override val type: InferenceNodeType = InferenceCallableType(callable)
     override fun toString(): String = "${callable.name.toString()}()@${element.source?.startOffset}"
 }
@@ -85,12 +86,27 @@ private class FirParameterReferenceNode(
     override fun toString(): String = "param:$parameterIndex"
 }

-private fun callableInferenceNodeOf(expression: FirElement, callable: FirCallableSymbol<*>, context: CheckerContext) =
-    parameterInferenceNodeOrNull(expression, context) ?: (expression as? FirAnonymousFunction)?.let {
+@OptIn(SymbolInternals::class)
+private fun callableInferenceNodeOf(expression: FirElement, callable: FirCallableSymbol<*>, context: CheckerContext): FirInferenceNode {
+    parameterInferenceNodeOrNull(expression, context)?.let {
+        return it
+    }
+
+    (expression as? FirAnonymousFunction)?.let {
         context.session.composableTargetSessionStorage.getLambdaExpression(expression)
     }?.let {
-        inferenceNodeOf(it, context)
-    } ?: FirCallableElementInferenceNode(callable, expression)
+        return inferenceNodeOf(it, context)
+    }
+
+    (expression as? FirFunctionCall)?.let {
+        return FirCallableElementInferenceNode(callable, callable.fir)
+    }
+
+    // A node's `element` property determines which scheme it is associated with. Falling through to
+    // this case means that it is not safe for the returned node to share a scheme with any other
+    // node, so we set its `element` property to `expression`.
+    return FirCallableElementInferenceNode(callable, expression)
+}

 @OptIn(SymbolInternals::class)
 private fun parameterInferenceNodeOrNull(expression: FirElement, context: CheckerContext): FirInferenceNode? {
diff --git a/plugins/compose/compiler-hosted/testData/diagnostics/targetWarnings.diag.txt b/plugins/compose/compiler-hosted/testData/diagnostics/targetWarnings.diag.txt
index 435d486d2cad6..43000d4638442 100644
--- a/plugins/compose/compiler-hosted/testData/diagnostics/targetWarnings.diag.txt
+++ b/plugins/compose/compiler-hosted/testData/diagnostics/targetWarnings.diag.txt
@@ -1,3 +1,7 @@
 /module_main_targetWarnings.kt:(367,373): warning: Calling a Vector composable function where a UI composable was expected

-/module_main_targetWarnings.kt:(459,461): warning: Calling a UI composable function where a Vector composable was expected
+/module_main_targetWarnings.kt:(431,444): warning: Calling a Vector composable function where a UI composable was expected
+
+/module_main_targetWarnings.kt:(539,548): warning: Calling a UI composable function where a Vector composable was expected
+
+/module_main_targetWarnings.kt:(563,565): warning: Calling a UI composable function where a Vector composable was expected
diff --git a/plugins/compose/compiler-hosted/testData/diagnostics/targetWarnings.kt b/plugins/compose/compiler-hosted/testData/diagnostics/targetWarnings.kt
index 6a3cb79cefd7a..bbc6f5c9de5fb 100644
--- a/plugins/compose/compiler-hosted/testData/diagnostics/targetWarnings.kt
+++ b/plugins/compose/compiler-hosted/testData/diagnostics/targetWarnings.kt
@@ -56,16 +56,16 @@ import vector.*

 @Composable fun VecInUi() {
     UiContent {
-        VectorContent {
-            <!COMPOSE_APPLIER_CALL_MISMATCH!>Ui<!>()
+        <!COMPOSE_APPLIER_CALL_MISMATCH!>VectorContent<!> {
+            Ui()
         }
     }
 }

 @Composable fun UiInVec() {
     VectorContent {
-        UiContent {
-            Ui()
+        <!COMPOSE_APPLIER_CALL_MISMATCH!>UiContent<!> {
+            <!COMPOSE_APPLIER_CALL_MISMATCH!>Ui<!>()
         }
     }
 }
PATCH

echo "Patch applied successfully."
