#!/bin/bash
set -e

cd /workspace/kotlin

# Check if already patched
if grep -q " FirCallableElementInferenceNode(callable, callable.fir)" plugins/compose/compiler-hosted/src/main/java/androidx/compose/compiler/plugins/kotlin/k2/ComposableTargetChecker.kt; then
    echo "Already patched"
    exit 0
fi

# Apply the fix
cat <<'PATCH' | git apply -
diff --git a/plugins/compose/compiler-hosted/src/main/java/androidx/compose/compiler/plugins/kotlin/k2/ComposableTargetChecker.kt b/plugins/compose/compiler-hosted/src/main/java/androidx/compose/compiler/plugins/kotlin/k2/ComposableTargetChecker.kt
index dabbbb22b069d..8adb98c9c3e8e 100644
--- a/plugins/compose/compiler-hosted/src/main/java/androidx/compose/compiler/plugins/kotlin/k2/ComposableTargetChecker.kt
+++ b/plugins/compose/compiler-hosted/src/main/java/androidx/compose/compiler/plugins/kotlin/k2/ComposableTargetChecker.kt
@@ -50,6 +50,7 @@ private open class FirElementInferenceNode(element: FirElement) : FirInferenceN
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
PATCH

echo "Patch applied successfully"
