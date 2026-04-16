#!/bin/bash
set -e

cd /workspace/excalidraw

# Apply the gold patch for PR #10682: fix dropdownMenu item badge position
patch -p1 <<'PATCH'
diff --git a/packages/excalidraw/components/Actions.tsx b/packages/excalidraw/components/Actions.tsx
index 9967ee2c995e..18791f8f9ba2 100644
--- a/packages/excalidraw/components/Actions.tsx
+++ b/packages/excalidraw/components/Actions.tsx
@@ -1263,9 +1263,9 @@ export const ShapesSwitcher = ({
               onSelect={() => app.onMagicframeToolSelect()}
               icon={MagicIcon}
               data-testid="toolbar-magicframe"
+              badge={<DropdownMenu.Item.Badge>AI</DropdownMenu.Item.Badge>}
             >
               {t("toolBar.magicframe")}
-              <DropdownMenu.Item.Badge>AI</DropdownMenu.Item.Badge>
             </DropdownMenu.Item>
           )}
         </DropdownMenu.Content>
diff --git a/packages/excalidraw/components/FontPicker/FontPickerList.tsx b/packages/excalidraw/components/FontPicker/FontPickerList.tsx
index a6202f022724..79dca68ce0cb 100644
--- a/packages/excalidraw/components/FontPicker/FontPickerList.tsx
+++ b/packages/excalidraw/components/FontPicker/FontPickerList.tsx
@@ -290,13 +290,15 @@ export const FontPickerList = React.memo(
             onHover(font.value);
           }
         }}
+        badge={
+          font.badge && (
+            <DropDownMenuItemBadge type={font.badge.type}>
+              {font.badge.placeholder}
+            </DropDownMenuItemBadge>
+          )
+        }
       >
         {font.text}
-        {font.badge && (
-          <DropDownMenuItemBadge type={font.badge.type}>
-            {font.badge.placeholder}
-          </DropDownMenuItemBadge>
-        )}
       </DropdownMenuItem>
     );

diff --git a/packages/excalidraw/components/TTDDialog/TTDDialogTrigger.tsx b/packages/excalidraw/components/TTDDialog/TTDDialogTrigger.tsx
index 0d5c62f331d4..9886d59c969e 100644
--- a/packages/excalidraw/components/TTDDialog/TTDDialogTrigger.tsx
+++ b/packages/excalidraw/components/TTDDialog/TTDDialogTrigger.tsx
@@ -26,9 +26,9 @@ export const TTDDialogTrigger = ({
           setAppState({ openDialog: { name: "ttd", tab: "text-to-diagram" } });
         }}
         icon={icon ?? brainIcon}
+        badge={<DropdownMenu.Item.Badge>AI</DropdownMenu.Item.Badge>}
       >
         {children ?? t("labels.textToDiagram")}
-        <DropdownMenu.Item.Badge>AI</DropdownMenu.Item.Badge>
       </DropdownMenu.Item>
     </TTDDialogTriggerTunnel.In>
   );
diff --git a/packages/excalidraw/components/dropdownMenu/DropdownMenuItem.tsx b/packages/excalidraw/components/dropdownMenu/DropdownMenuItem.tsx
index 59c5dd2f84cd..0f227a0bbd92 100644
--- a/packages/excalidraw/components/dropdownMenu/DropdownMenuItem.tsx
+++ b/packages/excalidraw/components/dropdownMenu/DropdownMenuItem.tsx
@@ -26,6 +26,7 @@ const DropdownMenuItem = ({
   textStyle,
   onSelect,
   onClick,
+  badge,
   ...rest
 }: {
   icon?: JSX.Element;
@@ -38,6 +39,7 @@ const DropdownMenuItem = ({
   selected?: boolean;
   textStyle?: React.CSSProperties;
   className?: string;
+  badge?: React.ReactNode;
 } & Omit<React.ButtonHTMLAttributes<HTMLButtonElement>, "onSelect">) => {
   const handleClick = useHandleDropdownMenuItemClick(onClick, onSelect);
   const ref = useRef<HTMLButtonElement>(null);
@@ -62,7 +64,12 @@ const DropdownMenuItem = ({
       className={getDropdownMenuItemClassName(className, selected, hovered)}
       title={rest.title ?? rest["aria-label"]}
     >
-      <MenuItemContent textStyle={textStyle} icon={icon} shortcut={shortcut}>
+      <MenuItemContent
+        textStyle={textStyle}
+        icon={icon}
+        shortcut={shortcut}
+        badge={badge}
+      >
         {children}
       </MenuItemContent>
     </button>
diff --git a/packages/excalidraw/components/dropdownMenu/DropdownMenuItemContent.tsx b/packages/excalidraw/components/dropdownMenu/DropdownMenuItemContent.tsx
index d4078a8da476..c57dad888546 100644
--- a/packages/excalidraw/components/dropdownMenu/DropdownMenuItemContent.tsx
+++ b/packages/excalidraw/components/dropdownMenu/DropdownMenuItemContent.tsx
@@ -9,11 +9,13 @@ const MenuItemContent = ({
   icon,
   shortcut,
   children,
+  badge,
 }: {
   icon?: JSX.Element;
   shortcut?: string;
   textStyle?: React.CSSProperties;
   children: React.ReactNode;
+  badge?: React.ReactNode;
 }) => {
   const editorInterface = useEditorInterface();
   return (
@@ -22,6 +24,7 @@ const MenuItemContent = ({
       <div style={textStyle} className="dropdown-menu-item__text">
         <Ellipsify>{children}</Ellipsify>
       </div>
+      {badge && <div className="dropdown-menu-item__badge">{badge}</div>}
       {shortcut && editorInterface.formFactor !== "phone" && (
         <div className="dropdown-menu-item__shortcut">{shortcut}</div>
       )}
PATCH

echo "Patch applied successfully"
