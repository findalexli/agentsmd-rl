#!/bin/bash
set -e

cd /workspace/kotlin

# Apply the gold patch
cat <<'PATCH' | git apply -
diff --git a/compiler/frontend.common/src/org/jetbrains/kotlin/diagnostics/KtDiagnostic.kt b/compiler/frontend.common/src/org/jetbrains/kotlin/diagnostics/KtDiagnostic.kt
index d02b43fe6da1c..9259b007e90fe 100644
--- a/compiler/frontend.common/src/org/jetbrains/kotlin/diagnostics/KtDiagnostic.kt
+++ b/compiler/frontend.common/src/org/jetbrains/kotlin/diagnostics/KtDiagnostic.kt
@@ -12,6 +12,8 @@ import org.jetbrains.kotlin.AbstractKtSourceElement
 import org.jetbrains.kotlin.KtLightSourceElement
 import org.jetbrains.kotlin.KtPsiSourceElement
 import org.jetbrains.kotlin.cli.common.messages.CompilerMessageSourceLocation
+import org.jetbrains.kotlin.utils.exceptions.requireWithAttachment
+import org.jetbrains.kotlin.utils.exceptions.withPsiEntry

 // ------------------------------ diagnostics ------------------------------

@@ -109,8 +111,12 @@ private const val CHECK_PSI_CONSISTENCY_IN_DIAGNOSTICS = true

 private fun KtPsiDiagnostic.checkPsiTypeConsistency() {
     if (CHECK_PSI_CONSISTENCY_IN_DIAGNOSTICS) {
-        require(factory.psiType.isInstance(element.psi)) {
-            "${element.psi::class} is not a subtype of ${factory.psiType} for factory $factory"
+        requireWithAttachment(
+            factory.psiType.isInstance(psiElement),
+            { "${psiElement::class} is not a subtype of ${factory.psiType} for factory $factory" }
+        ) {
+            withPsiEntry("psi", psiElement)
+            withPsiEntry("file", psiFile)
         }
     }
 }
PATCH

# Verify the patch was applied (distinctive line from the patch)
grep -q "requireWithAttachment" compiler/frontend.common/src/org/jetbrains/kotlin/diagnostics/KtDiagnostic.kt

echo "Patch applied successfully"
