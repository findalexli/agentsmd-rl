#!/bin/bash
set -euo pipefail

cd /workspace/react

# Check if patch already applied (look for reduceReactBuild function)
if grep -q "function reduceReactBuild" packages/react-devtools-extensions/src/contentScripts/reactBuildType.js 2>/dev/null; then
    echo "Patch already applied, skipping"
    exit 0
fi

# Apply the gold patch
git apply - <<'PATCH'
diff --git a/packages/react-devtools-extensions/src/background/setExtensionIconAndPopup.js b/packages/react-devtools-extensions/src/background/setExtensionIconAndPopup.js
index 51f233e284f0..7f92114c87e1 100644
--- a/packages/react-devtools-extensions/src/background/setExtensionIconAndPopup.js
+++ b/packages/react-devtools-extensions/src/background/setExtensionIconAndPopup.js
@@ -1,8 +1,20 @@
+/**
+ * Copyright (c) Meta Platforms, Inc. and affiliates.
+ *
+ * This source code is licensed under the MIT license found in the
+ * LICENSE file in the root directory of this source tree.
+ *
+ * @flow
+ */
 /* global chrome */

 'use strict';
+import type {ReactBuildType} from 'react-devtools-shared/src/backend/types';

-function setExtensionIconAndPopup(reactBuildType, tabId) {
+function setExtensionIconAndPopup(
+  reactBuildType: ReactBuildType,
+  tabId: number,
+) {
   chrome.action.setIcon({
     tabId,
     path: {
diff --git a/packages/react-devtools-extensions/src/contentScripts/installHook.js b/packages/react-devtools-extensions/src/contentScripts/installHook.js
index 490232baf869..4a7cb44eaa31 100644
--- a/packages/react-devtools-extensions/src/contentScripts/installHook.js
+++ b/packages/react-devtools-extensions/src/contentScripts/installHook.js
@@ -10,6 +10,7 @@ import {
   getProfilingSettings,
 } from 'react-devtools-shared/src/utils';
 import {postMessage} from './messages';
+import {createReactRendererListener} from './reactBuildType';

 let resolveHookSettingsInjection: (settings: DevToolsHookSettings) => void;
 let resolveComponentFiltersInjection: (filters: Array<ComponentFilter>) => void;
@@ -67,17 +68,6 @@ if (!window.hasOwnProperty('__REACT_DEVTOOLS_GLOBAL_HOOK__')) {
   // Detect React
   window.__REACT_DEVTOOLS_GLOBAL_HOOK__.on(
     'renderer',
-    function ({reactBuildType}) {
-      window.postMessage(
-        {
-          source: 'react-devtools-hook',
-          payload: {
-            type: 'react-renderer-attached',
-            reactBuildType,
-          },
-        },
-        '*',
-      );
-    },
+    createReactRendererListener(window),
   );
 }
diff --git a/packages/react-devtools-extensions/src/contentScripts/reactBuildType.js b/packages/react-devtools-extensions/src/contentScripts/reactBuildType.js
new file mode 100644
index 000000000000..f1d5326ea96a
--- /dev/null
+++ b/packages/react-devtools-extensions/src/contentScripts/reactBuildType.js
@@ -0,0 +1,50 @@
+/**
+ * Copyright (c) Meta Platforms, Inc. and affiliates.
+ *
+ * This source code is licensed under the MIT license found in the
+ * LICENSE file in the root directory of this source tree.
+ *
+ * @flow
+ */
+import type {ReactBuildType} from 'react-devtools-shared/src/backend/types';
+
+function reduceReactBuild(
+  currentReactBuildType: null | ReactBuildType,
+  nextReactBuildType: ReactBuildType,
+): ReactBuildType {
+  if (
+    currentReactBuildType === null ||
+    currentReactBuildType === 'production'
+  ) {
+    return nextReactBuildType;
+  }
+
+  // We only display the "worst" build type, so if we've already detected a non-production build,
+  // we ignore any future production builds. This way if a page has multiple renderers,
+  // and at least one of them is a non-production build, we'll display that instead of "production".
+  return nextReactBuildType === 'production'
+    ? currentReactBuildType
+    : nextReactBuildType;
+}
+
+export function createReactRendererListener(target: {
+  postMessage: Function,
+  ...
+}): ({reactBuildType: ReactBuildType}) => void {
+  let displayedReactBuild: null | ReactBuildType = null;
+
+  return function ({reactBuildType}) {
+    displayedReactBuild = reduceReactBuild(displayedReactBuild, reactBuildType);
+
+    target.postMessage(
+      {
+        source: 'react-devtools-hook',
+        payload: {
+          type: 'react-renderer-attached',
+          reactBuildType: displayedReactBuild,
+        },
+      },
+      '*',
+    );
+  };
+}
diff --git a/packages/react-devtools-shared/src/backend/types.js b/packages/react-devtools-shared/src/backend/types.js
index c68601f9b633..70ef8e4befef 100644
--- a/packages/react-devtools-shared/src/backend/types.js
+++ b/packages/react-devtools-shared/src/backend/types.js
@@ -603,3 +603,10 @@ export type DevToolsHookSettings = {
 export type DevToolsSettings = DevToolsHookSettings & {
   componentFilters: Array<ComponentFilter>,
 };
+
+export type ReactBuildType =
+  | 'deadcode'
+  | 'development'
+  | 'outdated'
+  | 'production'
+  | 'unminified';
diff --git a/packages/react-devtools-shared/src/hook.js b/packages/react-devtools-shared/src/hook.js
index 5764a8bee4bf..f24ae48c3601 100644
--- a/packages/react-devtools-shared/src/hook.js
+++ b/packages/react-devtools-shared/src/hook.js
@@ -17,6 +17,7 @@ import type {
   DevToolsBackend,
   DevToolsHookSettings,
   ProfilingSettings,
+  ReactBuildType,
 } from './backend/types';
 import type {ComponentFilter} from './frontend/types';

@@ -71,7 +72,7 @@ export function installHook(
     return null;
   }

-  function detectReactBuildType(renderer: ReactRenderer) {
+  function detectReactBuildType(renderer: ReactRenderer): ReactBuildType {
     try {
       if (typeof renderer.version === 'string') {
         // React DOM Fiber (16+)
@@ -211,7 +212,7 @@ export function installHook(
     const id = ++uidCounter;
     renderers.set(id, renderer);

-    const reactBuildType = hasDetectedBadDCE
+    const reactBuildType: ReactBuildType = hasDetectedBadDCE
       ? 'deadcode'
       : detectReactBuildType(renderer);

diff --git a/scripts/flow/react-devtools.js b/scripts/flow/react-devtools.js
index 21f9e441ada6..ddd925c2443d 100644
--- a/scripts/flow/react-devtools.js
+++ b/scripts/flow/react-devtools.js
@@ -17,6 +17,16 @@ declare const __IS_CHROME__: boolean;
 declare const __IS_EDGE__: boolean;
 declare const __IS_NATIVE__: boolean;

+interface ExtensionAction {
+  /** @see {@link https://developer.mozilla.org/en-US/docs/Mozilla/Add-ons/WebExtensions/API/action/setIcon} */
+  setIcon(details: {
+    tabId: number,
+    path?: string | {[iconSize: string]: string},
+  }): void;
+  /** @see {@link https://developer.mozilla.org/en-US/docs/Mozilla/Add-ons/WebExtensions/API/action/setPopup} */
+  setPopup(details: {tabId: number, popup: string}): void;
+}
+
 interface ExtensionDevtools {
   /** @see {@link https://developer.mozilla.org/en-US/docs/Mozilla/Add-ons/WebExtensions/API/devtools/inspectedWindow} */
   inspectedWindow: $FlowFixMe;
@@ -73,6 +83,8 @@ interface ExtensionRuntime {
     extensionId: string,
     connectInfo?: {name?: string, includeTlsChannelId?: boolean},
   ): ExtensionRuntimePort;
+  /** @see {@link https://developer.mozilla.org/en-US/docs/Mozilla/Add-ons/WebExtensions/API/runtime/getURL} */
+  getURL(path: string): string;
   /** @see {@link https://developer.mozilla.org/en-US/docs/Mozilla/Add-ons/WebExtensions/API/runtime/onMessage} */
   onMessage: ExtensionEvent<
     (
@@ -108,6 +120,8 @@ interface ExtensionTabs {
 }

 interface ExtensionAPI {
+  /** @see {@link https://developer.mozilla.org/en-US/docs/Mozilla/Add-ons/WebExtensions/API/action} */
+  action: ExtensionAction;
   devtools: ExtensionDevtools;
   /** @see {@link https://developer.mozilla.org/en-US/docs/Mozilla/Add-ons/WebExtensions/API/permissions} */
   permissions: $FlowFixMe;
PATCH

echo "Patch applied successfully"
