#!/usr/bin/env bash
set -euo pipefail

cd /workspace/next.js

# Idempotent: skip if already applied
if grep -q 'Registry is now flushed; rawStyledJsxInsertedHTML will be empty' packages/next/src/server/render.tsx 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/packages/next/src/server/render.tsx b/packages/next/src/server/render.tsx
index 872927b8d787c0..fdff082e4374fb 100644
--- a/packages/next/src/server/render.tsx
+++ b/packages/next/src/server/render.tsx
@@ -1385,29 +1385,22 @@ export async function renderToHTMLImpl(
       | {}
       | Awaited<ReturnType<typeof loadDocumentInitialProps>>

-    const [rawStyledJsxInsertedHTML, content] = await Promise.all([
-      renderToString(styledJsxInsertedHTML()),
-      (async () => {
-        if (hasDocumentGetInitialProps) {
-          documentInitialPropsRes = await loadDocumentInitialProps(renderShell)
-          if (documentInitialPropsRes === null) return null
-          const { docProps } = documentInitialPropsRes as any
-          return docProps.html
-        } else {
-          documentInitialPropsRes = {}
-          const stream = await renderShell(App, Component)
-          await stream.allReady
-          return streamToString(stream)
-        }
-      })(),
-    ])
-
-    if (content === null) {
-      return null
+    let content: string | null
+    if (hasDocumentGetInitialProps) {
+      documentInitialPropsRes = await loadDocumentInitialProps(renderShell)
+      if (documentInitialPropsRes === null) {
+        content = null
+      } else {
+        const { docProps } = documentInitialPropsRes as any
+        content = docProps.html
+      }
+    } else {
+      documentInitialPropsRes = {}
+      const stream = await renderShell(App, Component)
+      await stream.allReady
+      content = await streamToString(stream)
     }

-    const contentHTML = rawStyledJsxInsertedHTML + content
-
     // @ts-ignore: documentInitialPropsRes is set
     const { docProps } = (documentInitialPropsRes as any) || {}
     const documentElement = (htmlProps: any) => {
@@ -1427,6 +1420,17 @@ export async function renderToHTMLImpl(
       jsxStyleRegistry.flush()
     }

+    // Registry is now flushed; rawStyledJsxInsertedHTML will be empty.
+    const rawStyledJsxInsertedHTML = await renderToString(
+      styledJsxInsertedHTML()
+    )
+
+    if (content === null) {
+      return null
+    }
+
+    const contentHTML = rawStyledJsxInsertedHTML + content
+
     return {
       contentHTML,
       documentElement,

PATCH

echo "Patch applied successfully."
