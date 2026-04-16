#!/bin/bash
set -e

cd /workspace/ant-design

# Idempotency check - skip if patch already applied
if grep -q "if (variant === 'solid')" components/button/Button.tsx 2>/dev/null; then
    echo "Patch already applied, skipping..."
    exit 0
fi

# Apply the gold patch
patch -p1 <<'PATCH'
diff --git a/components/button/Button.tsx b/components/button/Button.tsx
index e7b5c4c671f6..9696d0af5721 100644
--- a/components/button/Button.tsx
+++ b/components/button/Button.tsx
@@ -188,11 +188,19 @@ const InternalCompoundedButton = React.forwardRef<
       return colorVariantPair;
     }

+    if (variant === 'solid') {
+      return ['primary', variant];
+    }
+
     // >>> Context fallback
     if (contextColor && contextVariant) {
       return [contextColor, contextVariant];
     }

+    if (contextVariant === 'solid') {
+      return ['primary', contextVariant];
+    }
+
     return ['default', 'outlined'];
   }, [color, variant, type, danger, contextColor, contextVariant, mergedType]);

diff --git a/components/tag/hooks/useColor.ts b/components/tag/hooks/useColor.ts
index b6075bdf9f5d..c0d437bf2144 100644
--- a/components/tag/hooks/useColor.ts
+++ b/components/tag/hooks/useColor.ts
@@ -35,11 +35,15 @@ export default function useColor(
     }

     // ==================== Color ====================
-    const nextColor = isInverseColor ? color?.replace('-inverse', '') : color;
+    let nextColor = isInverseColor ? color?.replace('-inverse', '') : color;
+
+    if (nextColor === undefined && nextVariant === 'solid') {
+      nextColor = 'default';
+    }

     // =============== Preset & Status ===============
-    const nextIsPreset = isPresetColor(color);
-    const nextIsStatus = isPresetStatusColor(color);
+    const nextIsPreset = isPresetColor(nextColor);
+    const nextIsStatus = isPresetStatusColor(nextColor);

     // ================== Customize ==================
     // When `color` is not preset color,
PATCH

echo "Patch applied successfully"
