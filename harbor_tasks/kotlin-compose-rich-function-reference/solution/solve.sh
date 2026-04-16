#!/bin/bash
set -euo pipefail

cd /workspace/kotlin

# Check if patch is already applied (idempotency)
if grep -q "IrRichFunctionReferenceImpl" plugins/compose/compiler-hosted/src/main/java/androidx/compose/compiler/plugins/kotlin/lower/ComposableFunInterfaceLowering.kt; then
    echo "Patch already applied, skipping..."
    exit 0
fi

# Apply the gold patch
cat <<'PATCH' | git apply -
diff --git a/plugins/compose/compiler-hosted/src/main/java/androidx/compose/compiler/plugins/kotlin/lower/ComposableFunInterfaceLowering.kt b/plugins/compose/compiler-hosted/src/main/java/androidx/compose/compiler/plugins/kotlin/lower/ComposableFunInterfaceLowering.kt
index d3249f467aa82..a151778b3095c 100644
--- a/plugins/compose/compiler-hosted/src/main/java/androidx/compose/compiler/plugins/kotlin/lower/ComposableFunInterfaceLowering.kt
+++ b/plugins/compose/compiler-hosted/src/main/java/androidx/compose/compiler/plugins/kotlin/lower/ComposableFunInterfaceLowering.kt
@@ -21,6 +21,7 @@ package androidx.compose.compiler.plugins.kotlin.lower
 import androidx.compose.compiler.plugins.kotlin.hasComposableAnnotation
 import org.jetbrains.kotlin.backend.common.IrElementTransformerVoidWithContext
 import org.jetbrains.kotlin.backend.common.extensions.IrPluginContext
+import org.jetbrains.kotlin.config.LanguageFeature
 import org.jetbrains.kotlin.descriptors.Modality
 import org.jetbrains.kotlin.ir.declarations.IrModuleFragment
 import org.jetbrains.kotlin.ir.expressions.IrExpression
@@ -28,14 +29,17 @@ import org.jetbrains.kotlin.ir.expressions.IrFunctionExpression
 import org.jetbrains.kotlin.ir.expressions.IrTypeOperator.IMPLICIT_CAST
 import org.jetbrains.kotlin.ir.expressions.IrTypeOperator.SAM_CONVERSION
 import org.jetbrains.kotlin.ir.expressions.IrTypeOperatorCall
+import org.jetbrains.kotlin.ir.expressions.impl.IrRichFunctionReferenceImpl
 import org.jetbrains.kotlin.ir.symbols.UnsafeDuringIrConstructionAPI
 import org.jetbrains.kotlin.ir.types.IrType
 import org.jetbrains.kotlin.ir.types.IrTypeSystemContextImpl
 import org.jetbrains.kotlin.ir.types.classOrNull
 import org.jetbrains.kotlin.ir.util.functions
 import org.jetbrains.kotlin.ir.util.isLambda
+import org.jetbrains.kotlin.ir.util.selectSAMOverriddenFunction
 import org.jetbrains.kotlin.ir.visitors.transformChildrenVoid
 import org.jetbrains.kotlin.platform.jvm.isJvm
+import org.jetbrains.kotlin.platform.konan.isNative

 @Suppress("PRE_RELEASE_CLASS")
 class ComposableFunInterfaceLowering(private val context: IrPluginContext) :
