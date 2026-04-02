#!/bin/bash
set -euo pipefail

# Idempotent application of the Suspense breadcrumbs fix
# PR: facebook/react#35700

cd /workspace/react

# Check if already applied (grep for distinctive new component)
if grep -q "SuspenseBreadcrumbsFlatList" packages/react-devtools-shared/src/devtools/views/SuspenseTab/SuspenseBreadcrumbs.js 2>/dev/null; then
    echo "Fix already applied, skipping"
    exit 0
fi

# Apply the gold patch
git apply - <<'PATCH'
diff --git a/packages/react-devtools-shared/src/devtools/views/SuspenseTab/SuspenseBreadcrumbs.css b/packages/react-devtools-shared/src/devtools/views/SuspenseTab/SuspenseBreadcrumbs.css
index 1e1544b477ca..3bd6a2519161 100644
--- a/packages/react-devtools-shared/src/devtools/views/SuspenseTab/SuspenseBreadcrumbs.css
+++ b/packages/react-devtools-shared/src/devtools/views/SuspenseTab/SuspenseBreadcrumbs.css
@@ -1,8 +1,13 @@
+.SuspenseBreadcrumbsContainer {
+  flex: 1;
+  display: flex;
+}
+
 .SuspenseBreadcrumbsList {
   margin: 0;
   padding: 0;
   list-style: none;
-  display: flex;
+  display: inline-flex;
   flex-direction: row;
   flex-wrap: nowrap;
 }
@@ -34,3 +39,59 @@
 .SuspenseBreadcrumbsButton:focus-visible {
   background: var(--color-button-background-focus);
 }
+
+.SuspenseBreadcrumbsMenuButton {
+  border-radius: 0.25rem;
+  display: inline-flex;
+  align-items: center;
+  padding: 0;
+  flex: 0 0 auto;
+  border: none;
+  background: var(--color-button-background);
+  color: var(--color-button);
+}
+
+.SuspenseBreadcrumbsMenuButtonContent {
+  display: inline-flex;
+  align-items: center;
+  border-radius: 0.25rem;
+  padding: 0.25rem;
+}
+
+.SuspenseBreadcrumbsMenuButton:hover {
+  color: var(--color-button-hover);
+}
+.SuspenseBreadcrumbsMenuButton[aria-expanded="true"],
+.SuspenseBreadcrumbsMenuButton[aria-expanded="true"]:active {
+  color: var(--color-button-active);
+  outline: none;
+}
+
+.SuspenseBreadcrumbsMenuButton:focus,
+.SuspenseBreadcrumbsMenuButtonContent:focus {
+  outline: none;
+}
+.SuspenseBreadcrumbsMenuButton:focus > .SuspenseBreadcrumbsMenuButtonContent {
+  background: var(--color-button-background-focus);
+}
+
+.SuspenseBreadcrumbsModal[data-reach-menu-list] {
+  display: inline-flex;
+  flex-direction: column;
+  background-color: var(--color-background);
+  color: var(--color-button);
+  padding: 0.25rem 0;
+  padding-right: 0;
+  border: 1px solid var(--color-border);
+  border-radius: 0.25rem;
+  max-height: 10rem;
+  overflow: auto;
+
+  /* Make sure this is above the DevTools, which are above the Overlay */
+  z-index: 10000002;
+  position: relative;
+
+  /* Reach UI tries to set its own :( */
+  font-family: var(--font-family-monospace);
+  font-size: var(--font-size-monospace-normal);
+}
diff --git a/packages/react-devtools-shared/src/devtools/views/SuspenseTab/SuspenseBreadcrumbs.js b/packages/react-devtools-shared/src/devtools/views/SuspenseTab/SuspenseBreadcrumbs.js
index 2ad235d57778..53a10ed0dc22 100644
--- a/packages/react-devtools-shared/src/devtools/views/SuspenseTab/SuspenseBreadcrumbs.js
+++ b/packages/react-devtools-shared/src/devtools/views/SuspenseTab/SuspenseBreadcrumbs.js
@@ -11,37 +11,47 @@ import type {SuspenseNode} from 'react-devtools-shared/src/frontend/types';
 import typeof {SyntheticMouseEvent} from 'react-dom-bindings/src/events/SyntheticEvent';

 import * as React from 'react';
