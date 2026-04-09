#!/bin/bash
set -e

cd /workspace/excalidraw

# Check if already applied
if grep -q "DARK_THEME_FILTER" packages/common/src/constants.ts; then
    echo "Patch already applied, skipping..."
    exit 0
fi

# Apply the gold patch
patch -p1 <<'PATCH'
diff --git a/packages/common/src/constants.ts b/packages/common/src/constants.ts
index 80d89b8cb6da..23d5f426e6a0 100644
--- a/packages/common/src/constants.ts
+++ b/packages/common/src/constants.ts
@@ -190,6 +190,8 @@ export const THEME = {
   DARK: "dark",
 } as const;

+export const DARK_THEME_FILTER = "invert(93%) hue-rotate(180deg)";
+
 export const FRAME_STYLE = {
   strokeColor: "#bbb" as ExcalidrawElement["strokeColor"],
   strokeWidth: 2 as ExcalidrawElement["strokeWidth"],
diff --git a/packages/element/src/renderElement.ts b/packages/element/src/renderElement.ts
index 2459bd45cbb6..1c5f941ebfdf 100644
--- a/packages/element/src/renderElement.ts
+++ b/packages/element/src/renderElement.ts
@@ -14,6 +14,7 @@ import {
   DEFAULT_REDUCED_GLOBAL_ALPHA,
   ELEMENT_READY_TO_ERASE_OPACITY,
   FRAME_STYLE,
+  DARK_THEME_FILTER,
   MIME_TYPES,
   THEME,
   distance,
@@ -433,9 +434,22 @@ const drawElementOnCanvas = (
       break;
     }
     case "image": {
+      context.save();
+      const cacheEntry =
+        element.fileId !== null
+          ? renderConfig.imageCache.get(element.fileId)
+          : null;
       const img = isInitializedImageElement(element)
-        ? renderConfig.imageCache.get(element.fileId)?.image
+        ? cacheEntry?.image
         : undefined;
+
+      const shouldInvertImage =
+        renderConfig.theme === THEME.DARK &&
+        cacheEntry?.mimeType === MIME_TYPES.svg;
+
+      if (shouldInvertImage) {
+        context.filter = DARK_THEME_FILTER;
+      }
       if (img != null && !(img instanceof Promise)) {
         if (element.roundness && context.roundRect) {
           context.beginPath();
@@ -472,6 +486,7 @@ const drawElementOnCanvas = (
       } else {
         drawImagePlaceholder(element, context);
       }
+      context.restore();
       break;
     }
     default: {
diff --git a/packages/excalidraw/renderer/staticSvgScene.ts b/packages/excalidraw/renderer/staticSvgScene.ts
index c6ff0eee1522..de9be13c83eb 100644
--- a/packages/excalidraw/renderer/staticSvgScene.ts
+++ b/packages/excalidraw/renderer/staticSvgScene.ts
@@ -3,11 +3,13 @@ import {
   MAX_DECIMALS_FOR_SVG_EXPORT,
   SVG_NS,
   THEME,
+  DARK_THEME_FILTER,
   getFontFamilyString,
   isRTL,
   isTestEnv,
   getVerticalOffset,
   applyDarkModeFilter,
+  MIME_TYPES,
 } from "@excalidraw/common";
 import { normalizeLink, toValidURL } from "@excalidraw/common";
 import { hashString } from "@excalidraw/element";
@@ -520,6 +522,13 @@ const renderElementToSvg = (

         const g = svgRoot.ownerDocument.createElementNS(SVG_NS, "g");

+        if (
+          renderConfig.theme === THEME.DARK &&
+          fileData.mimeType === MIME_TYPES.svg
+        ) {
+          g.setAttribute("filter", DARK_THEME_FILTER);
+        }
+
         if (element.crop) {
           const mask = svgRoot.ownerDocument.createElementNS(SVG_NS, "mask");
           mask.setAttribute("id", `mask-image-crop-${element.id}`);
PATCH

echo "Patch applied successfully!"
