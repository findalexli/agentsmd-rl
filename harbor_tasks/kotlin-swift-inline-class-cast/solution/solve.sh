#!/bin/bash
set -e

cd /workspace/kotlin

# Check if patch already applied (idempotency check using distinctive line from patch)
if grep -q 'if ((ktSymbol.containingDeclaration as KaNamedClassSymbol).isInline)' native/swift/sir-light-classes/src/org/jetbrains/sir/lightclasses/nodes/SirInitFromKtSymbol.kt 2>/dev/null; then
    echo "Patch already applied, skipping..."
    exit 0
fi

# Apply gold patch
cat <<'PATCH' | git apply -
diff --git a/native/swift/sir-light-classes/src/org/jetbrains/sir/lightclasses/nodes/SirInitFromKtSymbol.kt b/native/swift/sir-light-classes/src/org/jetbrains/sir/lightclasses/nodes/SirInitFromKtSymbol.kt
index 7dc57abbe4034..01446b02ed6aa 100644
--- a/native/swift/sir-light-classes/src/org/jetbrains/sir/lightclasses/nodes/SirInitFromKtSymbol.kt
+++ b/native/swift/sir-light-classes/src/org/jetbrains/sir/lightclasses/nodes/SirInitFromKtSymbol.kt
@@ -5,6 +5,7 @@

 package org.jetbrains.sir.lightclasses.nodes

+import org.jetbrains.kotlin.analysis.api.components.containingDeclaration
 import org.jetbrains.kotlin.analysis.api.components.containingSymbol
 import org.jetbrains.kotlin.analysis.api.components.defaultType
 import org.jetbrains.kotlin.analysis.api.components.isArrayOrPrimitiveArray
@@ -138,7 +139,9 @@ internal class SirRegularInitFromKtSymbol(
                             producingType,
                             SirTypeNamer.KotlinNameType.PARAMETRIZED
                         )
-                    }>(${args.joinToString()})"
+                    }>(${args.joinToString()})${
+                        if ((ktSymbol.containingDeclaration as KaNamedClassSymbol).isInline) " as Any?" else ""
+                    }"
                 }.orEmpty()
             )
             if (origin is InnerInitSource) {
PATCH

echo "Patch applied successfully!"
