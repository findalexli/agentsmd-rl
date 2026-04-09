#!/bin/bash
set -e

cd /workspace/kotlin

# Apply the gold patch for the stability inference caching fix
patch -p1 << 'PATCH'
diff --git a/plugins/compose/compiler-hosted/src/main/java/androidx/compose/compiler/plugins/kotlin/analysis/Stability.kt b/plugins/compose/compiler-hosted/src/main/java/androidx/compose/compiler/plugins/kotlin/analysis/Stability.kt
index 68c09a7619d91..278e71c9a2ce5 100644
--- a/plugins/compose/compiler-hosted/src/main/java/androidx/compose/compiler/plugins/kotlin/analysis/Stability.kt
+++ b/plugins/compose/compiler-hosted/src/main/java/androidx/compose/compiler/plugins/kotlin/analysis/Stability.kt
@@ -202,6 +202,8 @@ class StabilityInferencer(
 ) {
     private val externalTypeMatcherCollection = FqNameMatcherCollection(externalStableTypeMatchers)

+    private val cache = mutableMapOf<SymbolForAnalysis, Stability>()
+
     fun stabilityOf(irType: IrType): Stability =
         stabilityOf(irType, emptyMap(), emptySet())

@@ -214,7 +216,20 @@ class StabilityInferencer(
         val typeArguments = declaration.typeParameters.map { substitutions[it.symbol] }
         val fullSymbol = SymbolForAnalysis(symbol, typeArguments)

-        if (currentlyAnalyzing.contains(fullSymbol)) return Stability.Unstable
+        if (fullSymbol in cache) return cache[fullSymbol]!!
+
+        val result = stabilityOf(declaration, fullSymbol, substitutions, currentlyAnalyzing)
+        cache[fullSymbol] = result
+        return result
+    }
+
+    private fun stabilityOf(
+        declaration: IrClass,
+        symbol: SymbolForAnalysis,
+        substitutions: Map<IrTypeParameterSymbol, IrTypeArgument>,
+        currentlyAnalyzing: Set<SymbolForAnalysis>
+    ): Stability {
+        if (currentlyAnalyzing.contains(symbol)) return Stability.Unstable
         if (declaration.hasStableMarkedDescendant()) return Stability.Stable
         if (declaration.isEnumClass || declaration.isEnumEntry) return Stability.Stable
         if (declaration.defaultType.isPrimitiveType()) return Stability.Stable
@@ -224,7 +239,7 @@ class StabilityInferencer(
             error("Builtins Stub: ${declaration.name}")
         }

-        val analyzing = currentlyAnalyzing + fullSymbol
+        val analyzing = currentlyAnalyzing + symbol

         if (canInferStability(declaration) || declaration.isExternalStableType()) {
             val fqName = declaration.fqNameWhenAvailable?.toString() ?: ""
PATCH

# Verify patch was applied by checking for the distinctive line
grep -q "private val cache = mutableMapOf<SymbolForAnalysis, Stability>()" \
    plugins/compose/compiler-hosted/src/main/java/androidx/compose/compiler/plugins/kotlin/analysis/Stability.kt \
    && echo "Patch applied successfully" \
    || { echo "Patch failed"; exit 1; }
