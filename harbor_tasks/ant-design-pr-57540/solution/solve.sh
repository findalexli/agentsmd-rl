#!/bin/bash
set -euo pipefail

cd /workspace/antd

# Idempotency check: skip if already patched
if grep -q "minWidth: 0," components/cascader/style/columns.ts 2>/dev/null; then
    echo "Patch already applied, skipping."
    exit 0
fi

# Apply the gold patch
patch -p1 <<'PATCH'
diff --git a/components/cascader/style/columns.ts b/components/cascader/style/columns.ts
index 250258d2e..366e4b855 100644
--- a/components/cascader/style/columns.ts
+++ b/components/cascader/style/columns.ts
@@ -65,8 +65,8 @@ const getColumnsStyle: GenerateStyle<CascaderToken, CSSInterpolation> = (token)
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

echo "Patch applied successfully."
