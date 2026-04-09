#!/bin/bash
set -e

cd /workspace/ant-design

# Apply the gold patch for TimePicker scroll fix
patch -p1 << 'PATCH'
diff --git a/components/date-picker/style/panel.ts b/components/date-picker/style/panel.ts
index c28cb5176099..8f3341337572 100644
--- a/components/date-picker/style/panel.ts
+++ b/components/date-picker/style/panel.ts
@@ -539,7 +539,7 @@ export const genPanelStyle: GenerateStyle<SharedPickerToken, CSSObject> = (toke
           width: timeColumnWidth,
           margin: `${unit(paddingXXS)} 0`,
           padding: 0,
-          overflowY: 'hidden',
+          overflowY: 'auto',
           textAlign: 'start',
           listStyle: 'none',
           transition: `background-color ${motionDurationMid}`,
@@ -575,10 +575,6 @@ export const genPanelStyle: GenerateStyle<SharedPickerToken, CSSObject> = (toke
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

# Idempotency check: verify the patch was applied by looking for the distinctive change
grep -q "overflowY: 'auto'," components/date-picker/style/panel.ts && echo "Patch applied successfully"