@@ -43,7 +47,7 @@ class ComposableFunInterfaceLowering(private val context: IrPluginContext) :
     ModuleLoweringPass {

     override fun lower(irModule: IrModuleFragment) {
-        if (context.platform.isJvm()) {
+        if (context.platform.isJvm() || (context.platform.isNative() && context.languageVersionSettings.supportsFeature(LanguageFeature.IrRichCallableReferencesInKlibs))) {
             irModule.transformChildrenVoid(this)
         }
     }
@@ -54,15 +58,27 @@ class ComposableFunInterfaceLowering(private val context: IrPluginContext) :
             val argument = functionExpr.transform(this, null) as IrFunctionExpression
             val superType = expression.typeOperand
             val superClass = superType.classOrNull ?: error("Expected non-null class")
-            return FunctionReferenceBuilder(
-                argument,
-                superClass,
-                superType,
-                currentDeclarationParent!!,
-                context,
-                currentScope!!.scope.scopeOwnerSymbol,
-                IrTypeSystemContextImpl(context.irBuiltIns)
-            ).build()
+            return if (!context.platform.isJvm()) {
+                IrRichFunctionReferenceImpl(
+                    startOffset = expression.startOffset,
+                    endOffset = expression.endOffset,
+                    type = expression.typeOperand,
+                    reflectionTargetSymbol = null,
+                    overriddenFunctionSymbol = superClass.owner.selectSAMOverriddenFunction().symbol,
+                    invokeFunction = functionExpr.function,
+                    origin = functionExpr.origin
+                )
+            } else {
+                FunctionReferenceBuilder(
+                    argument,
+                    superClass,
+                    superType,
+                    currentDeclarationParent!!,
+                    context,
+                    currentScope!!.scope.scopeOwnerSymbol,
+                    IrTypeSystemContextImpl(context.irBuiltIns)
+                ).build()
+            }
         }
         return super.visitTypeOperator(expression)
     }
diff --git a/plugins/compose/compiler-hosted/src/main/java/androidx/compose/compiler/plugins/kotlin/lower/ComposableTypeRemapper.kt b/plugins/compose/compiler-hosted/src/main/java/androidx/compose/compiler/plugins/kotlin/lower/ComposableTypeRemapper.kt
index f45fe372c4cec..65a4eaf70dab7 100644
--- a/plugins/compose/compiler-hosted/src/main/java/androidx/compose/compiler/plugins/kotlin/lower/ComposableTypeRemapper.kt
+++ b/plugins/compose/compiler-hosted/src/main/java/androidx/compose/compiler/plugins/kotlin/lower/ComposableTypeRemapper.kt
@@ -296,6 +296,13 @@ internal class ComposableTypeTransformer(
         return super.visitClassReference(expression)
     }

+    override fun visitRichFunctionReference(expression: IrRichFunctionReference): IrExpression {
+        if (expression.overriddenFunctionSymbol.owner.needsComposableRemapping()) {
+            expression.overriddenFunctionSymbol.owner.transform(this, null)
+        }
+        return super.visitRichFunctionReference(expression)
+    }
+
     private fun IrType.remapType() = typeRemapper.remapType(this)
 }

diff --git a/plugins/compose/compiler-hosted/src/main/java/androidx/compose/compiler/plugins/kotlin/lower/ComposerParamTransformer.kt b/plugins/compose/compiler-hosted/src/main/java/androidx/compose/compiler/plugins/kotlin/lower/ComposerParamTransformer.kt
index 26bd72d22d12f..b2c3802fd4c2e 100644
--- a/plugins/compose/compiler-hosted/src/main/java/androidx/compose/compiler/plugins/kotlin/lower/ComposerParamTransformer.kt
+++ b/plugins/compose/compiler-hosted/src/main/java/androidx/compose/compiler/plugins/kotlin/lower/ComposerParamTransformer.kt
@@ -177,6 +177,12 @@ class ComposerParamTransformer(
         }
     }

+    override fun visitRichFunctionReference(expression: IrRichFunctionReference): IrExpression {
+        expression.overriddenFunctionSymbol = expression.overriddenFunctionSymbol.owner.withComposerParamIfNeeded().symbol
+
+        return super.visitRichFunctionReference(expression)
+    }
+
     private fun IrFunction.findCallInBody(): IrCall? {
         var call: IrCall? = null
         body?.acceptChildrenVoid(object : IrVisitorVoid() {
PATCH

echo "Patch applied successfully!"
