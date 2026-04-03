#!/usr/bin/env bash
set -euo pipefail

cd /workspace/storybook

# Idempotent: skip if already applied
if grep -q "Cancel any running play function before patching" code/builders/builder-vite/src/codegen-modern-iframe-script.ts 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply --whitespace=fix - <<'PATCH'
diff --git a/.github/copilot-instructions.md b/.github/copilot-instructions.md
index 2c66e469ef73..dc9785e14913 100644
--- a/.github/copilot-instructions.md
+++ b/.github/copilot-instructions.md
@@ -65,6 +65,12 @@ yarn nx compile <package-name> -c production # Compile specific package
 yarn lint                         # Run all linting checks (~4 min)
 ```

+Fix linting on all touched files by running the following command before commiting:
+
+```bash
+yarn --cwd code lint:js:cmd <file> --fix
+```
+
 ### Type Checking

 ```bash
diff --git a/code/builders/builder-vite/src/codegen-modern-iframe-script.ts b/code/builders/builder-vite/src/codegen-modern-iframe-script.ts
index e8a615db5b59..ac7f3026d957 100644
--- a/code/builders/builder-vite/src/codegen-modern-iframe-script.ts
+++ b/code/builders/builder-vite/src/codegen-modern-iframe-script.ts
@@ -31,11 +31,9 @@ export async function generateModernIframeScriptCodeFromPreviews(options: {

     return dedent`
     if (import.meta.hot) {
-      import.meta.hot.on('vite:afterUpdate', () => {
-        window.__STORYBOOK_PREVIEW__.channel.emit('${STORY_HOT_UPDATED}');
-      });
-
       import.meta.hot.accept('${SB_VIRTUAL_FILES.VIRTUAL_STORIES_FILE}', (newModule) => {
+        // Cancel any running play function before patching in the new importFn
+        window.__STORYBOOK_PREVIEW__.channel.emit('${STORY_HOT_UPDATED}');
         // importFn has changed so we need to patch the new one in
         window.__STORYBOOK_PREVIEW__.onStoriesChanged({ importFn: newModule.importFn });
       });
diff --git a/code/builders/builder-vite/src/codegen-project-annotations.ts b/code/builders/builder-vite/src/codegen-project-annotations.ts
index 9d13c9390ec9..c878027239d0 100644
--- a/code/builders/builder-vite/src/codegen-project-annotations.ts
+++ b/code/builders/builder-vite/src/codegen-project-annotations.ts
@@ -1,4 +1,5 @@
 import { getFrameworkName, loadPreviewOrConfigFile } from 'storybook/internal/common';
+import { STORY_HOT_UPDATED } from 'storybook/internal/core-events';
 import { isCsfFactoryPreview, readConfig } from 'storybook/internal/csf-tools';
 import type { Options, PreviewAnnotation } from 'storybook/internal/types';

@@ -68,6 +69,8 @@ export function generateProjectAnnotationsCodeFromPreviews(options: {

       if (import.meta.hot) {
         import.meta.hot.accept([${JSON.stringify(previewFileURL)}], (previewAnnotationModules) => {
+          // Cancel any running play function before patching in the new getProjectAnnotations
+          window?.__STORYBOOK_PREVIEW__?.channel?.emit('${STORY_HOT_UPDATED}');
           // getProjectAnnotations has changed so we need to patch the new one in
           window?.__STORYBOOK_PREVIEW__?.onGetProjectAnnotationsChanged({
             getProjectAnnotations: () => getProjectAnnotations(previewAnnotationModules),
@@ -96,6 +99,8 @@ export function generateProjectAnnotationsCodeFromPreviews(options: {

     if (import.meta.hot) {
       import.meta.hot.accept(${JSON.stringify(previewAnnotationURLs)}, (previewAnnotationModules) => {
+        // Cancel any running play function before patching in the new getProjectAnnotations
+        window?.__STORYBOOK_PREVIEW__?.channel?.emit('${STORY_HOT_UPDATED}');
         // getProjectAnnotations has changed so we need to patch the new one in
         window?.__STORYBOOK_PREVIEW__?.onGetProjectAnnotationsChanged({
           getProjectAnnotations: () => getProjectAnnotations(previewAnnotationModules),
diff --git a/code/builders/builder-webpack5/templates/virtualModuleModernEntry.js b/code/builders/builder-webpack5/templates/virtualModuleModernEntry.js
index c470929a6520..e6ded416e206 100644
--- a/code/builders/builder-webpack5/templates/virtualModuleModernEntry.js
+++ b/code/builders/builder-webpack5/templates/virtualModuleModernEntry.js
@@ -33,18 +33,16 @@ window.__STORYBOOK_STORY_STORE__ = preview.storyStore;
 window.__STORYBOOK_ADDONS_CHANNEL__ = channel;

 if (import.meta.webpackHot) {
-  import.meta.webpackHot.addStatusHandler((status) => {
-    if (status === 'idle') {
-      preview.channel.emit(STORY_HOT_UPDATED);
-    }
-  });
-
   import.meta.webpackHot.accept('{{storiesFilename}}', () => {
+    // Cancel any running play function before patching in the new importFn
+    preview.channel.emit(STORY_HOT_UPDATED);
     // importFn has changed so we need to patch the new one in
     preview.onStoriesChanged({ importFn });
   });

   import.meta.webpackHot.accept(['{{previewAnnotations}}'], () => {
+    // Cancel any running play function before patching in the new getProjectAnnotations
+    preview.channel.emit(STORY_HOT_UPDATED);
     // getProjectAnnotations has changed so we need to patch the new one in
     preview.onGetProjectAnnotationsChanged({ getProjectAnnotations });
   });
diff --git a/code/core/src/core-server/utils/index-json.ts b/code/core/src/core-server/utils/index-json.ts
index daf33d195a62..9afd11a4646e 100644
--- a/code/core/src/core-server/utils/index-json.ts
+++ b/code/core/src/core-server/utils/index-json.ts
@@ -39,7 +39,7 @@ export function registerIndexJsonRoute({
   normalizedStories: NormalizedStoriesSpecifier[];
 }) {
   const maybeInvalidate = debounce(() => channel.emit(STORY_INDEX_INVALIDATED), DEBOUNCE, {
-    edges: ['leading', 'trailing'],
+    edges: ['trailing'],
   });
   watchStorySpecifiers(normalizedStories, { workingDir }, async (path, removed) => {
     (await storyIndexGeneratorPromise).invalidate(path, removed);

PATCH

echo "Patch applied successfully."
