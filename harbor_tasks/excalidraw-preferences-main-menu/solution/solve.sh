#!/bin/bash
set -e

cd /workspace/excalidraw

# Check if already applied
if grep -q "toolLock" packages/excalidraw/actions/shortcuts.ts 2>/dev/null; then
    echo "Patch already applied, skipping"
    exit 0
fi

# Apply the gold patch
cat <<'PATCH' | git apply -
diff --git a/excalidraw-app/components/AppMainMenu.tsx b/excalidraw-app/components/AppMainMenu.tsx
index e51d1763b8a4..a3f847385f48 100644
--- a/excalidraw-app/components/AppMainMenu.tsx
+++ b/excalidraw-app/components/AppMainMenu.tsx
@@ -77,6 +77,7 @@ export const AppMainMenu: React.FC<{
         </MainMenu.Item>
       )}
       <MainMenu.Separator />
+      <MainMenu.DefaultItems.Preferences />
       <MainMenu.DefaultItems.ToggleTheme
         allowSystemTheme
         theme={props.theme}
diff --git a/packages/excalidraw/actions/shortcuts.ts b/packages/excalidraw/actions/shortcuts.ts
index ca593c340220..ca4119d25152 100644
--- a/packages/excalidraw/actions/shortcuts.ts
+++ b/packages/excalidraw/actions/shortcuts.ts
@@ -55,7 +55,8 @@ export type ShortcutName =
   | "saveScene"
   | "imageExport"
   | "commandPalette"
