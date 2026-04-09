#!/bin/bash
set -e

cd /workspace/kotlin

# Idempotency check: skip if already applied
if grep -q "FirJavaWhenExhaustivenessWarningChecker" compiler/fir/checkers/checkers.jvm/src/org/jetbrains/kotlin/fir/analysis/jvm/checkers/JvmExpressionCheckers.kt 2>/dev/null; then
    echo "Patch already applied, skipping."
    exit 0
fi

# Apply the gold patch (ignore failures for already-patched files)
patch -p1 << 'ENDOFPATCH' || true
diff --git a/analysis/analysis-api-fir/gen/org/jetbrains/kotlin/analysis/api/fir/diagnostics/KaFirDataClassConverters.kt b/analysis/analysis-api-fir/gen/org/jetbrains/kotlin/analysis/api/fir/diagnostics/KaFirDataClassConverters.kt
index 864e4bb01f4ab..1c3476eadd7cf 100644
--- a/analysis/analysis-api-fir/gen/org/jetbrains/kotlin/analysis/api/fir/diagnostics/KaFirDataClassConverters.kt
+++ b/analysis/analysis-api-fir/gen/org/jetbrains/kotlin/analysis/api/fir/diagnostics/KaFirDataClassConverters.kt
@@ -4706,6 +4706,13 @@ private fun KaDiagnosticConverterBuilder.addConversions105() {
             token,
         )
     }
