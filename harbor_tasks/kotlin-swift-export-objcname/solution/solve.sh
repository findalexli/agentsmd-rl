#!/bin/bash
set -e

cd /workspace/kotlin

# Check if already applied (idempotency check)
if grep -q "objCNameAnnotation" native/swift/sir-providers/src/org/jetbrains/kotlin/sir/providers/utils/AnalysisApiUtils.kt 2>/dev/null; then
    echo "Patch already applied, skipping"
    exit 0
fi

# Apply the gold patch
patch -p1 <<'PATCH'
diff --git a/native/swift/sir-light-classes/src/org/jetbrains/sir/lightclasses/nodes/SirProtocolFromKtSymbol.kt b/native/swift/sir-light-classes/src/org/jetbrains/sir/lightclasses/nodes/SirProtocolFromKtSymbol.kt
index 33111d3a92a83..afeba81f6b8b6 100644
--- a/native/swift/sir-light-classes/src/org/jetbrains/sir/lightclasses/nodes/SirProtocolFromKtSymbol.kt
+++ b/native/swift/sir-light-classes/src/org/jetbrains/sir/lightclasses/nodes/SirProtocolFromKtSymbol.kt
@@ -41,8 +41,8 @@ internal open class SirProtocolFromKtSymbol(
     override val documentation: String? by lazy {
         ktSymbol.documentation()
     }
-    override val name: String by lazy {
-        (this.relocatedDeclarationNamePrefix() ?: "") + ktSymbol.name.asString()
+    override val name: String by lazyWithSessions {
+        (this.relocatedDeclarationNamePrefix() ?: "") + ktSymbol.sirDeclarationName()
     }
     override var parent: SirDeclarationParent
         get() = withSessions {
diff --git a/native/swift/sir-light-classes/src/org/jetbrains/sir/lightclasses/utils/TypeTranslationUtils.kt b/native/swift/sir-light-classes/src/org/jetbrains/sir/lightclasses/utils/TypeTranslationUtils.kt
index 33e30cc1ecd59..5dffa0d3ce18f 100644
--- a/native/swift/sir-light-classes/src/org/jetbrains/sir/lightclasses/utils/TypeTranslationUtils.kt
+++ b/native/swift/sir-light-classes/src/org/jetbrains/sir/lightclasses/utils/TypeTranslationUtils.kt
@@ -23,6 +23,7 @@ import org.jetbrains.kotlin.sir.providers.SirSession
 import org.jetbrains.kotlin.sir.providers.sirModule
 import org.jetbrains.kotlin.sir.providers.source.KotlinParameterOrigin
 import org.jetbrains.kotlin.sir.providers.translateType
+import org.jetbrains.kotlin.sir.providers.utils.objCNameAnnotation
 import org.jetbrains.kotlin.sir.providers.utils.updateImports
 import org.jetbrains.sir.lightclasses.SirFromKtSymbol
 import org.jetbrains.sir.lightclasses.extensions.withSessions
@@ -52,8 +53,12 @@ internal inline fun <reified T : KaFunctionSymbol> SirFromKtSymbol<T>.translateP
     return withSessions {
         this@translateParameters.ktSymbol.valueParameters.map { parameter ->
             val sirType = createParameterType(ktSymbol, parameter).escaping
+            val objCNameAnnotation = parameter.objCNameAnnotation
+            val argumentName = objCNameAnnotation?.argumentName ?: parameter.name.asString()
+            val parameterName = objCNameAnnotation?.name ?: parameter.name.asString()
             SirParameter(
-                argumentName = parameter.name.asString(),
+                argumentName = argumentName,
+                parameterName = parameterName.takeIf { it != argumentName },
                 type = sirType,
                 origin = KotlinParameterOrigin.ValueParameter(parameter),
                 isVariadic = parameter.isVararg,
diff --git a/native/swift/sir-providers/src/org/jetbrains/kotlin/sir/providers/impl/SirDeclarationNamerImpl.kt b/native/swift/sir-providers/src/org/jetbrains/kotlin/sir/providers/impl/SirDeclarationNamerImpl.kt
index 26fc71c5a886c..fb7fed64e12c5 100644
--- a/native/swift/sir-providers/src/org/jetbrains/kotlin/sir/providers/impl/SirDeclarationNamerImpl.kt
+++ b/native/swift/sir-providers/src/org/jetbrains/kotlin/sir/providers/impl/SirDeclarationNamerImpl.kt
@@ -9,6 +9,7 @@ import org.jetbrains.kotlin.analysis.api.export.utilities.getJvmNameOrNull
 import org.jetbrains.kotlin.analysis.api.symbols.*
 import org.jetbrains.kotlin.analysis.api.types.symbol
 import org.jetbrains.kotlin.sir.providers.SirDeclarationNamer
+import org.jetbrains.kotlin.sir.providers.utils.objCNameAnnotation

 public class SirDeclarationNamerImpl : SirDeclarationNamer {

@@ -17,6 +18,7 @@ public class SirDeclarationNamerImpl : SirDeclarationNamer {
     }

     private fun KaDeclarationSymbol.getName(): String? {
+        objCNameAnnotation?.name?.let { return it }
         return when (this) {
             is KaNamedClassSymbol -> this.classId?.shortClassName?.asString()
             is KaPropertySymbol -> this.name.asString()
diff --git a/native/swift/sir-providers/src/org/jetbrains/kotlin/sir/providers/utils/AnalysisApiUtils.kt b/native/swift/sir-providers/src/org/jetbrains/kotlin/sir/providers/utils/AnalysisApiUtils.kt
index ab347bb9f2415..191a45bba76a3 100644
--- a/native/swift/sir-providers/src/org/jetbrains/kotlin/sir/providers/utils/AnalysisApiUtils.kt
+++ b/native/swift/sir-providers/src/org/jetbrains/kotlin/sir/providers/utils/AnalysisApiUtils.kt
@@ -6,6 +6,8 @@
 package org.jetbrains.kotlin.sir.providers.utils

 import org.jetbrains.kotlin.analysis.api.annotations.KaAnnotationValue
+import org.jetbrains.kotlin.analysis.api.annotations.KaNamedAnnotationValue
+import org.jetbrains.kotlin.analysis.api.base.KaConstantValue
 import org.jetbrains.kotlin.analysis.api.symbols.KaDeclarationSymbol
 import org.jetbrains.kotlin.analysis.api.symbols.KaSymbolModality
 import org.jetbrains.kotlin.builtins.StandardNames
@@ -52,3 +54,42 @@ public val KaDeclarationSymbol.throwsAnnotation: Throws?

         Throws()
     }
+
+private val ObjCNameClassId = ClassId.topLevel(FqName("kotlin.native.ObjCName"))
+
+public class ObjCNameAnnotation(
+    public val objCName: String?,
+    public val swiftName: String?,
+    public val isExact: Boolean,
+) {
+    /**
+     * The Swift friendly declaration name, this will never be an empty string.
+     */
+    public val name: String? get() = swiftName?.takeIf { it.isNotEmpty() } ?: objCName
+
+    /**
+     * The Swift friendly argument name for this declaration, this might be an empty string.
+     */
+    public val argumentName: String? get() = swiftName ?: objCName
+}
+
+public val KaDeclarationSymbol.objCNameAnnotation: ObjCNameAnnotation?
+    get() = annotations[ObjCNameClassId].firstOrNull()?.let { annotation ->
+        var objCName: String? = null
+        var swiftName: String? = null
+        var isExact: Boolean? = null
+        for (argument in annotation.arguments) {
+            when (argument.name.identifier) {
+                "name" -> objCName = argument.resolveConstantValue<KaConstantValue.StringValue>()?.value
+                "swiftName" -> swiftName = argument.resolveConstantValue<KaConstantValue.StringValue>()?.value
+                "exact" -> isExact = argument.resolveConstantValue<KaConstantValue.BooleanValue>()?.value
+            }
+        }
+        if (swiftName == "_") swiftName = "" // In Swift export we convert empty names to _ where needed
+        ObjCNameAnnotation(objCName, swiftName, isExact ?: false)
+    }
+
+private inline fun <reified T : KaConstantValue> KaNamedAnnotationValue.resolveConstantValue(): T? {
+    val constantValue = expression as? KaAnnotationValue.ConstantValue ?: return null
+    return constantValue.value as? T
+}
PATCH

echo "Patch applied successfully"
