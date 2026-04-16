#!/bin/bash
set -e

cd /workspace/excalidraw

# Check if already applied (idempotency check)
if grep -q "MQ_MAX_TABLET = 1180" packages/common/src/editorInterface.ts; then
    echo "Patch already applied, skipping"
    exit 0
fi

# Apply the gold patch
patch -p1 << 'PATCH'
diff --git a/packages/common/src/editorInterface.ts b/packages/common/src/editorInterface.ts
index 36b55d91829a..d18b7a7d084e 100644
--- a/packages/common/src/editorInterface.ts
+++ b/packages/common/src/editorInterface.ts
@@ -16,7 +16,6 @@ export type EditorInterface = Readonly<{
 const DESKTOP_UI_MODE_STORAGE_KEY = "excalidraw.desktopUIMode";

 // breakpoints
-// mobile: up to 699px
 export const MQ_MAX_MOBILE = 599;

 export const MQ_MAX_WIDTH_LANDSCAPE = 1000;
@@ -24,9 +23,9 @@ export const MQ_MAX_HEIGHT_LANDSCAPE = 500;

 // tablets
 export const MQ_MIN_TABLET = MQ_MAX_MOBILE + 1; // lower bound (excludes phones)
-export const MQ_MAX_TABLET = 1400; // upper bound (excludes laptops/desktops)
+export const MQ_MAX_TABLET = 1180; // ipad air

-// desktop/laptop
+// desktop/laptop (NOTE: not used for form factor detection)
 export const MQ_MIN_WIDTH_DESKTOP = 1440;

 // sidebar
diff --git a/packages/excalidraw/components/App.tsx b/packages/excalidraw/components/App.tsx
index 5fec6ff4abb5..c37d992e0386 100644
--- a/packages/excalidraw/components/App.tsx
+++ b/packages/excalidraw/components/App.tsx
@@ -2780,7 +2780,7 @@ class App extends React.Component<AppProps, AppState> {

   private getFormFactor = (editorWidth: number, editorHeight: number) => {
     return (
-      this.props.UIOptions.formFactor ??
+      this.props.UIOptions.getFormFactor?.(editorWidth, editorHeight) ??
       getFormFactor(editorWidth, editorHeight)
     );
   };
@@ -2804,10 +2804,7 @@ class App extends React.Component<AppProps, AppState> {
         ? this.props.UIOptions.dockedSidebarBreakpoint
         : MQ_RIGHT_SIDEBAR_MIN_WIDTH;
     const nextEditorInterface = updateObject(this.editorInterface, {
-      desktopUIMode:
-        this.props.UIOptions.desktopUIMode ??
-        storedDesktopUIMode ??
-        this.editorInterface.desktopUIMode,
+      desktopUIMode: storedDesktopUIMode ?? this.editorInterface.desktopUIMode,
       formFactor: this.getFormFactor(editorWidth, editorHeight),
       userAgent: userAgentDescriptor,
       canFitSidebar: editorWidth > sidebarBreakpoint,
diff --git a/packages/excalidraw/index.tsx b/packages/excalidraw/index.tsx
index 44b83a5dca6f..db0fe94cd8a7 100644
--- a/packages/excalidraw/index.tsx
+++ b/packages/excalidraw/index.tsx
@@ -187,6 +187,9 @@ const areEqual = (prevProps: ExcalidrawProps, nextProps: ExcalidrawProps) => {
   }

   const isUIOptionsSame = prevUIOptionsKeys.every((key) => {
+    if (key === "getFormFactor") {
+      return true;
+    }
     if (key === "canvasActions") {
       const canvasOptionKeys = Object.keys(
         prevUIOptions.canvasActions!,
diff --git a/packages/excalidraw/types.ts b/packages/excalidraw/types.ts
index ad7c46a6db9a..2f464d868348 100644
--- a/packages/excalidraw/types.ts
+++ b/packages/excalidraw/types.ts
@@ -682,8 +682,10 @@ export type UIOptions = Partial<{
    * Optionally control the editor form factor and desktop UI mode from the host app.
    * If not provided, we will take care of it internally.
    */
-  formFactor?: EditorInterface["formFactor"];
-  desktopUIMode?: EditorInterface["desktopUIMode"];
+  getFormFactor?: (
+    editorWidth: number,
+    editorHeight: number,
+  ) => EditorInterface["formFactor"];
   /** @deprecated does nothing. Will be removed in 0.15 */
   welcomeScreen?: boolean;
 }>;
PATCH

echo "Patch applied successfully"
