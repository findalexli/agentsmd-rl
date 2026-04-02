#!/usr/bin/env bash
set -euo pipefail

cd /workspace/react

# Check if already applied (idempotency check)
if grep -q "createSuspensePanel();" packages/react-devtools-extensions/src/main/index.js && \
   ! grep -q "enableSuspenseTab" packages/react-devtools-shared/src/backend/agent.js; then
    echo "Patch already applied, skipping."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/packages/react-devtools-extensions/src/main/index.js b/packages/react-devtools-extensions/src/main/index.js
index 75a81c92ddcf..c12e392881b6 100644
--- a/packages/react-devtools-extensions/src/main/index.js
+++ b/packages/react-devtools-extensions/src/main/index.js
@@ -167,10 +167,6 @@ function createBridgeAndStore() {
     supportsClickToInspect: true,
   });

-  store.addListener('enableSuspenseTab', () => {
-    createSuspensePanel();
-  });
-
   store.addListener('settingsUpdated', (hookSettings, componentFilters) => {
     chrome.storage.local.set({...hookSettings, componentFilters});
   });
@@ -565,8 +561,7 @@ function mountReactDevTools() {
   createProfilerPanel();
   createSourcesEditorPanel();
   createElementsInspectPanel();
-  // Suspense Tab is created via the hook
-  // TODO(enableSuspenseTab): Create eagerly once Suspense tab is stable
+  createSuspensePanel();
 }

 let reactPollingInstance = null;
diff --git a/packages/react-devtools-shared/src/backend/agent.js b/packages/react-devtools-shared/src/backend/agent.js
index ee7b05882038..78387326f379 100644
--- a/packages/react-devtools-shared/src/backend/agent.js
+++ b/packages/react-devtools-shared/src/backend/agent.js
@@ -38,7 +38,7 @@ import type {
   ElementType,
 } from 'react-devtools-shared/src/frontend/types';
 import type {GroupItem} from './views/TraceUpdates/canvas';
