#!/bin/bash
set -euo pipefail

# Idempotent patch application for RN event timing fix
# Check if already applied by looking for getEventType function

if grep -q "function getEventType" /workspace/react/packages/react-native-renderer/src/ReactFiberConfigFabric.js 2>/dev/null; then
    echo "Patch already applied, skipping..."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/packages/react-native-renderer/src/ReactFiberConfigFabric.js b/packages/react-native-renderer/src/ReactFiberConfigFabric.js
index 4eeac5433777..26f921bf4297 100644
--- a/packages/react-native-renderer/src/ReactFiberConfigFabric.js
+++ b/packages/react-native-renderer/src/ReactFiberConfigFabric.js
@@ -422,14 +422,48 @@ export function resolveUpdatePriority(): EventPriority {
   return DefaultEventPriority;
 }

-export function trackSchedulerEvent(): void {}
+let schedulerEvent: void | Event = undefined;
+export function trackSchedulerEvent(): void {
+  schedulerEvent = global.event;
+}
+
+function getEventType(event: Event): null | string {
+  if (event.type) {
+    return event.type;
+  }
+
+  // Legacy implementation. RN does not define the `type` property on the event object yet.
+  // $FlowExpectedError[prop-missing]
+  const dispatchConfig = event.dispatchConfig;
+  if (
+    dispatchConfig == null ||
+    dispatchConfig.phasedRegistrationNames == null
+  ) {
+    return null;
+  }
+
+  const rawEventType =
+    dispatchConfig.phasedRegistrationNames.bubbled ||
+    dispatchConfig.phasedRegistrationNames.captured;
+  if (!rawEventType) {
+    return null;
+  }
+
+  if (rawEventType.startsWith('on')) {
+    return rawEventType.slice(2).toLowerCase();
+  }
+
+  return rawEventType.toLowerCase();
+}

 export function resolveEventType(): null | string {
-  return null;
+  const event = global.event;
+  return event && event !== schedulerEvent ? getEventType(event) : null;
 }

 export function resolveEventTimeStamp(): number {
-  return -1.1;
+  const event = global.event;
+  return event && event !== schedulerEvent ? event.timeStamp : -1.1;
 }

 export function shouldAttemptEagerTransition(): boolean {
PATCH

echo "Patch applied successfully!"
