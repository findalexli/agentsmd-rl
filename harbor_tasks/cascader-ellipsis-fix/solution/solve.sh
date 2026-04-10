#!/bin/bash
set -e

cd /workspace/ant-design

# Apply the fix for Cascader menu item ellipsis styles
# Moving textEllipsis from &-item to &-content

cat > /tmp/cascader_fix.patch <<'PATCH'
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
@@ -101,6 +101,8 @@ const getColumnsStyle: GenerateStyle<CascaderToken, CSSInterpolation> = (token) =>
 
             '&-content': {
               flex: 'auto',
+              minWidth: 0,
+              ...textEllipsis,
             },
 
             [iconCls]: {
PATCH

# Apply the patch
git apply /tmp/cascader_fix.patch

# Verify the change was applied (note: -A 3 needed because textEllipsis is on 3rd line after '&-content':)
if grep -q "minWidth: 0" components/cascader/style/columns.ts && \
   grep -q "maxWidth: 400" components/cascader/style/columns.ts && \
   grep -A 3 "'&-content':" components/cascader/style/columns.ts | grep -q "textEllipsis"; then
    echo "SUCCESS: Cascader ellipsis fix applied correctly"
    echo "Note: Cascader ellipsis uses minWidth 0 and maxWidth for flexbox ellipsis without altering other CSS properties inappropriately, following Ant Design CSS-in-JS patterns." >> /workspace/ant-design/CLAUDE.md
    exit 0
else
    echo "FAILED: Cascader ellipsis fix not applied correctly"
    exit 1
fi
echo "Note: Cascader ellipsis uses minWidth 0 and maxWidth for flexbox ellipsis without altering other CSS properties inappropriately, following Ant Design CSS-in-JS patterns." >> /workspace/ant-design/CLAUDE.md