-import {gte, isReactNativeEnvironment} from './utils';
+import {isReactNativeEnvironment} from './utils';
 import {
   sessionStorageGetItem,
   sessionStorageRemoveItem,
@@ -961,16 +961,6 @@ export default class Agent extends EventEmitter<{

     rendererInterface.setTraceUpdatesEnabled(this._traceUpdatesEnabled);

-    const renderer = rendererInterface.renderer;
-    if (renderer !== null) {
-      const devRenderer = renderer.bundleType === 1;
-      const enableSuspenseTab =
-        devRenderer && gte(renderer.version, '19.3.0-canary');
-      if (enableSuspenseTab) {
-        this._bridge.send('enableSuspenseTab');
-      }
-    }
-
     // When the renderer is attached, we need to tell it whether
     // we remember the previous selection that we'd like to restore.
     // It'll start tracking mounts for matches to the last selection path.
diff --git a/packages/react-devtools-shared/src/bridge.js b/packages/react-devtools-shared/src/bridge.js
index bc752ec4b8cd..2e30e909841f 100644
--- a/packages/react-devtools-shared/src/bridge.js
+++ b/packages/react-devtools-shared/src/bridge.js
@@ -199,7 +199,6 @@ export type BackendEvents = {
   backendInitialized: [],
   backendVersion: [string],
   bridgeProtocol: [BridgeProtocol],
-  enableSuspenseTab: [],
   extensionBackendInitialized: [],
   fastRefreshScheduled: [],
   getSavedPreferences: [],
diff --git a/packages/react-devtools-shared/src/devtools/store.js b/packages/react-devtools-shared/src/devtools/store.js
index 45ced5d4fdd3..cb3bdccdec28 100644
--- a/packages/react-devtools-shared/src/devtools/store.js
+++ b/packages/react-devtools-shared/src/devtools/store.js
@@ -143,7 +143,6 @@ export default class Store extends EventEmitter<{
   backendVersion: [],
   collapseNodesByDefault: [],
   componentFilters: [],
-  enableSuspenseTab: [],
   error: [Error],
   hookSettings: [$ReadOnly<DevToolsHookSettings>],
   hostInstanceSelected: [Element['id'] | null],
@@ -239,8 +238,6 @@ export default class Store extends EventEmitter<{
   _supportsClickToInspect: boolean = false;
   _supportsTimeline: boolean = false;
   _supportsTraceUpdates: boolean = false;
-  // Dynamically set if the renderer supports the Suspense tab.
-  _supportsSuspenseTab: boolean = false;

   _isReloadAndProfileFrontendSupported: boolean = false;
   _isReloadAndProfileBackendSupported: boolean = false;
@@ -341,7 +338,6 @@ export default class Store extends EventEmitter<{
     bridge.addListener('hookSettings', this.onHookSettings);
     bridge.addListener('backendInitialized', this.onBackendInitialized);
     bridge.addListener('selectElement', this.onHostInstanceSelected);
-    bridge.addListener('enableSuspenseTab', this.onEnableSuspenseTab);
   }

   // This is only used in tests to avoid memory leaks.
@@ -2394,15 +2390,6 @@ export default class Store extends EventEmitter<{
     }
   }

-  get supportsSuspenseTab(): boolean {
-    return this._supportsSuspenseTab;
-  }
-
-  onEnableSuspenseTab = (): void => {
-    this._supportsSuspenseTab = true;
-    this.emit('enableSuspenseTab');
-  };
-
   // The Store should never throw an Error without also emitting an event.
   // Otherwise Store errors will be invisible to users,
   // but the downstream errors they cause will be reported as bugs.
diff --git a/packages/react-devtools-shared/src/devtools/views/DevTools.js b/packages/react-devtools-shared/src/devtools/views/DevTools.js
index dc4715749782..bf541f667287 100644
--- a/packages/react-devtools-shared/src/devtools/views/DevTools.js
+++ b/packages/react-devtools-shared/src/devtools/views/DevTools.js
@@ -135,21 +135,7 @@ const suspenseTab = {
   title: 'React Suspense',
 };

-const defaultTabs = [componentsTab, profilerTab];
-const tabsWithSuspense = [componentsTab, profilerTab, suspenseTab];
-
-function useIsSuspenseTabEnabled(store: Store): boolean {
-  const subscribe = useCallback(
-    (onStoreChange: () => void) => {
-      store.addListener('enableSuspenseTab', onStoreChange);
-      return () => {
-        store.removeListener('enableSuspenseTab', onStoreChange);
-      };
-    },
-    [store],
-  );
-  return React.useSyncExternalStore(subscribe, () => store.supportsSuspenseTab);
-}
+const tabs = [componentsTab, profilerTab, suspenseTab];

 export default function DevTools({
   bridge,
@@ -183,8 +169,6 @@ export default function DevTools({
     LOCAL_STORAGE_DEFAULT_TAB_KEY,
     defaultTab,
   );
-  const enableSuspenseTab = useIsSuspenseTabEnabled(store);
-  const tabs = enableSuspenseTab ? tabsWithSuspense : defaultTabs;

   let tab = currentTab;

@@ -364,17 +348,15 @@ export default function DevTools({
                                         }
                                       />
                                     </div>
-                                    {enableSuspenseTab && (
-                                      <div
-                                        className={styles.TabContent}
-                                        hidden={tab !== 'suspense'}>
-                                        <SuspenseTab
-                                          portalContainer={
-                                            suspensePortalContainer
-                                          }
-                                        />
-                                      </div>
-                                    )}
+                                    <div
+                                      className={styles.TabContent}
+                                      hidden={tab !== 'suspense'}>
+                                      <SuspenseTab
+                                        portalContainer={
+                                          suspensePortalContainer
+                                        }
+                                      />
+                                    </div>
                                   </div>
                                   {editorPortalContainer ? (
                                     <EditorPane
PATCH

echo "Patch applied successfully."
