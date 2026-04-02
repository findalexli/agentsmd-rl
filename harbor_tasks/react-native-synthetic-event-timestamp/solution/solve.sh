#!/bin/bash
set -euo pipefail

cd /workspace/react

# Check if already applied
timeStampFile="packages/react-native-renderer/src/legacy-events/SyntheticEvent.js"
if grep -q "event.timeStamp || event.timestamp || currentTimeStamp()" "$timeStampFile" 2>/dev/null; then
    echo "Patch already applied"
    exit 0
fi

# Apply the fix for SyntheticEvent timeStamp handling
git apply - <<'PATCH'
diff --git a/packages/react-native-renderer/src/legacy-events/SyntheticEvent.js b/packages/react-native-renderer/src/legacy-events/SyntheticEvent.js
index 723daa0dc9e5..b6a4bf4e7cbb 100644
--- a/packages/react-native-renderer/src/legacy-events/SyntheticEvent.js
+++ b/packages/react-native-renderer/src/legacy-events/SyntheticEvent.js
@@ -11,6 +11,21 @@ import assign from 'shared/assign';

 const EVENT_POOL_SIZE = 10;

+let currentTimeStamp = () => {
+  // Lazily define the function based on the existence of performance.now()
+  if (
+    typeof performance === 'object' &&
+    performance !== null &&
+    typeof performance.now === 'function'
+  ) {
+    currentTimeStamp = () => performance.now();
+  } else {
+    currentTimeStamp = () => Date.now();
+  }
+
+  return currentTimeStamp();
+};
+
 /**
  * @interface Event
  * @see http://www.w3.org/TR/DOM-Level-3-Events/
@@ -26,7 +41,7 @@ const EventInterface = {
   bubbles: null,
   cancelable: null,
   timeStamp: function (event) {
-    return event.timeStamp || Date.now();
+    return event.timeStamp || event.timestamp || currentTimeStamp();
   },
   defaultPrevented: null,
   isTrusted: null,
PATCH

echo "Patch applied successfully"
