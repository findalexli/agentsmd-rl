#!/bin/bash
set -e

cd /workspace/kotlin

# Check if patch already applied (idempotency)
if grep -q "visitInlinedLambdaInComposableScope" plugins/compose/compiler-hosted/src/main/java/androidx/compose/compiler/plugins/kotlin/lower/ComposableFunctionBodyTransformer.kt; then
    echo "Patch already applied, skipping"
    exit 0
fi

# Apply the gold patch
patch -p1 << 'PATCH'
diff --git a/plugins/compose/compiler-hosted/src/main/java/androidx/compose/compiler/plugins/kotlin/lower/ComposableFunctionBodyTransformer.kt b/plugins/compose/compiler-hosted/src/main/java/androidx/compose/compiler/plugins/kotlin/lower/ComposableFunctionBodyTransformer.kt
index 02e3d8d82c1f7..fb1f685a17236 100644
--- a/plugins/compose/compiler-hosted/src/main/java/androidx/compose/compiler/plugins/kotlin/lower/ComposableFunctionBodyTransformer.kt
+++ b/plugins/compose/compiler-hosted/src/main/java/androidx/compose/compiler/plugins/kotlin/lower/ComposableFunctionBodyTransformer.kt
@@ -624,9 +624,6 @@ class ComposableFunctionBodyTransformer(
         return inScope(scope) {
             visitFunctionInScope(declaration)
         }.also {
-            if (scope.isInlinedLambda && !scope.isComposable && scope.hasComposableCalls) {
-                encounteredCapturedComposableCall()
-            }
             metrics.recordFunction(scope.metrics)
             declaration.functionMetrics = scope.metrics
         }
@@ -634,8 +631,14 @@ class ComposableFunctionBodyTransformer(

     private fun visitFunctionInScope(declaration: IrFunction): IrStatement {
         val scope = currentFunctionScope
-        // if the function isn't composable, there's nothing to do
-        if (!scope.isComposable) return super.visitFunction(declaration)
+        if (!scope.isComposable) {
+            if (scope.isInlinedLambda && scope.isInComposable) {
+                return visitInlinedLambdaInComposableScope(declaration)
+            } else {
+                // if the function isn't composable, there's nothing to do
+                return super.visitFunction(declaration)
+            }
+        }
         if (declaration.isDefaultParamStub) {
             // don't transform the body of the stub normally
             return visitComposableFunctionStub(declaration)
@@ -1280,6 +1283,54 @@ class ComposableFunctionBodyTransformer(
         return declaration
     }

+    private fun visitInlinedLambdaInComposableScope(declaration: IrFunction): IrStatement {
+        val scope = currentFunctionScope
+        val parentScope = scope.parent
+        val outerGroupRequired = parentScope is Scope.CaptureScope && parentScope.forceInlinedLambdaGroup
+
+        if (!outerGroupRequired) {
+            val result = super.visitFunction(declaration)
+            if (scope.hasComposableCalls) {
+                encounteredCapturedComposableCall()
+            }
+            return result
+        }
+
+        val originalBody = declaration.body ?: return super.visitFunction(declaration)
+        val (body, returnVar) = originalBody.asBodyAndResultVar()
+        body.transformChildrenVoid()
+
+        scope.realizeGroup {
+            irEndReplaceGroup(scope = scope, startOffset = body.endOffset, endOffset = body.endOffset)
+        }
+
+        declaration.body = context.irFactory.createBlockBody(body.startOffset, body.endOffset) {
+            statements.add(
+                irStartReplaceGroup(
+                    body,
+                    scope,
+                    irFunctionSourceKey(),
+                    startOffset = body.startOffset,
+                    endOffset = body.startOffset
+                )
+            )
+            statements.addAll(body.statements)
+            statements.add(
+                irEndReplaceGroup(
+                    startOffset = body.endOffset,
+                    endOffset = body.endOffset,
+                    scope
+                )
+            )
+            if (returnVar != null) {
+                statements.add(
+                    irReturnVar(declaration.symbol, returnVar)
+                )
+            }
+        }
+        return declaration
+    }
+
     private fun visitComposableReferenceAdapter(
         declaration: IrFunction,
         scope: Scope.FunctionScope
@@ -2635,13 +2686,13 @@ class ComposableFunctionBodyTransformer(
     ) {
         var scope: Scope? = currentScope
         val blockScopeMarks = mutableListOf<Scope.BlockScope>()
-        var leavingInlinedLambda = false
+        var leavingInlinedComposableLambda = false
         loop@ while (scope != null) {
             when (scope) {
                 is Scope.FunctionScope -> {
                     if (scope.function == symbol.owner) {
                         scope.hasAnyEarlyReturn = true
-                        if (!leavingInlinedLambda || !rollbackGroupMarkerEnabled) {
+                        if (!rollbackGroupMarkerEnabled || !leavingInlinedComposableLambda) {
                             blockScopeMarks.fastForEach {
                                 it.markReturn(extraEndLocation)
                             }
@@ -2662,9 +2713,12 @@ class ComposableFunctionBodyTransformer(
                         }
                         break@loop
                     }
-                    if (scope.isInlinedLambda && scope.inComposableCall) {
-                        leavingInlinedLambda = true
-                        scope.hasInlineEarlyReturn = true
+                    if (scope.isInlinedLambda) {
+                        blockScopeMarks.add(scope)
+                        if (scope.inComposableCall) {
+                            scope.hasInlineEarlyReturn = true
+                            leavingInlinedComposableLambda = true
+                        }
                     }
                 }
                 is Scope.BlockScope -> {
@@ -2953,8 +3007,15 @@ class ComposableFunctionBodyTransformer(
             expression.symbol.owner.isInline || expression.symbol.owner.isInlineArrayConstructor() -> {
                 val captureScope = Scope.CaptureScope()
                 withScope(Scope.CallScope(expression, this)) {
+                    val owner = expression.symbol.owner
+
+                    // if it is a non-composable call with multiple inline lambdas, we need to force a group for each inline function.
+                    // this preserves structure in the argument body in cases when inline function hides some control flow.
+                    val inlineLambdaCount = owner.parameters.count { it.isInlineParameter() }
+                    captureScope.forceInlinedLambdaGroup = inlineLambdaCount > 1
+
                     expression.arguments.fastForEachIndexed { index, arg ->
-                        val parameter = expression.symbol.owner.parameters[index]
+                        val parameter = owner.parameters[index]
                         val transformed = if (parameter.isInlineParameter()) {
                             // if it is not a composable call but it is an inline function, then we allow
                             // composable calls to happen inside of the inlined lambdas. This means that we have
@@ -2969,7 +3030,9 @@ class ComposableFunctionBodyTransformer(
                         expression.arguments[index] = transformed
                     }
                 }
-                return if (captureScope.hasCapturedComposableCall) {
+                return if (captureScope.hasCapturedComposableCall && !captureScope.forceInlinedLambdaGroup) {
+                    // the outer group around the call is only required when the inline function body is not
+                    // wrapped with a group.
                     captureScope.realizeAllDirectChildren()
                     expression.asCoalescableGroup(captureScope)
                 } else {
@@ -4473,6 +4536,8 @@ class ComposableFunctionBodyTransformer(
             var hasCapturedComposableCall = false
                 private set

+            var forceInlinedLambdaGroup = false
+
             fun markCapturedComposableCall() {
                 hasCapturedComposableCall = true
             }
PATCH

echo "Patch applied successfully"