+    add(FirJvmErrors.UNEXHAUSTIVE_WHEN_BASED_ON_JAVA_ANNOTATIONS) { firDiagnostic ->
+        UnexhaustiveWhenBasedOnJavaAnnotationsImpl(
+            firSymbolBuilder.typeBuilder.buildKtType(firDiagnostic.a),
+            firDiagnostic as KtPsiDiagnostic,
+            token,
+        )
+    }
     add(FirJvmErrors.EXTERNAL_DECLARATION_CANNOT_BE_ABSTRACT) { firDiagnostic ->
         ExternalDeclarationCannotBeAbstractImpl(
             firDiagnostic as KtPsiDiagnostic,
diff --git a/analysis/analysis-api-fir/gen/org/jetbrains/kotlin/analysis/api/fir/diagnostics/KaFirDiagnostics.kt b/analysis/analysis-api-fir/gen/org/jetbrains/kotlin/analysis/api/fir/diagnostics/KaFirDiagnostics.kt
index 5e91d9ce9b93a..6a497a30bdd01 100644
--- a/analysis/analysis-api-fir/gen/org/jetbrains/kotlin/analysis/api/fir/diagnostics/KaFirDiagnostics.kt
+++ b/analysis/analysis-api-fir/gen/org/jetbrains/kotlin/analysis/api/fir/diagnostics/KaFirDiagnostics.kt
@@ -4897,6 +4897,11 @@ sealed interface KaFirDiagnostic<PSI : PsiElement> : KaDiagnosticWithPsi<PSI> {
         val expectedType: KaType
     }

+    interface UnexhaustiveWhenBasedOnJavaAnnotations : KaFirDiagnostic<PsiElement> {
+        override val diagnosticClass get() = UnexhaustiveWhenBasedOnJavaAnnotations::class
+        val subjectType: KaType
+    }
+
     interface UpperBoundCannotBeArray : KaFirDiagnostic<PsiElement> {
         override val diagnosticClass get() = UpperBoundCannotBeArray::class
     }
diff --git a/analysis/analysis-api-fir/gen/org/jetbrains/kotlin/analysis/api/fir/diagnostics/KaFirDiagnosticsImpl.kt b/analysis/analysis-api-fir/gen/org/jetbrains/kotlin/analysis/api/fir/diagnostics/KaFirDiagnosticsImpl.kt
index 0ac5b83fafd12..04a574d877d30 100644
--- a/analysis/analysis-api-fir/gen/org/jetbrains/kotlin/analysis/api/fir/diagnostics/KaFirDiagnosticsImpl.kt
+++ b/analysis/analysis-api-fir/gen/org/jetbrains/kotlin/analysis/api/fir/diagnostics/KaFirDiagnosticsImpl.kt
@@ -5882,6 +5882,12 @@ internal class JavaClassOnCompanionImpl(
     token: KaLifetimeToken,
 ) : KaAbstractFirDiagnostic<PsiElement>(firDiagnostic, token), KaFirDiagnostic.JavaClassOnCompanion

+internal class UnexhaustiveWhenBasedOnJavaAnnotationsImpl(
+    override val subjectType: KaType,
+    firDiagnostic: KtPsiDiagnostic,
+    token: KaLifetimeToken,
+) : KaAbstractFirDiagnostic<PsiElement>(firDiagnostic, token), KaFirDiagnostic.UnexhaustiveWhenBasedOnJavaAnnotations
+
 internal class UpperBoundCannotBeArrayImpl(
     firDiagnostic: KtPsiDiagnostic,
     token: KaLifetimeToken,
diff --git a/compiler/fir/checkers/checkers-component-generator/src/org/jetbrains/kotlin/fir/checkers/generator/diagnostics/FirJvmDiagnosticsList.kt b/compiler/fir/checkers/checkers-component-generator/src/org/jetbrains/kotlin/fir/checkers/generator/diagnostics/FirJvmDiagnosticsList.kt
index 3ba953ded8fef..a3493224e4e58 100644
--- a/compiler/fir/checkers/checkers-component-generator/src/org/jetbrains/kotlin/fir/checkers/generator/diagnostics/FirJvmDiagnosticsList.kt
+++ b/compiler/fir/checkers/checkers-component-generator/src/org/jetbrains/kotlin/fir/checkers/generator/diagnostics/FirJvmDiagnosticsList.kt
@@ -115,6 +115,10 @@ object JVM_DIAGNOSTICS_LIST : DiagnosticList("FirJvmErrors") {
             parameter<ConeKotlinType>("actualType")
             parameter<ConeKotlinType>("expectedType")
         }
+
+        val UNEXHAUSTIVE_WHEN_BASED_ON_JAVA_ANNOTATIONS by warning<PsiElement>(PositioningStrategy.WHEN_EXPRESSION) {
+            parameter<ConeKotlinType>("subjectType")
+        }
     }

     val TYPE_PARAMETERS by object : DiagnosticGroup("Type parameters") {
diff --git a/compiler/fir/checkers/checkers.jvm/gen/org/jetbrains/kotlin/fir/analysis/diagnostics/jvm/FirJvmErrors.kt b/compiler/fir/checkers/checkers.jvm/gen/org/jetbrains/kotlin/fir/analysis/diagnostics/jvm/FirJvmErrors.kt
index 11ee4fdf2f581..0f08a289fdff5 100644
--- a/compiler/fir/checkers/checkers.jvm/gen/org/jetbrains/kotlin/fir/analysis/diagnostics/jvm/FirJvmErrors.kt
+++ b/compiler/fir/checkers/checkers.jvm/gen/org/jetbrains/kotlin/fir/analysis/diagnostics/jvm/FirJvmErrors.kt
@@ -86,6 +86,7 @@ object FirJvmErrors : KtDiagnosticsContainer() {
     val NULLABILITY_MISMATCH_BASED_ON_EXPLICIT_TYPE_ARGUMENTS_FOR_JAVA: KtDiagnosticFactory3<ConeKotlinType, ConeKotlinType, String> = KtDiagnosticFactory3("NULLABILITY_MISMATCH_BASED_ON_EXPLICIT_TYPE_ARGUMENTS_FOR_JAVA", WARNING, SourceElementPositioningStrategies.DEFAULT, PsiElement::class, getRendererFactory())
     val TYPE_MISMATCH_WHEN_FLEXIBILITY_CHANGES: KtDiagnosticFactory2<ConeKotlinType, ConeKotlinType> = KtDiagnosticFactory2("TYPE_MISMATCH_WHEN_FLEXIBILITY_CHANGES", WARNING, SourceElementPositioningStrategies.DEFAULT, PsiElement::class, getRendererFactory())
     val JAVA_CLASS_ON_COMPANION: KtDiagnosticFactory2<ConeKotlinType, ConeKotlinType> = KtDiagnosticFactory2("JAVA_CLASS_ON_COMPANION", WARNING, SourceElementPositioningStrategies.SELECTOR_BY_QUALIFIED, PsiElement::class, getRendererFactory())
+    val UNEXHAUSTIVE_WHEN_BASED_ON_JAVA_ANNOTATIONS: KtDiagnosticFactory1<ConeKotlinType> = KtDiagnosticFactory1("UNEXHAUSTIVE_WHEN_BASED_ON_JAVA_ANNOTATIONS", WARNING, SourceElementPositioningStrategies.WHEN_EXPRESSION, PsiElement::class, getRendererFactory())

     // Type parameters
     val UPPER_BOUND_CANNOT_BE_ARRAY: KtDiagnosticFactory0 = KtDiagnosticFactory0("UPPER_BOUND_CANNOT_BE_ARRAY", ERROR, SourceElementPositioningStrategies.DEFAULT, PsiElement::class, getRendererFactory())
diff --git a/compiler/fir/checkers/checkers.jvm/src/org/jetbrains/kotlin/fir/analysis/diagnostics/jvm/FirJvmErrorsDefaultMessages.kt b/compiler/fir/checkers/checkers.jvm/src/org/jetbrains/kotlin/fir/analysis/diagnostics/jvm/FirJvmErrorsDefaultMessages.kt
index de356ddd4c3b6..7a8e106890636 100644
--- a/compiler/fir/checkers/checkers.jvm/src/org/jetbrains/kotlin/fir/analysis/diagnostics/jvm/FirJvmErrorsDefaultMessages.kt
+++ b/compiler/fir/checkers/checkers.jvm/src/org/jetbrains/kotlin/fir/analysis/diagnostics/jvm/FirJvmErrorsDefaultMessages.kt
@@ -123,6 +123,7 @@ import org.jetbrains.kotlin.fir.analysis.diagnostics.jvm.FirJvmErrors.SYNCHRONIZ
 import org.jetbrains.kotlin.fir.analysis.diagnostics.jvm.FirJvmErrors.SYNTHETIC_PROPERTY_WITHOUT_JAVA_ORIGIN
 import org.jetbrains.kotlin.fir.analysis.diagnostics.jvm.FirJvmErrors.THROWS_IN_ANNOTATION
 import org.jetbrains.kotlin.fir.analysis.diagnostics.jvm.FirJvmErrors.TYPE_MISMATCH_WHEN_FLEXIBILITY_CHANGES
+import org.jetbrains.kotlin.fir.analysis.diagnostics.jvm.FirJvmErrors.UNEXHAUSTIVE_WHEN_BASED_ON_JAVA_ANNOTATIONS
 import org.jetbrains.kotlin.fir.analysis.diagnostics.jvm.FirJvmErrors.UPPER_BOUND_CANNOT_BE_ARRAY
 import org.jetbrains.kotlin.fir.analysis.diagnostics.jvm.FirJvmErrors.UPPER_BOUND_VIOLATED_BASED_ON_JAVA_ANNOTATIONS
 import org.jetbrains.kotlin.fir.analysis.diagnostics.jvm.FirJvmErrors.UPPER_BOUND_VIOLATED_IN_TYPEALIAS_EXPANSION_BASED_ON_JAVA_ANNOTATIONS
@@ -183,6 +184,11 @@ object FirJvmErrorsDefaultMessages : BaseDiagnosticRendererFactory() {
             RENDER_TYPE,
         )

+        map.put(
+            UNEXHAUSTIVE_WHEN_BASED_ON_JAVA_ANNOTATIONS,
+            "''when'' expression over a subject of type ''{0}'' is not exhaustive. Add a ''null'' or ''else'' branch.",
+            RENDER_TYPE
+        )
         map.put(
             WRONG_TYPE_FOR_JAVA_OVERRIDE,
             "Override ''{0}'' has incorrect nullability/mutability in its signature compared to the overridden declaration ''{1}''.",
diff --git a/compiler/fir/checkers/checkers.jvm/src/org/jetbrains/kotlin/fir/analysis/jvm/checkers/JvmExpressionCheckers.kt b/compiler/fir/checkers/checkers.jvm/src/org/jetbrains/kotlin/fir/analysis/jvm/checkers/JvmExpressionCheckers.kt
index e54a8cac4bdf9..9fe10449d7874 100644
--- a/compiler/fir/checkers/checkers.jvm/src/org/jetbrains/kotlin/fir/analysis/jvm/checkers/JvmExpressionCheckers.kt
+++ b/compiler/fir/checkers/checkers.jvm/src/org/jetbrains/kotlin/fir/analysis/jvm/checkers/JvmExpressionCheckers.kt
@@ -68,6 +68,7 @@ object JvmExpressionCheckers : ExpressionCheckers() {
     override val whenExpressionCheckers: Set<FirWhenExpressionChecker>
         get() = setOf(
             FirWhenConditionJavaNullabilityWarningChecker,
+            FirJavaWhenExhaustivenessWarningChecker,
         )

     override val booleanOperatorExpressionCheckers: Set<FirBooleanOperatorExpressionChecker>
diff --git a/compiler/fir/checkers/checkers.jvm/src/org/jetbrains/kotlin/fir/analysis/jvm/checkers/expression/FirJavaWhenExhaustivenessWarningChecker.kt b/compiler/fir/checkers/checkers.jvm/src/org/jetbrains/kotlin/fir/analysis/jvm/checkers/expression/FirJavaWhenExhaustivenessWarningChecker.kt
new file mode 100644
index 0000000000000..6818b3cccb1c0
--- /dev/null
+++ b/compiler/fir/checkers/checkers.jvm/src/org/jetbrains/kotlin/fir/analysis/jvm/checkers/expression/FirJavaWhenExhaustivenessWarningChecker.kt
@@ -0,0 +1,50 @@
+/*
+ * Copyright 2010-2026 JetBrains s.r.o. and Kotlin Programming Language contributors.
+ * Use of this source code is governed by the Apache 2.0 license that can be found in the license/LICENSE.txt file.
+ */
+
+package org.jetbrains.kotlin.fir.analysis.jvm.checkers.expression
+
+import org.jetbrains.kotlin.diagnostics.DiagnosticReporter
+import org.jetbrains.kotlin.diagnostics.reportOn
+import org.jetbrains.kotlin.fir.analysis.checkers.MppCheckerKind
+import org.jetbrains.kotlin.fir.analysis.checkers.context.CheckerContext
+import org.jetbrains.kotlin.fir.analysis.checkers.expression.FirWhenExpressionChecker
+import org.jetbrains.kotlin.fir.analysis.diagnostics.jvm.FirJvmErrors
+import org.jetbrains.kotlin.fir.expressions.FirEqualityOperatorCall
+import org.jetbrains.kotlin.fir.expressions.FirOperation
+import org.jetbrains.kotlin.fir.expressions.FirTypeOperatorCall
+import org.jetbrains.kotlin.fir.expressions.FirWhenExpression
+import org.jetbrains.kotlin.fir.expressions.arguments
+import org.jetbrains.kotlin.fir.expressions.isExhaustive
+import org.jetbrains.kotlin.fir.java.enhancement.enhancedTypeForWarning
+import org.jetbrains.kotlin.fir.types.canBeNull
+import org.jetbrains.kotlin.fir.types.coneType
+import org.jetbrains.kotlin.fir.types.isMarkedOrFlexiblyNullable
+import org.jetbrains.kotlin.fir.types.isNullableNothing
+import org.jetbrains.kotlin.fir.types.lowerBoundIfFlexible
+import org.jetbrains.kotlin.fir.types.resolvedType
+
+object FirJavaWhenExhaustivenessWarningChecker : FirWhenExpressionChecker(MppCheckerKind.Platform) {
+    context(context: CheckerContext, reporter: DiagnosticReporter)
+    override fun check(expression: FirWhenExpression) {
+        if (!expression.isExhaustive) return
+        val variable = expression.subjectVariable ?: return
+        val coneType = variable.returnTypeRef.coneType
+        val enhancedType = coneType.enhancedTypeForWarning ?: return
+        if (!enhancedType.lowerBoundIfFlexible().canBeNull(context.session) ||
+            coneType.lowerBoundIfFlexible().canBeNull(context.session)
+        ) return
+
+        val hasNullCheck = expression.branches.any {
+            if (it.hasGuard) return@any false
+            when (val condition = it.condition) {
+                is FirEqualityOperatorCall -> condition.arguments[1].resolvedType.isNullableNothing
+                is FirTypeOperatorCall -> condition.operation == FirOperation.IS && condition.conversionTypeRef.coneType.isMarkedOrFlexiblyNullable
+                else -> false
+            }
+        }
+
+        if (!hasNullCheck) reporter.reportOn(expression.source, FirJvmErrors.UNEXHAUSTIVE_WHEN_BASED_ON_JAVA_ANNOTATIONS, enhancedType)
+    }
+}
diff --git a/compiler/fir/checkers/src/org/jetbrains/kotlin/fir/analysis/checkers/expression/FirExhaustiveWhenChecker.kt b/compiler/fir/checkers/src/org/jetbrains/kotlin/fir/analysis/checkers/expression/FirExhaustiveWhenChecker.kt
index e8e95db49b90d..6e9c0cc89c360 100644
--- a/compiler/fir/checkers/src/org/jetbrains/kotlin/fir/analysis/checkers/expression/FirExhaustiveWhenChecker.kt
+++ b/compiler/fir/checkers/src/org/jetbrains/kotlin/fir/analysis/checkers/expression/FirExhaustiveWhenChecker.kt
@@ -79,13 +79,10 @@ object FirExhaustiveWhenChecker : FirWhenExpressionChecker(MppCheckerKind.Common
             }
         } else {
             if (subjectClassSymbol == null) return
-            val kind = when {
-                subjectClassSymbol.modality == Modality.SEALED -> AlgebraicTypeKind.Sealed
-                subjectClassSymbol.classKind == ClassKind.ENUM_CLASS -> AlgebraicTypeKind.Enum
-                subjectType.isBooleanOrNullableBoolean -> AlgebraicTypeKind.Boolean
-                else -> return
-            }
-
+            if (subjectClassSymbol.modality != Modality.SEALED &&
+                subjectClassSymbol.classKind != ClassKind.ENUM_CLASS &&
+                !subjectType.isBooleanOrNullableBoolean
+            ) return
             reportNoElseInWhen(source, whenExpression, subjectClassSymbol)
         }
     }
@@ -127,12 +124,6 @@ object FirExhaustiveWhenChecker : FirWhenExpressionChecker(MppCheckerKind.Common
     private val FirWhenExpression.missingCases: List<WhenMissingCase>
         get() = (exhaustivenessStatus as ExhaustivenessStatus.NotExhaustive).reasons

-    private enum class AlgebraicTypeKind(val displayName: String) {
-        Sealed("sealed class/interface"),
-        Enum("enum"),
-        Boolean("Boolean")
-    }
-
     context(reporter: DiagnosticReporter, context: CheckerContext)
     private fun reportElseMisplaced(
         expression: FirWhenExpression,
diff --git a/compiler/testData/diagnostics/foreignAnnotationsTests/java8Tests/jspecify/WhenWarn.fir.kt b/compiler/testData/diagnostics/foreignAnnotationsTests/java8Tests/jspecify/WhenWarn.fir.kt
index 85ee249416d55..abd89ed01ac3d 100644
--- a/compiler/testData/diagnostics/foreignAnnotationsTests/java8Tests/jspecify/WhenWarn.fir.kt
+++ b/compiler/testData/diagnostics/foreignAnnotationsTests/java8Tests/jspecify/WhenWarn.fir.kt
@@ -89,7 +89,7 @@ fun test_8(): Int {


 fun test_9(): Int {
-    return when (J.getNullable()) {
+    return <!UNEXHAUSTIVE_WHEN_BASED_ON_JAVA_ANNOTATIONS!>when<!> (J.getNullable()) {
         J.A -> 1
         J.B -> 2
     }
@@ -104,7 +104,7 @@ fun test_10(): Int {
 }

 fun test_11(): Int {
-    return when (J.getNullable()) {
+    return <!UNEXHAUSTIVE_WHEN_BASED_ON_JAVA_ANNOTATIONS!>when<!> (J.getNullable()) {
         J.A -> 1
         J.B -> 2
         else -> 3
ENDOFPATCH

echo "Patch applied successfully."

# Create the new test data files
mkdir -p compiler/testData/diagnostics/foreignAnnotationsTests/java8Tests/jspecify/strictMode
mkdir -p compiler/testData/diagnostics/foreignAnnotationsTests/java8Tests/jspecify/warnMode

cat > compiler/testData/diagnostics/foreignAnnotationsTests/java8Tests/jspecify/strictMode/annotatedWhenSubject.fir.kt << 'EOF'
// ISSUE: KT-84106
// JSPECIFY_STATE: strict

// FILE: J.java
import org.jspecify.annotations.*;

public class J {
    @Nullable
    public static <T> T identity(T t) { return null; }
}

// FILE: test.kt
sealed class Sealed1
class C1 : Sealed1()

sealed class Sealed2
object O2 : Sealed2()

fun test() {
    <!NO_ELSE_IN_WHEN!>when<!> (J.identity(C1() as Sealed1)) {
        is C1 -> {}
    }

    when (J.identity(C1() as Sealed1)) {
        is C1 -> {}
        null -> {}
    }

    when (J.identity(C1() as Sealed1)) {
        is C1? -> {}
    }

    <!NO_ELSE_IN_WHEN!>when<!> (J.identity(O2 as Sealed2)) {
        O2 -> {}
    }

    when (J.identity(O2 as Sealed2)) {
        O2 -> {}
        null -> {}
    }
}
EOF

cat > compiler/testData/diagnostics/foreignAnnotationsTests/java8Tests/jspecify/strictMode/annotatedWhenSubject.kt << 'EOF'
// ISSUE: KT-84106
// JSPECIFY_STATE: strict

// FILE: J.java
import org.jspecify.annotations.*;

public class J {
    @Nullable
    public static <T> T identity(T t) { return null; }
}

// FILE: test.kt
sealed class Sealed1
class C1 : Sealed1()

sealed class Sealed2
object O2 : Sealed2()

fun test() {
    <!NO_ELSE_IN_WHEN!>when<!> (J.identity(C1() as Sealed1)) {
        is C1 -> {}
    }

    when (J.identity(C1() as Sealed1)) {
        is C1 -> {}
        null -> {}
    }

    <!NO_ELSE_IN_WHEN!>when<!> (J.identity(C1() as Sealed1)) {
        is C1? -> {}
    }

    <!NO_ELSE_IN_WHEN!>when<!> (J.identity(O2 as Sealed2)) {
        O2 -> {}
    }

    when (J.identity(O2 as Sealed2)) {
        O2 -> {}
        null -> {}
    }
}
EOF

cat > compiler/testData/diagnostics/foreignAnnotationsTests/java8Tests/jspecify/warnMode/annotatedWhenSubject.fir.kt << 'EOF'
// ISSUE: KT-84106
// JSPECIFY_STATE: warn

// FILE: J.java
import org.jspecify.annotations.*;

public class J {
    @Nullable
    public static <T> T identity(T t) { return null; }
}

// FILE: test.kt
sealed class Sealed1
class C1 : Sealed1()

sealed class Sealed2
object O2 : Sealed2()

fun test() {
    <!UNEXHAUSTIVE_WHEN_BASED_ON_JAVA_ANNOTATIONS!>when<!> (J.identity(C1() as Sealed1)) {
        is C1 -> {}
    }

    when (J.identity(C1() as Sealed1)) {
        is C1 -> {}
        null -> {}
    }

    when (J.identity(C1() as Sealed1)) {
        is C1? -> {}
    }

    <!UNEXHAUSTIVE_WHEN_BASED_ON_JAVA_ANNOTATIONS!>when<!> (J.identity(O2 as Sealed2)) {
        O2 -> {}
    }

    when (J.identity(O2 as Sealed2)) {
        O2 -> {}
        null -> {}
    }
}
EOF

cat > compiler/testData/diagnostics/foreignAnnotationsTests/java8Tests/jspecify/warnMode/annotatedWhenSubject.kt << 'EOF'
// ISSUE: KT-84106
// JSPECIFY_STATE: warn

// FILE: J.java
import org.jspecify.annotations.*;

public class J {
    @Nullable
    public static <T> T identity(T t) { return null; }
}

// FILE: test.kt
sealed class Sealed1
class C1 : Sealed1()

sealed class Sealed2
object O2 : Sealed2()

fun test() {
    when (J.identity(C1() as Sealed1)) {
        is C1 -> {}
    }

    when (J.identity(C1() as Sealed1)) {
        is C1 -> {}
        null -> {}
    }

    when (J.identity(C1() as Sealed1)) {
        is C1? -> {}
    }

    when (J.identity(O2 as Sealed2)) {
        O2 -> {}
    }

    when (J.identity(O2 as Sealed2)) {
        O2 -> {}
        null -> {}
    }
}
EOF

echo "All files created successfully."
