#!/bin/bash
set -e

# Apply the gold patch for caching stability inference results
# PR: JetBrains/kotlin#5680

cd /workspace/kotlin

# Create the patch file
cat > /tmp/stability_cache.patch << 'PATCH'
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

# Apply the patch
git apply /tmp/stability_cache.patch

# Verify the distinctive line was added (cache field)
if ! grep -q "private val cache = mutableMapOf<SymbolForAnalysis, Stability>()" "plugins/compose/compiler-hosted/src/main/java/androidx/compose/compiler/plugins/kotlin/analysis/Stability.kt"; then
    echo "ERROR: Patch was not applied correctly - cache field not found"
    exit 1
fi

echo "Patch applied successfully"
