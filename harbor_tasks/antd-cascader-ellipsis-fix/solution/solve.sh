#!/bin/bash
set -e

cd /workspace/ant-design

# Idempotency check - if already patched, skip
if grep -q "minWidth: 0" components/cascader/style/columns.ts; then
    echo "Patch already applied, skipping."
    exit 0
fi

# Apply the gold patch for Cascader ellipsis fix
cat <<'PATCH' | git apply -
diff --git a/components/cascader/style/columns.ts b/components/cascader/style/columns.ts
index 250258d2e1f1..366e4b855a5d 100644
--- a/components/cascader/style/columns.ts
+++ b/components/cascader/style/columns.ts
@@ -65,8 +65,8 @@ const getColumnsStyle: GenerateStyle<CascaderToken, CSSInterpolation> = (token) =>
           },

           '&-item': {
-            ...textEllipsis,
             display: 'flex',
+            maxWidth: 400,
             flexWrap: 'nowrap',
             alignItems: 'center',
             padding: token.optionPadding,
@@ -101,6 +101,8 @@ const getColumnsStyle: GenerateStyle<CascaderToken, CSSInterpolation> = (token)

             '&-content': {
               flex: 'auto',
+              minWidth: 0,
+              ...textEllipsis,
             },

             [iconCls]: {
PATCH

echo "Gold patch applied successfully!"
