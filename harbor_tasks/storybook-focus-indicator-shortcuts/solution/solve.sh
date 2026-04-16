#!/bin/bash
set -e

cd /workspace/storybook

# Check if already patched (idempotency check)
if grep -q "if (!wasPanelShown)" code/core/src/manager-api/modules/shortcuts.ts; then
    echo "Patch already applied, skipping"
    exit 0
fi

# Apply the gold patch
cat <<'PATCH' | git apply -
diff --git a/code/core/src/manager-api/modules/shortcuts.ts b/code/core/src/manager-api/modules/shortcuts.ts
index 58f352467407..b991713a5c2f 100644
--- a/code/core/src/manager-api/modules/shortcuts.ts
+++ b/code/core/src/manager-api/modules/shortcuts.ts
@@ -380,6 +380,13 @@ export const init: ModuleFn = ({ store, fullAPI, provider }) => {
               }
             });
           }
+
+          if (!wasPanelShown) {
+            fullAPI.focusOnUIElement(focusableUIElements.addonPanel, {
+              forceFocus: true,
+              poll: true,
+            });
+          }
           break;
         }

@@ -402,6 +409,14 @@ export const init: ModuleFn = ({ store, fullAPI, provider }) => {
               }
             });
           }
+
+          if (!wasNavShown) {
+            fullAPI.focusOnUIElement(focusableUIElements.sidebarRegion, {
+              forceFocus: true,
+              poll: true,
+            });
+          }
+
           break;
         }

diff --git a/code/core/src/manager/components/panel/Panel.tsx b/code/core/src/manager/components/panel/Panel.tsx
index 7682692dbacd..135d10b83cd7 100644
--- a/code/core/src/manager/components/panel/Panel.tsx
+++ b/code/core/src/manager/components/panel/Panel.tsx
@@ -166,7 +166,7 @@ export const AddonPanel = React.memo<{
         Addon panel
       </h2>
       <StatelessTabsView
-        id="storybook-panel-root"
+        id={focusableUIElements.storyPanelRoot}
         showToolsWhenEmpty
         emptyState={emptyState}
         selected={selectedPanel ?? undefined}
diff --git a/code/core/src/manager/components/preview/tools/addons.tsx b/code/core/src/manager/components/preview/tools/addons.tsx
index 4fd70a399811..0f5aeb4de4e4 100644
--- a/code/core/src/manager/components/preview/tools/addons.tsx
+++ b/code/core/src/manager/components/preview/tools/addons.tsx
@@ -9,7 +9,6 @@ import { Consumer, types } from 'storybook/manager-api';
 import type { Combo } from 'storybook/manager-api';

 import { focusableUIElements } from '../../../../manager-api/modules/layout';
-import { useRegionFocusAnimation } from '../../layout/useLandmarkIndicator';

 const SHOW_ADDON_PANEL_BUTTON_ID = 'storybook-show-addon-panel';

@@ -17,15 +16,12 @@ const menuMapper = ({ api, state }: Combo) => ({
   isVisible: api.getIsPanelShown(),
   singleStory: state.singleStory,
   panelPosition: state.layout.panelPosition,
-  showPanel: async (animateLandmark?: (e: HTMLElement | null) => void) => {
+  showPanel: async (forceFocus: boolean) => {
     api.togglePanel(true);
-    const success = await api.focusOnUIElement(focusableUIElements.addonPanel, {
-      forceFocus: true,
+    api.focusOnUIElement(focusableUIElements.addonPanel, {
+      forceFocus,
       poll: true,
     });
-    if (success) {
-      animateLandmark?.(document.getElementById(focusableUIElements.addonPanel));
-    }
   },
 });

@@ -35,8 +31,6 @@ export const addonsTool: Addon_BaseType = {
   type: types.TOOL,
   match: ({ viewMode, tabId }) => viewMode === 'story' && !tabId,
   render: () => {
-    const animateLandmark = useRegionFocusAnimation();
-
     return (
       <Consumer filter={menuMapper}>
         {({ isVisible, showPanel, singleStory, panelPosition }) =>
@@ -49,11 +43,11 @@ export const addonsTool: Addon_BaseType = {
                 ariaLabel="Show addon panel"
                 id={SHOW_ADDON_PANEL_BUTTON_ID}
                 key="addons"
-                onClick={() => showPanel()}
+                onClick={() => showPanel(false)}
                 onKeyDown={(e) => {
                   if (e.key === 'Enter' || e.key === ' ') {
                     e.preventDefault();
-                    showPanel(animateLandmark);
+                    showPanel(true);
                   }
                 }}
               >
diff --git a/code/core/src/manager/components/preview/tools/menu.tsx b/code/core/src/manager/components/preview/tools/menu.tsx
index 404177ba6f57..a8b94c3e2e13 100644
--- a/code/core/src/manager/components/preview/tools/menu.tsx
+++ b/code/core/src/manager/components/preview/tools/menu.tsx
@@ -9,21 +9,17 @@ import { Consumer, types } from 'storybook/manager-api';
 import type { Combo } from 'storybook/manager-api';

 import { focusableUIElements } from '../../../../manager-api/modules/layout';
-import { useRegionFocusAnimation } from '../../layout/useLandmarkIndicator';

 const menuMapper = ({ api, state }: Combo) => ({
   isVisible: api.getIsNavShown(),
   singleStory: state.singleStory,
   viewMode: state.viewMode,
-  showSidebar: async (animateLandmark?: (e: HTMLElement | null) => void) => {
+  showSidebar: async (forceFocus: boolean) => {
     api.toggleNav(true);
-    const success = await api.focusOnUIElement(focusableUIElements.sidebarRegion, {
-      forceFocus: true,
+    api.focusOnUIElement(focusableUIElements.sidebarRegion, {
+      forceFocus,
       poll: true,
     });
-    if (success) {
-      animateLandmark?.(document.getElementById(focusableUIElements.sidebarRegion));
-    }
   },
 });

@@ -34,8 +30,6 @@ export const menuTool: Addon_BaseType = {
   // @ts-expect-error (non strict)
   match: ({ viewMode }) => ['story', 'docs'].includes(viewMode),
   render: () => {
-    const animateLandmark = useRegionFocusAnimation();
-
     return (
       <Consumer filter={menuMapper}>
         {({ isVisible, showSidebar, singleStory }) =>
@@ -48,11 +42,11 @@ export const menuTool: Addon_BaseType = {
                 ariaLabel="Show sidebar"
                 id={focusableUIElements.showSidebar}
                 key="menu"
-                onClick={() => showSidebar()}
+                onClick={() => showSidebar(false)}
                 onKeyDown={(e) => {
                   if (e.key === 'Enter' || e.key === ' ') {
                     e.preventDefault();
-                    showSidebar(animateLandmark);
+                    showSidebar(true);
                   }
                 }}
               >
PATCH

# Recompile the affected package
yarn nx compile storybook || yarn nx run-many -t compile --projects=storybook

echo "Patch applied successfully"
