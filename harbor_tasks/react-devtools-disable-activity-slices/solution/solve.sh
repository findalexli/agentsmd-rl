#!/usr/bin/env bash
set -euo pipefail

cd /workspace/react

# Check if already applied (idempotency check)
if grep -q "enableActivitySlices" packages/react-devtools-shared/src/config/DevToolsFeatureFlags.default.js 2>/dev/null; then
    echo "Patch already applied, skipping"
    exit 0
fi

git apply - <<'PATCH'
diff --git a/packages/react-devtools-shared/src/config/DevToolsFeatureFlags.core-fb.js b/packages/react-devtools-shared/src/config/DevToolsFeatureFlags.core-fb.js
index 9cec3ce338c7..5d9c476b3bfd 100644
--- a/packages/react-devtools-shared/src/config/DevToolsFeatureFlags.core-fb.js
+++ b/packages/react-devtools-shared/src/config/DevToolsFeatureFlags.core-fb.js
@@ -13,6 +13,7 @@
  * It should always be imported from "react-devtools-feature-flags".
  ******************************************************************************/

+export const enableActivitySlices: boolean = false;
 export const enableLogger: boolean = true;
 export const enableStyleXFeatures: boolean = true;
 export const isInternalFacebookBuild: boolean = true;
diff --git a/packages/react-devtools-shared/src/config/DevToolsFeatureFlags.core-oss.js b/packages/react-devtools-shared/src/config/DevToolsFeatureFlags.core-oss.js
index 326b0fd16cca..88b01afc3ee0 100644
--- a/packages/react-devtools-shared/src/config/DevToolsFeatureFlags.core-oss.js
+++ b/packages/react-devtools-shared/src/config/DevToolsFeatureFlags.core-oss.js
@@ -13,6 +13,7 @@
  * It should always be imported from "react-devtools-feature-flags".
  ******************************************************************************/

+export const enableActivitySlices: boolean = __DEV__;
 export const enableLogger: boolean = false;
 export const enableStyleXFeatures: boolean = false;
 export const isInternalFacebookBuild: boolean = false;
diff --git a/packages/react-devtools-shared/src/config/DevToolsFeatureFlags.default.js b/packages/react-devtools-shared/src/config/DevToolsFeatureFlags.default.js
index e7355f8a3475..85f678a980cf 100644
--- a/packages/react-devtools-shared/src/config/DevToolsFeatureFlags.default.js
+++ b/packages/react-devtools-shared/src/config/DevToolsFeatureFlags.default.js
@@ -13,6 +13,7 @@
  * It should always be imported from "react-devtools-feature-flags".
  ******************************************************************************/

+export const enableActivitySlices: boolean = __DEV__;
 export const enableLogger: boolean = false;
 export const enableStyleXFeatures: boolean = false;
 export const isInternalFacebookBuild: boolean = false;
diff --git a/packages/react-devtools-shared/src/config/DevToolsFeatureFlags.extension-fb.js b/packages/react-devtools-shared/src/config/DevToolsFeatureFlags.extension-fb.js
index dc4f05d16fb8..734e7988c858 100644
--- a/packages/react-devtools-shared/src/config/DevToolsFeatureFlags.extension-fb.js
+++ b/packages/react-devtools-shared/src/config/DevToolsFeatureFlags.extension-fb.js
@@ -13,6 +13,7 @@
  * It should always be imported from "react-devtools-feature-flags".
  ******************************************************************************/

+export const enableActivitySlices: boolean = false;
 export const enableLogger: boolean = true;
 export const enableStyleXFeatures: boolean = true;
 export const isInternalFacebookBuild: boolean = true;
diff --git a/packages/react-devtools-shared/src/config/DevToolsFeatureFlags.extension-oss.js b/packages/react-devtools-shared/src/config/DevToolsFeatureFlags.extension-oss.js
index 71df63eef051..c9b665a9096e 100644
--- a/packages/react-devtools-shared/src/config/DevToolsFeatureFlags.extension-oss.js
+++ b/packages/react-devtools-shared/src/config/DevToolsFeatureFlags.extension-oss.js
@@ -13,6 +13,7 @@
  * It should always be imported from "react-devtools-feature-flags".
  ******************************************************************************/

+export const enableActivitySlices: boolean = __DEV__;
 export const enableLogger: boolean = false;
 export const enableStyleXFeatures: boolean = false;
 export const isInternalFacebookBuild: boolean = false;
diff --git a/packages/react-devtools-shared/src/devtools/views/SuspenseTab/SuspenseTab.js b/packages/react-devtools-shared/src/devtools/views/SuspenseTab/SuspenseTab.js
index bd5de7d13e4e..0b195a99c4db 100644
--- a/packages/react-devtools-shared/src/devtools/views/SuspenseTab/SuspenseTab.js
+++ b/packages/react-devtools-shared/src/devtools/views/SuspenseTab/SuspenseTab.js
@@ -16,6 +16,7 @@ import {
   Fragment,
 } from 'react';

+import {enableActivitySlices} from 'react-devtools-feature-flags';
 import {
   localStorageGetItem,
   localStorageSetItem,
@@ -284,7 +285,7 @@ function SuspenseTab(_: {}) {
   const {activities} = useContext(TreeStateContext);
   // If there are no named Activity boundaries, we don't have any tree list and we should hide
   // both the panel and the button to toggle it.
-  const activityListDisabled = activities.length === 0;
+  const activityListDisabled = !enableActivitySlices || activities.length === 0;

   const wrapperTreeRef = useRef<null | HTMLElement>(null);
   const resizeTreeRef = useRef<null | HTMLElement>(null);
PATCH

echo "Patch applied successfully"
