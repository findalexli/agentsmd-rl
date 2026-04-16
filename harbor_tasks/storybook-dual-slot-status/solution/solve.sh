#!/bin/bash
set -e

cd /workspace/storybook

# Apply the gold patch for dual-slot status icons
patch -p1 <<'PATCH'
diff --git a/code/core/src/manager/utils/status.tsx b/code/core/src/manager/utils/status.tsx
index eddc9c101c37..f4fe5b48726d 100644
--- a/code/core/src/manager/utils/status.tsx
+++ b/code/core/src/manager/utils/status.tsx
@@ -2,7 +2,12 @@ import type { ReactElement } from 'react';
 import React from 'react';

 import type { StatusValue } from 'storybook/internal/types';
-import { type API_HashEntry, type StatusesByStoryIdAndTypeId } from 'storybook/internal/types';
+import {
+  CHANGE_DETECTION_STATUS_TYPE_ID,
+  type API_HashEntry,
+  type StatusByTypeId,
+  type StatusesByStoryIdAndTypeId,
+} from 'storybook/internal/types';

 import { CircleIcon } from '@storybook/icons';

@@ -121,6 +126,22 @@ export const getStatus = memoizerific(10)((theme: Theme, status: StatusValue):
   return statusMapping[status];
 });

+export function getChangeDetectionStatus(statuses: StatusByTypeId): {
+  changeStatus: StatusValue;
+  testStatus: StatusValue;
+} {
+  const changeValues = Object.values(statuses)
+    .filter((status) => status.typeId === CHANGE_DETECTION_STATUS_TYPE_ID)
+    .map((status) => status.value);
+  const testValues = Object.values(statuses)
+    .filter((status) => status.typeId !== CHANGE_DETECTION_STATUS_TYPE_ID)
+    .map((status) => status.value);
+  return {
+    changeStatus: getMostCriticalStatusValue(changeValues),
+    testStatus: getMostCriticalStatusValue(testValues),
+  };
+}
+
 export const getMostCriticalStatusValue = (statusValues: StatusValue[]): StatusValue => {
   return statusPriority.reduce(
     (acc, value) => (statusValues.includes(value) ? value : acc),
@@ -154,3 +175,43 @@ export function getGroupStatus(
     return acc;
   }, {});
 }
+
+export function getGroupDualStatus(
+  collapsedData: {
+    [x: string]: Partial<API_HashEntry>;
+  },
+  allStatuses: StatusesByStoryIdAndTypeId
+): Record<string, { change: StatusValue; test: StatusValue }> {
+  return Object.values(collapsedData).reduce<
+    Record<string, { change: StatusValue; test: StatusValue }>
+  >((acc, item) => {
+    if (item.type === 'group' || item.type === 'component' || item.type === 'story') {
+      // @ts-expect-error (non strict)
+      const leafs = getDescendantIds(collapsedData as any, item.id, false)
+        .map((id) => collapsedData[id])
+        .filter((i) => i.type === 'story');
+
+      const allDescendantStatuses = leafs.flatMap(
+        (story) =>
+          Object.values(allStatuses[story.id!] || {}) as Array<{
+            typeId: string;
+            value: StatusValue;
+          }>
+      );
+
+      const changeValues = allDescendantStatuses
+        .filter((s: { typeId: string }) => s.typeId === CHANGE_DETECTION_STATUS_TYPE_ID)
+        .map((s: { value: StatusValue }) => s.value);
+      const testValues = allDescendantStatuses
+        .filter((s: { typeId: string }) => s.typeId !== CHANGE_DETECTION_STATUS_TYPE_ID)
+        .map((s: { value: StatusValue }) => s.value);
+
+      // @ts-expect-error (non strict)
+      acc[item.id] = {
+        change: getMostCriticalStatusValue(changeValues),
+        test: getMostCriticalStatusValue(testValues),
+      };
+    }
+    return acc;
+  }, {});
+}
PATCH

echo "Patch applied successfully"
