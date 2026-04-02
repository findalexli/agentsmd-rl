#!/usr/bin/env bash
set -euo pipefail

cd /workspace/opencode

# Idempotency: check if already fixed (file tree defaults to closed)
if grep -q 'DEFAULT_FILE_TREE_WIDTH' packages/app/src/context/layout.tsx 2>/dev/null || \
   grep -q 'opened: false' packages/app/src/context/layout.tsx 2>/dev/null | grep -q 'fileTree' 2>/dev/null; then
    # More precise check: is fileTree.opened already false in the initial store?
    if node -e "
      const fs = require('fs');
      const src = fs.readFileSync('packages/app/src/context/layout.tsx', 'utf8');
      const match = src.match(/fileTree:\s*\{[^}]*opened:\s*false/);
      process.exit(match ? 0 : 1);
    " 2>/dev/null; then
        echo "Already applied."
        exit 0
    fi
fi

git apply - <<'PATCH'
diff --git a/packages/app/src/context/layout.tsx b/packages/app/src/context/layout.tsx
index 78928118d72..640d5e02eb3 100644
--- a/packages/app/src/context/layout.tsx
+++ b/packages/app/src/context/layout.tsx
@@ -13,7 +13,8 @@ import { createScrollPersistence, type SessionScroll } from "./layout-scroll"
 import { createPathHelpers } from "./file/path"

 const AVATAR_COLOR_KEYS = ["pink", "mint", "orange", "purple", "cyan", "lime"] as const
-const DEFAULT_PANEL_WIDTH = 344
+const DEFAULT_SIDEBAR_WIDTH = 344
+const DEFAULT_FILE_TREE_WIDTH = 200
 const DEFAULT_SESSION_WIDTH = 600
 const DEFAULT_TERMINAL_HEIGHT = 280
 export type AvatarColorKey = (typeof AVATAR_COLOR_KEYS)[number]
@@ -161,11 +162,11 @@ export const { use: useLayout, provider: LayoutProvider } = createSimpleContext(
         if (!isRecord(fileTree)) return fileTree
         if (fileTree.tab === "changes" || fileTree.tab === "all") return fileTree

-        const width = typeof fileTree.width === "number" ? fileTree.width : DEFAULT_PANEL_WIDTH
+        const width = typeof fileTree.width === "number" ? fileTree.width : DEFAULT_FILE_TREE_WIDTH
         return {
           ...fileTree,
           opened: true,
-          width: width === 260 ? DEFAULT_PANEL_WIDTH : width,
+          width: width === 260 ? DEFAULT_FILE_TREE_WIDTH : width,
           tab: "changes",
         }
       })()
@@ -230,7 +231,7 @@ export const { use: useLayout, provider: LayoutProvider } = createSimpleContext(
       createStore({
         sidebar: {
           opened: false,
-          width: DEFAULT_PANEL_WIDTH,
+          width: DEFAULT_SIDEBAR_WIDTH,
           workspaces: {} as Record<string, boolean>,
           workspacesDefault: false,
         },
@@ -243,8 +244,8 @@ export const { use: useLayout, provider: LayoutProvider } = createSimpleContext(
           panelOpened: true,
         },
         fileTree: {
-          opened: true,
-          width: DEFAULT_PANEL_WIDTH,
+          opened: false,
+          width: DEFAULT_FILE_TREE_WIDTH,
           tab: "changes" as "changes" | "all",
         },
         session: {
@@ -628,32 +629,32 @@ export const { use: useLayout, provider: LayoutProvider } = createSimpleContext(
       },
       fileTree: {
         opened: createMemo(() => store.fileTree?.opened ?? true),
-        width: createMemo(() => store.fileTree?.width ?? DEFAULT_PANEL_WIDTH),
+        width: createMemo(() => store.fileTree?.width ?? DEFAULT_FILE_TREE_WIDTH),
         tab: createMemo(() => store.fileTree?.tab ?? "changes"),
         setTab(tab: "changes" | "all") {
           if (!store.fileTree) {
-            setStore("fileTree", { opened: true, width: DEFAULT_PANEL_WIDTH, tab })
+            setStore("fileTree", { opened: true, width: DEFAULT_FILE_TREE_WIDTH, tab })
             return
           }
           setStore("fileTree", "tab", tab)
         },
         open() {
           if (!store.fileTree) {
-            setStore("fileTree", { opened: true, width: DEFAULT_PANEL_WIDTH, tab: "changes" })
+            setStore("fileTree", { opened: true, width: DEFAULT_FILE_TREE_WIDTH, tab: "changes" })
             return
           }
           setStore("fileTree", "opened", true)
         },
         close() {
           if (!store.fileTree) {
-            setStore("fileTree", { opened: false, width: DEFAULT_PANEL_WIDTH, tab: "changes" })
+            setStore("fileTree", { opened: false, width: DEFAULT_FILE_TREE_WIDTH, tab: "changes" })
             return
           }
           setStore("fileTree", "opened", false)
         },
         toggle() {
           if (!store.fileTree) {
-            setStore("fileTree", { opened: true, width: DEFAULT_PANEL_WIDTH, tab: "changes" })
+            setStore("fileTree", { opened: true, width: DEFAULT_FILE_TREE_WIDTH, tab: "changes" })
             return
           }
           setStore("fileTree", "opened", (x) => !x)
diff --git a/packages/app/src/pages/session.tsx b/packages/app/src/pages/session.tsx
index 752b549b861..11e6375b3b6 100644
--- a/packages/app/src/pages/session.tsx
+++ b/packages/app/src/pages/session.tsx
@@ -1640,6 +1640,15 @@ export default function Page() {
     consumePendingMessage: layout.pendingMessage.consume,
   })

+  createEffect(
+    on(
+      () => params.id,
+      (id) => {
+        if (!id) requestAnimationFrame(() => inputRef?.focus())
+      },
+    ),
+  )
+
   onMount(() => {
     document.addEventListener("keydown", handleKeyDown)
   })

PATCH

echo "Patch applied successfully."