-import {useContext} from 'react';
+import {useContext, useLayoutEffect, useRef, useState} from 'react';
+import Button from '../Button';
+import ButtonIcon from '../ButtonIcon';
+import Tooltip from '../Components/reach-ui/tooltip';
+import {
+  Menu,
+  MenuList,
+  MenuButton,
+  MenuItem,
+} from '../Components/reach-ui/menu-button';
 import {
   TreeDispatcherContext,
   TreeStateContext,
 } from '../Components/TreeContext';
 import {StoreContext} from '../context';
-import {useHighlightHostInstance} from '../hooks';
+import {useHighlightHostInstance, useIsOverflowing} from '../hooks';
 import styles from './SuspenseBreadcrumbs.css';
 import {
   SuspenseTreeStateContext,
   SuspenseTreeDispatcherContext,
 } from './SuspenseTreeContext';

-export default function SuspenseBreadcrumbs(): React$Node {
+type SuspenseBreadcrumbsFlatListProps = {
+  onItemClick: (id: SuspenseNode['id'], event: SyntheticMouseEvent) => void,
+  onItemPointerEnter: (
+    id: SuspenseNode['id'],
+    scrollIntoView?: boolean,
+  ) => void,
+  onItemPointerLeave: (event: SyntheticMouseEvent) => void,
+};
+
+function SuspenseBreadcrumbsFlatList({
+  onItemClick,
+  onItemPointerEnter,
+  onItemPointerLeave,
+}: SuspenseBreadcrumbsFlatListProps): React$Node {
   const store = useContext(StoreContext);
   const {activityID} = useContext(TreeStateContext);
-  const treeDispatch = useContext(TreeDispatcherContext);
-  const suspenseTreeDispatch = useContext(SuspenseTreeDispatcherContext);
   const {selectedSuspenseID, lineage, roots} = useContext(
     SuspenseTreeStateContext,
   );
-
-  const {highlightHostInstance, clearHighlightHostInstance} =
-    useHighlightHostInstance();
-
-  function handleClick(id: SuspenseNode['id'], event: SyntheticMouseEvent) {
-    event.preventDefault();
-    treeDispatch({type: 'SELECT_ELEMENT_BY_ID', payload: id});
-    suspenseTreeDispatch({type: 'SELECT_SUSPENSE_BY_ID', payload: id});
-  }
-
   return (
     <ol className={styles.SuspenseBreadcrumbsList}>
       {lineage === null ? null : lineage.length === 0 ? (
@@ -55,7 +65,7 @@ export default function SuspenseBreadcrumbs(): React$Node {
             aria-current="true">
             <button
               className={styles.SuspenseBreadcrumbsButton}
-              onClick={handleClick.bind(
+              onClick={onItemClick.bind(
                 null,
                 activityID === null ? roots[0] : activityID,
               )}
@@ -73,11 +83,11 @@ export default function SuspenseBreadcrumbs(): React$Node {
               key={id}
               className={styles.SuspenseBreadcrumbsListItem}
               aria-current={selectedSuspenseID === id}
-              onPointerEnter={highlightHostInstance.bind(null, id, false)}
-              onPointerLeave={clearHighlightHostInstance}>
+              onPointerEnter={onItemPointerEnter.bind(null, id, false)}
+              onPointerLeave={onItemPointerLeave}>
               <button
                 className={styles.SuspenseBreadcrumbsButton}
-                onClick={handleClick.bind(null, id)}
+                onClick={onItemClick.bind(null, id)}
                 type="button">
                 {node === null ? 'Unknown' : node.name || 'Unknown'}
               </button>
@@ -88,3 +98,225 @@ export default function SuspenseBreadcrumbs(): React$Node {
     </ol>
   );
 }
+
+type SuspenseBreadcrumbsMenuProps = {
+  onItemClick: (id: SuspenseNode['id'], event: SyntheticMouseEvent) => void,
+  onItemPointerEnter: (
+    id: SuspenseNode['id'],
+    scrollIntoView?: boolean,
+  ) => void,
+  onItemPointerLeave: (event: SyntheticMouseEvent) => void,
+};
+
+function SuspenseBreadcrumbsMenu({
+  onItemClick,
+  onItemPointerEnter,
+  onItemPointerLeave,
+}: SuspenseBreadcrumbsMenuProps): React$Node {
+  const store = useContext(StoreContext);
+  const {activityID} = useContext(TreeStateContext);
+  const {selectedSuspenseID, lineage, roots} = useContext(
+    SuspenseTreeStateContext,
+  );
+  const selectedSuspenseNode =
+    selectedSuspenseID !== null
+      ? store.getSuspenseByID(selectedSuspenseID)
+      : null;
+
+  return (
+    <>
+      {lineage === null ? null : lineage.length === 0 ? (
+        // We selected the root. This means that we're currently viewing the Transition
+        // that rendered the whole screen. In laymans terms this is really "Initial Paint" .
+        // When we're looking at a subtree selection, then the equivalent is a
+        // "Transition" since in that case it's really about a Transition within the page.
+        roots.length > 0 ? (
+          <button
+            className={styles.SuspenseBreadcrumbsButton}
+            onClick={onItemClick.bind(
+              null,
+              activityID === null ? roots[0] : activityID,
+            )}
+            type="button">
+            {activityID === null ? 'Initial Paint' : 'Transition'}
+          </button>
+        ) : null
+      ) : (
+        <>
+          <SuspenseBreadcrumbsDropdown
+            lineage={lineage}
+            selectElement={onItemClick}
+          />
+          <SuspenseBreadcrumbsToParentButton
+            lineage={lineage}
+            selectedSuspenseID={selectedSuspenseID}
+            selectElement={onItemClick}
+          />
+          {selectedSuspenseNode != null && (
+            <button
+              className={styles.SuspenseBreadcrumbsButton}
+              onClick={onItemClick.bind(null, selectedSuspenseNode.id)}
+              onPointerEnter={onItemPointerEnter.bind(
+                null,
+                selectedSuspenseNode.id,
+                false,
+              )}
+              onPointerLeave={onItemPointerLeave}
+              type="button">
+              {selectedSuspenseNode === null
+                ? 'Unknown'
+                : selectedSuspenseNode.name || 'Unknown'}
+            </button>
+          )}
+        </>
+      )}
+    </>
+  );
+}
+
+type SuspenseBreadcrumbsDropdownProps = {
+  lineage: $ReadOnlyArray<SuspenseNode['id']>,
+  selectedIndex: number,
+  selectElement: (id: SuspenseNode['id']) => void,
+};
+function SuspenseBreadcrumbsDropdown({
+  lineage,
+  selectElement,
+}: SuspenseBreadcrumbsDropdownProps) {
+  const store = useContext(StoreContext);
+
+  const menuItems = [];
+  for (let index = lineage.length - 1; index >= 0; index--) {
+    const suspenseNodeID = lineage[index];
+    const node = store.getSuspenseByID(suspenseNodeID);
+    menuItems.push(
+      <MenuItem
+        key={suspenseNodeID}
+        className={`${styles.Component}`}
+        onSelect={selectElement.bind(null, suspenseNodeID)}>
+        {node === null ? 'Unknown' : node.name || 'Unknown'}
+      </MenuItem>,
+    );
+  }
+
+  return (
+    <Menu>
+      <MenuButton className={styles.SuspenseBreadcrumbsMenuButton}>
+        <Tooltip label="Open elements dropdown">
+          <span
+            className={styles.SuspenseBreadcrumbsMenuButtonContent}
+            tabIndex={-1}>
+            <ButtonIcon type="more" />
+          </span>
+        </Tooltip>
+      </MenuButton>
+      <MenuList className={styles.SuspenseBreadcrumbsModal}>
+        {menuItems}
+      </MenuList>
+    </Menu>
+  );
+}
+
+type SuspenseBreadcrumbsToParentButtonProps = {
+  lineage: $ReadOnlyArray<SuspenseNode['id']>,
+  selectedSuspenseID: SuspenseNode['id'] | null,
+  selectElement: (id: SuspenseNode['id'], event: SyntheticMouseEvent) => void,
+};
+function SuspenseBreadcrumbsToParentButton({
+  lineage,
+  selectedSuspenseID,
+  selectElement,
+}: SuspenseBreadcrumbsToParentButtonProps) {
+  const store = useContext(StoreContext);
+  const selectedIndex =
+    selectedSuspenseID === null
+      ? lineage.length - 1
+      : lineage.indexOf(selectedSuspenseID);
+
+  if (selectedIndex <= 0) {
+    return null;
+  }
+
+  const parentID = lineage[selectedIndex - 1];
+  const parent = store.getSuspenseByID(parentID);
+
+  return (
+    <Button
+      className={parent !== null ? undefined : styles.NotInStore}
+      onClick={parent !== null ? selectElement.bind(null, parentID) : null}
+      title={`Up to ${parent === null ? 'Unknown' : parent.name || 'Unknown'}`}>
+      <ButtonIcon type="previous" />
+    </Button>
+  );
+}
+
+export default function SuspenseBreadcrumbs(): React$Node {
+  const treeDispatch = useContext(TreeDispatcherContext);
+  const suspenseTreeDispatch = useContext(SuspenseTreeDispatcherContext);
+
+  const {highlightHostInstance, clearHighlightHostInstance} =
+    useHighlightHostInstance();
+
+  function handleClick(id: SuspenseNode['id'], event?: SyntheticMouseEvent) {
+    if (event !== undefined) {
+      // E.g. 3rd party component libraries might omit the event and already prevent default
+      // like Reach's MenuItem does.
+      event.preventDefault();
+    }
+    treeDispatch({type: 'SELECT_ELEMENT_BY_ID', payload: id});
+    suspenseTreeDispatch({type: 'SELECT_SUSPENSE_BY_ID', payload: id});
+  }
+
+  const [elementsTotalWidth, setElementsTotalWidth] = useState(0);
+  const containerRef = useRef<HTMLDivElement | null>(null);
+  const isOverflowing = useIsOverflowing(containerRef, elementsTotalWidth);
+
+  useLayoutEffect(() => {
+    const container = containerRef.current;
+
+    if (
+      container === null ||
+      // We want to measure the size of the flat list only when it's being used.
+      isOverflowing
+    ) {
+      return;
+    }
+
+    const ResizeObserver = container.ownerDocument.defaultView.ResizeObserver;
+    const observer = new ResizeObserver(() => {
+      let totalWidth = 0;
+      for (let i = 0; i < container.children.length; i++) {
+        const element = container.children[i];
+        const computedStyle = getComputedStyle(element);
+
+        totalWidth +=
+          element.offsetWidth +
+          parseInt(computedStyle.marginLeft, 10) +
+          parseInt(computedStyle.marginRight, 10);
+      }
+      setElementsTotalWidth(totalWidth);
+    });
+
+    observer.observe(container);
+
+    return observer.disconnect.bind(observer);
+  }, [containerRef, isOverflowing]);
+
+  return (
+    <div className={styles.SuspenseBreadcrumbsContainer} ref={containerRef}>
+      {isOverflowing ? (
+        <SuspenseBreadcrumbsMenu
+          onItemClick={handleClick}
+          onItemPointerEnter={highlightHostInstance}
+          onItemPointerLeave={clearHighlightHostInstance}
+        />
+      ) : (
+        <SuspenseBreadcrumbsFlatList
+          onItemClick={handleClick}
+          onItemPointerEnter={highlightHostInstance}
+          onItemPointerLeave={clearHighlightHostInstance}
+        />
+      )}
+    </div>
+  );
+}
diff --git a/packages/react-devtools-shared/src/devtools/views/SuspenseTab/SuspenseTab.css b/packages/react-devtools-shared/src/devtools/views/SuspenseTab/SuspenseTab.css
index a7915d0d9101..92935bd4a6b4 100644
--- a/packages/react-devtools-shared/src/devtools/views/SuspenseTab/SuspenseTab.css
+++ b/packages/react-devtools-shared/src/devtools/views/SuspenseTab/SuspenseTab.css
@@ -121,15 +121,6 @@
   border-bottom: 1px solid var(--color-border);
 }

-.SuspenseBreadcrumbs {
-  flex: 1;
-  /**
-   * TODO: Switch to single item view on overflow like OwnerStack does.
-   * OwnerStack has more constraints that make it easier so it won't be a 1:1 port.
-   */
-  overflow-x: auto;
-}
-
 .SuspenseTreeViewFooter {
   flex: 0 0 42px;
   display: flex;
diff --git a/packages/react-devtools-shared/src/devtools/views/SuspenseTab/SuspenseTab.js b/packages/react-devtools-shared/src/devtools/views/SuspenseTab/SuspenseTab.js
index 0b195a99c4db..3fdd9fe935a3 100644
--- a/packages/react-devtools-shared/src/devtools/views/SuspenseTab/SuspenseTab.js
+++ b/packages/react-devtools-shared/src/devtools/views/SuspenseTab/SuspenseTab.js
@@ -501,9 +501,7 @@ function SuspenseTab(_: {}) {
                   <div className={styles.VRule} />
                 </Fragment>
               )}
-              <div className={styles.SuspenseBreadcrumbs}>
-                <SuspenseBreadcrumbs />
-              </div>
+              <SuspenseBreadcrumbs />
               <div className={styles.VRule} />
               <ToggleUniqueSuspenders />
               {!hideSettings && <SettingsModalContextToggle />}
PATCH

echo "Fix applied successfully"
