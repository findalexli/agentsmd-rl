#!/bin/bash
set -e

cd /workspace/kotlin

# Apply the gold patch for removing ForbidUsingSupertypesWithInaccessibleContentInTypeArguments
patch -p1 <<'PATCH'
diff --git a/compiler/fir/checkers/src/org/jetbrains/kotlin/fir/analysis/checkers/FirMissingDependencySupertypeUtils.kt b/compiler/fir/checkers/src/org/jetbrains/kotlin/fir/analysis/checkers/FirMissingDependencySupertypeUtils.kt
index 8d5b862ae16f7..6f0f801501f48 100644
--- a/compiler/fir/checkers/src/org/jetbrains/kotlin/fir/analysis/checkers/FirMissingDependencySupertypeUtils.kt
+++ b/compiler/fir/checkers/src/org/jetbrains/kotlin/fir/analysis/checkers/FirMissingDependencySupertypeUtils.kt
@@ -32,12 +32,9 @@ fun checkMissingDependencySuperTypes(

     val missingSuperTypes = context.session.missingDependencyStorage.getMissingSuperTypes(declaration)
     val languageVersionSettings = context.languageVersionSettings
-    for ((superType, origin) in missingSuperTypes) {
+    for (superType in missingSuperTypes) {
         val diagnostic =
             when {
-                origin == FirMissingDependencyStorage.SupertypeOrigin.TYPE_ARGUMENT && !languageVersionSettings.supportsFeature(
-                    LanguageFeature.ForbidUsingSupertypesWithInaccessibleContentInTypeArguments
-                ) -> FirErrors.MISSING_DEPENDENCY_SUPERCLASS_IN_TYPE_ARGUMENT
                 isEagerCheck && !languageVersionSettings.supportsFeature(
                     LanguageFeature.AllowEagerSupertypeAccessibilityChecks
                 ) -> FirErrors.MISSING_DEPENDENCY_SUPERCLASS_WARNING
diff --git a/compiler/fir/providers/src/org/jetbrains/kotlin/fir/types/FirMissingDependencyStorage.kt b/compiler/fir/providers/src/org/jetbrains/kotlin/fir/types/FirMissingDependencyStorage.kt
index 4dce33f03ad90..d334603ee76b9 100644
--- a/compiler/fir/providers/src/org/jetbrains/kotlin/fir/types/FirMissingDependencyStorage.kt
+++ b/compiler/fir/providers/src/org/jetbrains/kotlin/fir/types/FirMissingDependencyStorage.kt
@@ -16,24 +16,17 @@ import org.jetbrains.kotlin.fir.symbols.impl.FirClassSymbol
 @ThreadSafeMutableState
 class FirMissingDependencyStorage(private val session: FirSession) : FirSessionComponent {
     private val cache =
-        session.firCachesFactory.createCache<FirClassSymbol<*>, Set<TypeWithOrigin>, Nothing?> { symbol, _ ->
+        session.firCachesFactory.createCache<FirClassSymbol<*>, Set<ConeKotlinType>, Nothing?> { symbol, _ ->
             findMissingSuperTypes(symbol)
         }

-    enum class SupertypeOrigin {
-        TYPE_ARGUMENT,
-        OTHER
-    }
-
-    data class TypeWithOrigin(val type: ConeKotlinType, val origin: SupertypeOrigin)
-
-    fun getMissingSuperTypes(declaration: FirClassSymbol<*>): Set<TypeWithOrigin> {
+    fun getMissingSuperTypes(declaration: FirClassSymbol<*>): Set<ConeKotlinType> {
         return cache.getValue(declaration, null)
     }

-    private fun findMissingSuperTypes(declaration: FirClassSymbol<*>): Set<TypeWithOrigin> {
+    private fun findMissingSuperTypes(declaration: FirClassSymbol<*>): Set<ConeKotlinType> {
         return declaration.collectSuperTypes(session)
-            .filterTo(mutableSetOf()) { (type, _) ->
+            .filterTo(mutableSetOf()) { type ->
                 // Ignore types which are already errors.
                 type !is ConeErrorType && type !is ConeDynamicType && type.lowerBoundIfFlexible().let {
                     it is ConeLookupTagBasedType && it.toSymbol(session) == null
@@ -41,24 +34,17 @@ class FirMissingDependencyStorage(private val session: FirSession) : FirSessionC
             }
     }

-    private fun FirClassSymbol<*>.collectSuperTypes(session: FirSession): Set<TypeWithOrigin> {
-        val result = mutableSetOf<TypeWithOrigin>()
-        fun collect(symbol: FirClassSymbol<*>, origin: SupertypeOrigin) {
+    private fun FirClassSymbol<*>.collectSuperTypes(session: FirSession): Set<ConeKotlinType> {
+        val result = mutableSetOf<ConeKotlinType>()
+        fun collect(symbol: FirClassSymbol<*>) {
             for (superTypeRef in symbol.resolvedSuperTypeRefs) {
                 val superType = superTypeRef.coneType
-                if (!superType.isAny && result.add(TypeWithOrigin(superType, origin))) {
-                    superType.toClassSymbol(session)?.let { collect(it, origin) }
-                }
-                for (typeArgument in superType.typeArguments) {
-                    if (typeArgument !is ConeKotlinTypeProjection) continue
-                    val type = typeArgument.type
-                    if (!type.isAny && result.add(TypeWithOrigin(type, SupertypeOrigin.TYPE_ARGUMENT))) {
-                        type.toClassSymbol(session)?.let { collect(it, SupertypeOrigin.TYPE_ARGUMENT) }
-                    }
+                if (!superType.isAny && result.add(superType)) {
+                    superType.toClassSymbol(session)?.let { collect(it) }
                 }
             }
         }
-        collect(this, SupertypeOrigin.OTHER)
+        collect(this)
         return result
     }
 }
diff --git a/compiler/testData/diagnostics/tests/multimodule/FalsePositiveInaccessibleTypeInDefaultArg.kt b/compiler/testData/diagnostics/tests/multimodule/FalsePositiveInaccessibleTypeInDefaultArg.kt
index ca3eeb71fc63b..93c939d0fce0a 100644
--- a/compiler/testData/diagnostics/tests/multimodule/FalsePositiveInaccessibleTypeInDefaultArg.kt
+++ b/compiler/testData/diagnostics/tests/multimodule/FalsePositiveInaccessibleTypeInDefaultArg.kt
@@ -1,6 +1,6 @@
 // RUN_PIPELINE_TILL: FRONTEND
 // ISSUE: KT-74459
-// LANGUAGE: -ForbidUsingExpressionTypesWithInaccessibleContent -ForbidUsingSupertypesWithInaccessibleContentInTypeArguments -ForbidLambdaParameterWithMissingDependencyType -AllowEagerSupertypeAccessibilityChecks
+// LANGUAGE: -ForbidUsingExpressionTypesWithInaccessibleContent -ForbidLambdaParameterWithMissingDependencyType -AllowEagerSupertypeAccessibilityChecks
 // MODULE: base
 // FILE: base.kt

diff --git a/compiler/testData/diagnostics/tests/multimodule/InaccessibleTypeEagerCheck.kt b/compiler/testData/diagnostics/tests/multimodule/InaccessibleTypeEagerCheck.kt
index 1115388c30ecf..e8a4bab048479 100644
--- a/compiler/testData/diagnostics/tests/multimodule/InaccessibleTypeEagerCheck.kt
+++ b/compiler/testData/diagnostics/tests/multimodule/InaccessibleTypeEagerCheck.kt
@@ -1,5 +1,5 @@
 // RUN_PIPELINE_TILL: BACKEND
-// LANGUAGE: +ForbidUsingExpressionTypesWithInaccessibleContent +ForbidUsingSupertypesWithInaccessibleContentInTypeArguments +ForbidLambdaParameterWithMissingDependencyType -AllowEagerSupertypeAccessibilityChecks
+// LANGUAGE: +ForbidUsingExpressionTypesWithInaccessibleContent +ForbidLambdaParameterWithMissingDependencyType -AllowEagerSupertypeAccessibilityChecks

 // MODULE: missing
 // FILE: Base.kt
diff --git a/compiler/testData/diagnostics/tests/multimodule/InaccessibleTypeEagerCheckForbidden.kt b/compiler/testData/diagnostics/tests/multimodule/InaccessibleTypeEagerCheckForbidden.kt
index 12b461c75bda2..77fce6cf4d4bb 100644
--- a/compiler/testData/diagnostics/tests/multimodule/InaccessibleTypeEagerCheckForbidden.kt
+++ b/compiler/testData/diagnostics/tests/multimodule/InaccessibleTypeEagerCheckForbidden.kt
@@ -1,5 +1,5 @@
 // RUN_PIPELINE_TILL: FRONTEND
-// LANGUAGE: +ForbidUsingExpressionTypesWithInaccessibleContent +ForbidUsingSupertypesWithInaccessibleContentInTypeArguments +ForbidLambdaParameterWithMissingDependencyType +AllowEagerSupertypeAccessibilityChecks
+// LANGUAGE: +ForbidUsingExpressionTypesWithInaccessibleContent +ForbidLambdaParameterWithMissingDependencyType +AllowEagerSupertypeAccessibilityChecks

 // MODULE: missing
 // FILE: Base.kt
diff --git a/compiler/testData/diagnostics/tests/multimodule/InaccessibleTypeEagerCheckJava.kt b/compiler/testData/diagnostics/tests/multimodule/InaccessibleTypeEagerCheckJava.kt
index 1cc132a92f583..862c3ccaff1c8 100644
--- a/compiler/testData/diagnostics/tests/multimodule/InaccessibleTypeEagerCheckJava.kt
+++ b/compiler/testData/diagnostics/tests/multimodule/InaccessibleTypeEagerCheckJava.kt
@@ -1,5 +1,5 @@
 // RUN_PIPELINE_TILL: BACKEND
-// LANGUAGE: +ForbidUsingExpressionTypesWithInaccessibleContent +ForbidUsingSupertypesWithInaccessibleContentInTypeArguments +ForbidLambdaParameterWithMissingDependencyType -AllowEagerSupertypeAccessibilityChecks
+// LANGUAGE: +ForbidUsingExpressionTypesWithInaccessibleContent +ForbidLambdaParameterWithMissingDependencyType -AllowEagerSupertypeAccessibilityChecks

 // MODULE: missing
 // FILE: Base.java
diff --git a/compiler/testData/diagnostics/tests/multimodule/SupertypesWithInaccessibleTypeArguments.kt b/compiler/testData/diagnostics/tests/multimodule/SupertypesWithInaccessibleTypeArguments.kt
index 3b87b12829d0d..2798f22d8e676 100644
--- a/compiler/testData/diagnostics/tests/multimodule/SupertypesWithInaccessibleTypeArguments.kt
+++ b/compiler/testData/diagnostics/tests/multimodule/SupertypesWithInaccessibleTypeArguments.kt
@@ -1,5 +1,4 @@
 // RUN_PIPELINE_TILL: BACKEND
-// LANGUAGE: -ForbidUsingSupertypesWithInaccessibleContentInTypeArguments

 // MODULE: start
 // FILE: start.kt
@@ -18,8 +17,8 @@ interface BoxedGenericType : Box<InaccessibleGenericSuperType<Nothing>>
 // MODULE: end(middle)
 // FILE: end.kt

-<!MISSING_DEPENDENCY_SUPERCLASS_IN_TYPE_ARGUMENT!>interface BoxedConcreteTypeImplementation<!> : BoxedConcreteType
+interface BoxedConcreteTypeImplementation : BoxedConcreteType

-<!MISSING_DEPENDENCY_SUPERCLASS_IN_TYPE_ARGUMENT!>interface BoxedGenericTypeImplementation<!> : BoxedGenericType
+interface BoxedGenericTypeImplementation : BoxedGenericType

 /* GENERATED_FIR_TAGS: interfaceDeclaration, nullableType, typeParameter */
diff --git a/compiler/testData/diagnostics/tests/multimodule/inaccessibleSupertypeVariousExperimental.kt b/compiler/testData/diagnostics/tests/multimodule/inaccessibleSupertypeVariousExperimental.kt
index c032940eae13f..cdce76299c90c 100644
--- a/compiler/testData/diagnostics/tests/multimodule/inaccessibleSupertypeVariousExperimental.kt
+++ b/compiler/testData/diagnostics/tests/multimodule/inaccessibleSupertypeVariousExperimental.kt
@@ -27,7 +27,7 @@ fun main() {
     dependencyInheritor

     <!MISSING_DEPENDENCY_SUPERCLASS_WARNING!>DependencyInheritor<!>()
-    <!MISSING_DEPENDENCY_SUPERCLASS_IN_TYPE_ARGUMENT!>BoxedDependencyInheritor<!>()
+    BoxedDependencyInheritor()

     dependencyInheritor.<!MISSING_DEPENDENCY_SUPERCLASS, UNRESOLVED_REFERENCE!>foo<!>()
     dependencyInheritor.<!MISSING_DEPENDENCY_SUPERCLASS!>bar<!>()
diff --git a/compiler/testData/diagnostics/tests/multimodule/inaccessibleSupertypeVariousExperimentalEnabled.kt b/compiler/testData/diagnostics/tests/multimodule/inaccessibleSupertypeVariousExperimentalEnabled.kt
index dd7147e870108..6925d5067cccb 100644
--- a/compiler/testData/diagnostics/tests/multimodule/inaccessibleSupertypeVariousExperimentalEnabled.kt
+++ b/compiler/testData/diagnostics/tests/multimodule/inaccessibleSupertypeVariousExperimentalEnabled.kt
@@ -1,6 +1,6 @@
 // RUN_PIPELINE_TILL: FRONTEND
 // ISSUE: KT-78800
-// LANGUAGE: +AllowEagerSupertypeAccessibilityChecks +ForbidUsingSupertypesWithInaccessibleContentInTypeArguments
+// LANGUAGE: +AllowEagerSupertypeAccessibilityChecks

 // MODULE: top
 // FILE: top.kt
@@ -28,7 +28,7 @@ fun main() {
     dependencyInheritor

     <!MISSING_DEPENDENCY_SUPERCLASS!>DependencyInheritor<!>()
-    <!MISSING_DEPENDENCY_SUPERCLASS!>BoxedDependencyInheritor<!>()
+    BoxedDependencyInheritor()

     dependencyInheritor.<!MISSING_DEPENDENCY_SUPERCLASS, UNRESOLVED_REFERENCE!>foo<!>()
     dependencyInheritor.<!MISSING_DEPENDENCY_SUPERCLASS!>bar<!>()
diff --git a/core/language.version-settings/api/language.version-settings.api b/core/language.version-settings/api/language.version-settings.api
index 92b628884551e..dfbf037b365fd 100644
--- a/core/language.version-settings/api/language.version-settings.api
+++ b/core/language.version-settings/api/language.version-settings.api
@@ -274,7 +274,6 @@ public final class org/jetbrains/kotlin/config/LanguageFeature : java/lang/Enum
 	public static final field ForbidUselessTypeArgumentsIn25 Lorg/jetbrains/kotlin/config/LanguageFeature;
 	public static final field ForbidUsingExpressionTypesWithInaccessibleContent Lorg/jetbrains/kotlin/config/LanguageFeature;
 	public static final field ForbidUsingExtensionPropertyTypeParameterInDelegate Lorg/jetbrains/kotlin/config/LanguageFeature;
-	public static final field ForbidUsingSupertypesWithInaccessibleContentInTypeArguments Lorg/jetbrains/kotlin/config/LanguageFeature;
 	public static final field ForkIsNotSuccessfulWhenNoBranchIsSuccessful Lorg/jetbrains/kotlin/config/LanguageFeature;
 	public static final field FunctionReferenceWithDefaultValueAsOtherType Lorg/jetbrains/kotlin/config/LanguageFeature;
 	public static final field FunctionTypesWithBigArity Lorg/jetbrains/kotlin/config/LanguageFeature;

diff --git a/core/language.version-settings/src/org/jetbrains/kotlin/config/LanguageVersionSettings.kt b/core/language.version-settings/src/org/jetbrains/kotlin/config/LanguageVersionSettings.kt
index b87e2052a7a77..f133d1c606674 100644
--- a/core/language.version-settings/src/org/jetbrains/kotlin/config/LanguageVersionSettings.kt
+++ b/core/language.version-settings/src/org/jetbrains/kotlin/config/LanguageVersionSettings.kt
@@ -608,7 +608,6 @@ enum class LanguageFeature(
     CollectionLiterals(sinceVersion = null, issue = "KT-80489"),
     ProperFieldAccessGenerationForFieldAccessShadowedByKotlinProperty(sinceVersion = null, "KT-56386"),
     IrCrossModuleInlinerBeforeKlibSerialization(sinceVersion = null, sinceApiVersion = ApiVersion.KOTLIN_2_3, forcesPreReleaseBinaries = true, issue = "KT-79717"),
-    ForbidUsingSupertypesWithInaccessibleContentInTypeArguments(sinceVersion = null, enabledInProgressiveMode = true, "KT-66691"), // KT-66691, KT-66742
     AllowEagerSupertypeAccessibilityChecks(sinceVersion = null, enabledInProgressiveMode = true, "KT-73611"),
     UnnamedLocalVariables(sinceVersion = null, forcesPreReleaseBinaries = false, issue = "KT-74809"),
     ContextSensitiveResolutionUsingExpectedType(sinceVersion = null, "KT-16768"),
PATCH

echo "Patch applied successfully"

# Idempotency check - verify the LanguageFeature enum entry was removed
if grep -q "ForbidUsingSupertypesWithInaccessibleContentInTypeArguments" core/language.version-settings/src/org/jetbrains/kotlin/config/LanguageVersionSettings.kt; then
    echo "ERROR: LanguageFeature entry still present"
    exit 1
fi

echo "Idempotency check passed - ForbidUsingSupertypesWithInaccessibleContentInTypeArguments feature removed"
