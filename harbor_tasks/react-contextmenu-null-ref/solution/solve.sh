#!/bin/bash
set -euo pipefail

# This script applies the gold patch for the ContextMenu null ref crash fix

if grep -q "hideMenu" /workspace/react/packages/react-devtools-shared/src/devtools/ContextMenu/ContextMenu.js; then
    echo "Fix already applied."
    exit 0
fi

cd /workspace/react

git apply - <<'PATCH'
diff --git a/packages/react-devtools-shared/src/devtools/ContextMenu/ContextMenu.js b/packages/react-devtools-shared/src/devtools/ContextMenu/ContextMenu.js
index a96634fbe46a..ded5bbb22e6c 100644
--- a/packages/react-devtools-shared/src/devtools/ContextMenu/ContextMenu.js
+++ b/packages/react-devtools-shared/src/devtools/ContextMenu/ContextMenu.js
@@ -8,7 +8,7 @@
  */

 import * as React from 'react';
-import {useLayoutEffect, createRef} from 'react';
+import {useLayoutEffect} from 'react';
 import {createPortal} from 'react-dom';

 import ContextMenuItem from './ContextMenuItem';
@@ -16,7 +16,6 @@ import ContextMenuItem from './ContextMenuItem';
 import type {
   ContextMenuItem as ContextMenuItemType,
   ContextMenuPosition,
-  ContextMenuRef,
 } from './types';

 import styles from './ContextMenu.css';
@@ -49,7 +48,6 @@ type Props = {
   items: ContextMenuItemType[],
   position: ContextMenuPosition,
   hide: () => void,
-  ref?: ContextMenuRef,
 };

 export default function ContextMenu({
@@ -57,7 +55,6 @@ export default function ContextMenu({
   position,
   items,
   hide,
-  ref = createRef(),
 }: Props): React.Node {
   // This works on the assumption that ContextMenu component is only rendered when it should be shown
   const anchor = anchorElementRef.current;
@@ -73,8 +70,21 @@ export default function ContextMenu({
     '[data-react-devtools-portal-root]',
   );

+  const hideMenu = portalContainer == null || items.length === 0;
+  const menuRef = React.useRef<HTMLDivElement | null>(null);
+
   useLayoutEffect(() => {
-    const menu = ((ref.current: any): HTMLElement);
+    // Match the early-return condition below.
+    if (hideMenu) {
+      return;
+    }
+    const maybeMenu = menuRef.current;
+    if (maybeMenu === null) {
+      throw new Error(
+        "Can't access context menu element. This is a bug in React DevTools.",
+      );
+    }
+    const menu = (maybeMenu: HTMLDivElement);

     function hideUnlessContains(event: Event) {
       if (!menu.contains(((event.target: any): Node))) {
@@ -98,14 +108,14 @@ export default function ContextMenu({

       ownerWindow.removeEventListener('resize', hide);
     };
-  }, []);
+  }, [hideMenu]);

-  if (portalContainer == null || items.length === 0) {
+  if (hideMenu) {
     return null;
   }

   return createPortal(
-    <div className={styles.ContextMenu} ref={ref}>
+    <div className={styles.ContextMenu} ref={menuRef}>
       {items.map(({onClick, content}, index) => (
         <ContextMenuItem key={index} onClick={onClick} hide={hide}>
           {content}
diff --git a/packages/react-devtools-shared/src/devtools/ContextMenu/ContextMenuContainer.js b/packages/react-devtools-shared/src/devtools/ContextMenu/ContextMenuContainer.js
index 14e1985b2022..22b70dd447c3 100644
--- a/packages/react-devtools-shared/src/devtools/ContextMenu/ContextMenuContainer.js
+++ b/packages/react-devtools-shared/src/devtools/ContextMenu/ContextMenuContainer.js
@@ -53,7 +53,6 @@ export default function ContextMenuContainer({
       position={position}
       hide={hide}
       items={items}
-      ref={ref}
     />
   );
 }
PATCH

echo "Fix applied successfully."
