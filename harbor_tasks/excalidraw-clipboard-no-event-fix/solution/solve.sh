#!/bin/bash
set -e

cd /workspace/excalidraw

# Idempotency check - if already patched, exit
if grep -q "const plainTextEntry = entries.find" packages/excalidraw/clipboard.ts; then
    echo "Patch already applied, exiting"
    exit 0
fi

# Apply the gold patch for clipboard.ts fix
patch -p1 <<'PATCH'
diff --git a/packages/excalidraw/clipboard.ts b/packages/excalidraw/clipboard.ts
--- a/packages/excalidraw/clipboard.ts
+++ b/packages/excalidraw/clipboard.ts
@@ -635,13 +635,13 @@ export const copyTextToSystemClipboard = async <
           throw new Error("Failed to setData on clipboardEvent");
         }
       }
+      return;
     }
-    return;
   } catch (error: any) {
     console.error(error);
   }

-  let plainTextEntry = entries.find(
+  const plainTextEntry = entries.find(
     ([mimeType]) => mimeType === MIME_TYPES.text,
   );

@@ -653,9 +653,7 @@ export const copyTextToSystemClipboard = async <
       // NOTE: doesn't work on FF on non-HTTPS domains, or when document
       // not focused
       await navigator.clipboard.writeText(plainTextEntry[1]);
-
-      // invalidate it so we don't write it again below
-      plainTextEntry = undefined;
+      return;
     } catch (error: any) {
       console.error(error);
     }
diff --git a/packages/excalidraw/components/FilledButton.scss b/packages/excalidraw/components/FilledButton.scss
--- a/packages/excalidraw/components/FilledButton.scss
+++ b/packages/excalidraw/components/FilledButton.scss
@@ -53,6 +53,7 @@
     &.ExcButton--status-loading,
     &.ExcButton--status-success {
       pointer-events: none;
+      background-color: var(--color-success);

       .ExcButton__contents {
         visibility: hidden;
PATCH

echo "Patch applied successfully"