-  | "searchMenu";
+  | "searchMenu"
+  | "toolLock";

 const shortcutMap: Record<ShortcutName, string[]> = {
   toggleTheme: [getShortcutKey("Shift+Alt+D")],
@@ -117,6 +118,7 @@ const shortcutMap: Record<ShortcutName, string[]> = {
   toggleShortcuts: [getShortcutKey("?")],
   searchMenu: [getShortcutKey("CtrlOrCmd+F")],
   wrapSelectionInFrame: [],
+  toolLock: [getShortcutKey("Q")],
 };

 export const getShortcutFromShortcutName = (name: ShortcutName, idx = 0) => {
diff --git a/packages/excalidraw/components/dropdownMenu/DropdownMenu.tsx b/packages/excalidraw/components/dropdownMenu/DropdownMenu.tsx
index e5b5441efd67..5b0ef39c3e99 100644
--- a/packages/excalidraw/components/dropdownMenu/DropdownMenu.tsx
+++ b/packages/excalidraw/components/dropdownMenu/DropdownMenu.tsx
@@ -12,6 +12,7 @@ import DropdownMenuItemLink from "./DropdownMenuItemLink";
 import MenuSeparator from "./DropdownMenuSeparator";
 import DropdownMenuSub from "./DropdownMenuSub";
 import DropdownMenuTrigger from "./DropdownMenuTrigger";
+import DropdownMenuItemCheckbox from "./DropdownMenuItemCheckbox";
 import {
   getMenuContentComponent,
   getMenuTriggerComponent,
@@ -57,6 +58,7 @@ const DropdownMenu = ({
 DropdownMenu.Trigger = DropdownMenuTrigger;
 DropdownMenu.Content = DropdownMenuContent;
 DropdownMenu.Item = DropdownMenuItem;
+DropdownMenu.ItemCheckbox = DropdownMenuItemCheckbox;
 DropdownMenu.ItemLink = DropdownMenuItemLink;
 DropdownMenu.ItemCustom = DropdownMenuItemCustom;
 DropdownMenu.Group = DropdownMenuGroup;
diff --git a/packages/excalidraw/components/dropdownMenu/DropdownMenuItem.tsx b/packages/excalidraw/components/dropdownMenu/DropdownMenuItem.tsx
index 7cc10b95d4ca..55ffcd584406 100644
--- a/packages/excalidraw/components/dropdownMenu/DropdownMenuItem.tsx
+++ b/packages/excalidraw/components/dropdownMenu/DropdownMenuItem.tsx
@@ -16,6 +16,17 @@ import MenuItemContent from "./DropdownMenuItemContent";

 import type { JSX } from "react";

+export type DropdownMenuItemProps = {
+  icon?: JSX.Element;
+  badge?: React.ReactNode;
+  value?: string | number | undefined;
+  onSelect?: (event: Event) => void;
+  children: React.ReactNode;
+  shortcut?: string;
+  selected?: boolean;
+  className?: string;
+} & Omit<React.ButtonHTMLAttributes<HTMLButtonElement>, "onSelect">;
+
 const DropdownMenuItem = ({
   icon,
   badge,
@@ -26,19 +37,7 @@ const DropdownMenuItem = ({
   selected,
   onSelect,
   ...rest
-}: {
-  icon?: JSX.Element;
-  badge?: React.ReactNode;
-  value?: string | number | undefined;
-  onSelect?: (event: Event) => void;
-  children: React.ReactNode;
-  shortcut?: string;
-  selected?: boolean;
-  className?: string;
-} & Omit<
-  React.ButtonHTMLAttributes<HTMLButtonElement>,
-  "onSelect" | "onClick"
->) => {
+}: DropdownMenuItemProps) => {
   const handleSelect = useHandleDropdownMenuItemSelect(onSelect);

   return (
diff --git a/packages/excalidraw/components/dropdownMenu/DropdownMenuItemCheckbox.tsx b/packages/excalidraw/components/dropdownMenu/DropdownMenuItemCheckbox.tsx
new file mode 100644
index 000000000000..c116e5bde70d
--- /dev/null
+++ b/packages/excalidraw/components/dropdownMenu/DropdownMenuItemCheckbox.tsx
@@ -0,0 +1,15 @@
+import { checkIcon, emptyIcon } from "../icons";
+
+import DropdownMenuItem from "./DropdownMenuItem";
+
+import type { DropdownMenuItemProps } from "./DropdownMenuItem";
+
+const DropdownMenuItemCheckbox = (
+  props: Omit<DropdownMenuItemProps, "icon"> & { checked: boolean },
+) => {
+  return (
+    <DropdownMenuItem {...props} icon={props.checked ? checkIcon : emptyIcon} />
+  );
+};
+
+export default DropdownMenuItemCheckbox;
diff --git a/packages/excalidraw/components/icons.tsx b/packages/excalidraw/components/icons.tsx
index f5ce947d7a97..6a7a93408349 100644
--- a/packages/excalidraw/components/icons.tsx
+++ b/packages/excalidraw/components/icons.tsx
@@ -2408,3 +2408,20 @@ export const chevronRight = createIcon(
   </g>,
   tablerIconProps,
 );
+
+// tabler-icons: adjustments-horizontal
+export const settingsIcon = createIcon(
+  <g strokeWidth={1.25}>
+    <path stroke="none" d="M0 0h24v24H0z" fill="none" />
+    <path d="M14 6m-2 0a2 2 0 1 0 4 0a2 2 0 1 0 -4 0" />
+    <path d="M4 6l8 0" />
+    <path d="M16 6l4 0" />
+    <path d="M8 12m-2 0a2 2 0 1 0 4 0a2 2 0 1 0 -4 0" />
+    <path d="M4 12l2 0" />
+    <path d="M10 12l10 0" />
+    <path d="M17 18m-2 0a2 2 0 1 0 4 0a2 2 0 1 0 -4 0" />
+    <path d="M4 18l11 0" />
+    <path d="M19 18l1 0" />
+  </g>,
+  tablerIconProps,
+);
diff --git a/packages/excalidraw/components/main-menu/DefaultItems.tsx b/packages/excalidraw/components/main-menu/DefaultItems.tsx
index 2a00a79a7124..04cea3da48fe 100644
--- a/packages/excalidraw/components/main-menu/DefaultItems.tsx
+++ b/packages/excalidraw/components/main-menu/DefaultItems.tsx
@@ -9,9 +9,14 @@ import {
   actionLoadScene,
   actionSaveToActiveFile,
   actionShortcuts,
+  actionToggleGridMode,
+  actionToggleObjectsSnapMode,
   actionToggleSearchMenu,
+  actionToggleStats,
   actionToggleTheme,
+  actionToggleZenMode,
 } from "../../actions";
+import { actionToggleViewMode } from "../../actions/actionToggleViewMode";
 import { getShortcutFromShortcutName } from "../../actions/shortcuts";
 import { trackEvent } from "../../analytics";
 import { useUIAppState } from "../../context/ui-appState";
@@ -23,13 +28,16 @@ import {
   useExcalidrawActionManager,
   useExcalidrawElements,
   useAppProps,
+  useApp,
 } from "../App";
 import { openConfirmModal } from "../OverwriteConfirm/OverwriteConfirmState";
 import Trans from "../Trans";
 import DropdownMenuItem from "../dropdownMenu/DropdownMenuItem";
+import DropdownMenuItemCheckbox from "../dropdownMenu/DropdownMenuItemCheckbox";
 import DropdownMenuItemContentRadio from "../dropdownMenu/DropdownMenuItemContentRadio";
 import DropdownMenuItemLink from "../dropdownMenu/DropdownMenuItemLink";
-import { GithubIcon, DiscordIcon, XBrandIcon } from "../icons";
+import DropdownMenuSub from "../dropdownMenu/DropdownMenuSub";
+import { GithubIcon, DiscordIcon, XBrandIcon, settingsIcon } from "../icons";
 import {
   boltIcon,
   DeviceDesktopIcon,
@@ -397,3 +405,152 @@ export const LiveCollaborationTrigger = ({
 };

 LiveCollaborationTrigger.displayName = "LiveCollaborationTrigger";
+
+const PreferencesToggleToolLockItem = () => {
+  const { t } = useI18n();
+  const app = useApp();
+  const appState = useUIAppState();
+
+  return (
+    <DropdownMenuItemCheckbox
+      checked={appState.activeTool.locked}
+      shortcut={getShortcutFromShortcutName("toolLock")}
+      onSelect={(event) => {
+        app.toggleLock();
+        event.preventDefault();
+      }}
+    >
+      {t("labels.preferences_toolLock")}
+    </DropdownMenuItemCheckbox>
+  );
+};
+
+const PreferencesToggleSnapModeItem = () => {
+  const { t } = useI18n();
+  const actionManager = useExcalidrawActionManager();
+  const appState = useUIAppState();
+  return (
+    <DropdownMenuItemCheckbox
+      checked={appState.objectsSnapModeEnabled}
+      shortcut={getShortcutFromShortcutName("objectsSnapMode")}
+      onSelect={(event) => {
+        actionManager.executeAction(actionToggleObjectsSnapMode);
+        event.preventDefault();
+      }}
+    >
+      {t("buttons.objectsSnapMode")}
+    </DropdownMenuItemCheckbox>
+  );
+};
+
+export const PreferencesToggleGridModeItem = () => {
+  const { t } = useI18n();
+  const actionManager = useExcalidrawActionManager();
+  const appState = useUIAppState();
+
+  return (
+    <DropdownMenuItemCheckbox
+      checked={appState.gridModeEnabled}
+      shortcut={getShortcutFromShortcutName("gridMode")}
+      onSelect={(event) => {
+        actionManager.executeAction(actionToggleGridMode);
+        event.preventDefault();
+      }}
+    >
+      {t("labels.toggleGrid")}
+    </DropdownMenuItemCheckbox>
+  );
+};
+
+export const PreferencesToggleZenModeItem = () => {
+  const { t } = useI18n();
+  const actionManager = useExcalidrawActionManager();
+  const appState = useUIAppState();
+  return (
+    <DropdownMenuItemCheckbox
+      checked={appState.zenModeEnabled}
+      shortcut={getShortcutFromShortcutName("zenMode")}
+      onSelect={(event) => {
+        actionManager.executeAction(actionToggleZenMode);
+        event.preventDefault();
+      }}
+    >
+      {t("buttons.zenMode")}
+    </DropdownMenuItemCheckbox>
+  );
+};
+
+const PreferencesToggleViewModeItem = () => {
+  const { t } = useI18n();
+  const actionManager = useExcalidrawActionManager();
+  const appState = useUIAppState();
+  return (
+    <DropdownMenuItemCheckbox
+      checked={appState.viewModeEnabled}
+      shortcut={getShortcutFromShortcutName("viewMode")}
+      onSelect={(event) => {
+        actionManager.executeAction(actionToggleViewMode);
+        event.preventDefault();
+      }}
+    >
+      {t("labels.viewMode")}
+    </DropdownMenuItemCheckbox>
+  );
+};
+
+const PreferencesToggleElementPropertiesItem = () => {
+  const { t } = useI18n();
+  const actionManager = useExcalidrawActionManager();
+  const appState = useUIAppState();
+  return (
+    <DropdownMenuItemCheckbox
+      checked={appState.stats.open}
+      shortcut={getShortcutFromShortcutName("stats")}
+      onSelect={(event) => {
+        actionManager.executeAction(actionToggleStats);
+        event.preventDefault();
+      }}
+    >
+      {t("stats.fullTitle")}
+    </DropdownMenuItemCheckbox>
+  );
+};
+
+export const Preferences = ({
+  children,
+  additionalItems,
+}: {
+  children?: React.ReactNode;
+  additionalItems?: React.ReactNode;
+}) => {
+  const { t } = useI18n();
+  return (
+    <DropdownMenuSub>
+      <DropdownMenuSub.Trigger icon={settingsIcon}>
+        {t("labels.preferences")}
+      </DropdownMenuSub.Trigger>
+      <DropdownMenuSub.Content className="excalidraw-main-menu-preferences-submenu">
+        {children || (
+          <>
+            <PreferencesToggleToolLockItem />
+            <PreferencesToggleSnapModeItem />
+            <PreferencesToggleGridModeItem />
+            <PreferencesToggleZenModeItem />
+            <PreferencesToggleViewModeItem />
+            <PreferencesToggleElementPropertiesItem />
+          </>
+        )}
+        {additionalItems}
+      </DropdownMenuSub.Content>
+    </DropdownMenuSub>
+  );
+};
+
+Preferences.ToggleToolLock = PreferencesToggleToolLockItem;
+Preferences.ToggleSnapMode = PreferencesToggleSnapModeItem;
+Preferences.ToggleGridMode = PreferencesToggleGridModeItem;
+Preferences.ToggleZenMode = PreferencesToggleZenModeItem;
+Preferences.ToggleViewMode = PreferencesToggleViewModeItem;
+Preferences.ToggleElementProperties = PreferencesToggleElementPropertiesItem;
+
+Preferences.displayName = "Preferences";
diff --git a/packages/excalidraw/locales/en.json b/packages/excalidraw/locales/en.json
index 765ff06cdd1d..182e59bb613b 100644
--- a/packages/excalidraw/locales/en.json
+++ b/packages/excalidraw/locales/en.json
@@ -171,7 +171,9 @@
     "linkToElement": "Link to object",
     "wrapSelectionInFrame": "Wrap selection in frame",
     "tab": "Tab",
-    "shapeSwitch": "Switch shape"
+    "shapeSwitch": "Switch shape",
+    "preferences": "Preferences",
+    "preferences_toolLock": "Tool lock"
   },
   "elementLink": {
     "title": "Link to object",
PATCH

echo "Patch applied successfully"
