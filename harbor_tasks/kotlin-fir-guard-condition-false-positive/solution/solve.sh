#!/bin/bash
set -e

cd /workspace/kotlin

# Apply the fix for false positive DUPLICATE_BRANCH_CONDITION_IN_WHEN
cat << 'PATCH' | git apply -
diff --git a/compiler/fir/checkers/src/org/jetbrains/kotlin/fir/analysis/checkers/expression/FirWhenConditionChecker.kt b/compiler/fir/checkers/src/org/jetbrains/kotlin/fir/analysis/checkers/expression/FirWhenConditionChecker.kt
index 942de46eb4a9c..5c19be4dfbdb4 100644
--- a/compiler/fir/checkers/src/org/jetbrains/kotlin/fir/analysis/checkers/expression/FirWhenConditionChecker.kt
+++ b/compiler/fir/checkers/src/org/jetbrains/kotlin/fir/analysis/checkers/expression/FirWhenConditionChecker.kt
@@ -40,26 +40,23 @@ object FirWhenConditionChecker : FirWhenExpressionChecker(MppCheckerKind.Common)
         val checkedConstants = hashSetOf<Any?>()
         for (branch in expression.branches) {
             when (val condition = branch.condition) {
-                is FirEqualityOperatorCall -> {
-                    val arguments = condition.arguments
-                    if (arguments.size == 2 && arguments[0].unwrapSmartcastExpression() is FirWhenSubjectExpression) {
-                        val value = when (val targetExpression = arguments[1].unwrapSmartcastExpression()) {
-                            is FirLiteralExpression -> targetExpression.value
-                            is FirQualifiedAccessExpression -> targetExpression.calleeReference.toResolvedCallableSymbol() as? FirEnumEntrySymbol
-                                ?: continue
-                            is FirResolvedQualifier -> {
-                                val classSymbol = targetExpression.symbol ?: continue
-                                if (classSymbol.classKind != ClassKind.OBJECT) continue
-                                classSymbol.classId
-                            }
-                            else -> continue
-                        }
-                        if (!checkedConstants.add(value)) {
-                            reporter.reportOn(condition.source, FirErrors.DUPLICATE_BRANCH_CONDITION_IN_WHEN)
+                is FirEqualityOperatorCall if condition.isArgumentWhenSubject() -> {
+                    val value = when (val targetExpression = condition.arguments[1].unwrapSmartcastExpression()) {
+                        is FirLiteralExpression -> targetExpression.value
+                        is FirQualifiedAccessExpression -> targetExpression.calleeReference.toResolvedCallableSymbol() as? FirEnumEntrySymbol
+                            ?: continue
+                        is FirResolvedQualifier -> {
+                            val classSymbol = targetExpression.symbol ?: continue
+                            if (classSymbol.classKind != ClassKind.OBJECT) continue
+                            classSymbol.classId
                         }
+                        else -> continue
+                    }
+                    if (!checkedConstants.add(value)) {
+                        reporter.reportOn(condition.source, FirErrors.DUPLICATE_BRANCH_CONDITION_IN_WHEN)
                     }
                 }
-                is FirTypeOperatorCall -> {
+                is FirTypeOperatorCall if condition.isArgumentWhenSubject() -> {
                     val coneType = condition.conversionTypeRef.coneType
                     if (!checkedTypes.add(coneType to condition.operation)) {
                         reporter.reportOn(condition.conversionTypeRef.source, FirErrors.DUPLICATE_BRANCH_CONDITION_IN_WHEN)
@@ -68,4 +65,8 @@ object FirWhenConditionChecker : FirWhenExpressionChecker(MppCheckerKind.Common)
             }
         }
     }
+
+    private fun FirCall.isArgumentWhenSubject(): Boolean {
+        return argument.unwrapSmartcastExpression() is FirWhenSubjectExpression
+    }
 }
PATCH

echo "Fix applied successfully"
