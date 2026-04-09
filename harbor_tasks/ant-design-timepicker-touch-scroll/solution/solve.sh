#!/bin/bash
set -e

# Navigate to the repository
cd /workspace/ant-design

# Check if already patched
if grep -q "overflowY: 'auto'" components/date-picker/style/panel.ts 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Apply the fix patch
cat <<'PATCH' | git apply -
diff --git a/components/date-picker/style/panel.ts b/components/date-picker/style/panel.ts
index c28cb5176099..8f3341337572 100644
--- a/components/date-picker/style/panel.ts
+++ b/components/date-picker/style/panel.ts
@@ -539,7 +539,7 @@ export const genPanelStyle: GenerateStyle<SharedPickerToken, CSSObject> = (token
           width: timeColumnWidth,
           margin: `${unit(paddingXXS)} 0`,
           padding: 0,
-          overflowY: 'hidden',
+          overflowY: 'auto',
           textAlign: 'start',
           listStyle: 'none',
           transition: `background-color ${motionDurationMid}`,
@@ -575,10 +575,6 @@ export const genPanelStyle: GenerateStyle<SharedPickerToken, CSSObject> = (token
             background: new FastColor(controlItemBgActive).setA(0.2).toHexString(),
           },

-          '&:hover': {
-            overflowY: 'auto',
-          },
-
           '> li': {
             margin: 0,
             padding: 0,
PATCH

echo "Patch applied successfully!"
