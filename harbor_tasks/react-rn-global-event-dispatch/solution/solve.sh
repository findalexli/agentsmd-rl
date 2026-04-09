#!/usr/bin/env bash
set -euo pipefail

cd /workspace/react

# Idempotent: skip if already applied
if grep -q 'const currentEvent = global.event' packages/react-native-renderer/src/legacy-events/EventPluginUtils.js 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/packages/react-native-renderer/src/legacy-events/EventPluginUtils.js b/packages/react-native-renderer/src/legacy-events/EventPluginUtils.js
index 64a05cef33fa..2027ac2e20fc 100644
--- a/packages/react-native-renderer/src/legacy-events/EventPluginUtils.js
+++ b/packages/react-native-renderer/src/legacy-events/EventPluginUtils.js
@@ -67,6 +67,9 @@ function validateEventDispatches(event) {
  */
 export function executeDispatch(event, listener, inst) {
   event.currentTarget = getNodeFromInstance(inst);
+  const currentEvent = global.event;
+  global.event = event;
+
   try {
     listener(event);
   } catch (error) {
@@ -77,6 +80,8 @@ export function executeDispatch(event, listener, inst) {
       // TODO: Make sure this error gets logged somehow.
     }
   }
+
+  global.event = currentEvent;
   event.currentTarget = null;
 }

PATCH

echo "Patch applied successfully."
