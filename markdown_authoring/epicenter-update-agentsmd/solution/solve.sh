#!/usr/bin/env bash
set -euo pipefail

cd /workspace/epicenter

# Idempotency guard
if grep -qF "## The Solution" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -754,11 +754,13 @@ Ready to revolutionize your workflow? Try it now!
 ## Examples: Reddit Technical Posts
 
 ### Good (Focused on Implementation)
+
 ```
 Hey r/sveltejs! Just shipped a file upload feature for Whispering and wanted to share how I implemented drag-and-drop files.
 
 I used the [FileDropZone component from shadcn-svelte-extras](https://www.shadcn-svelte-extras.com/components/file-drop-zone), which provided a clean abstraction that allows users to drop and click to upload files:
 
+``` 
 ```svelte
 <FileDropZone
   accept="{ACCEPT_AUDIO}, {ACCEPT_VIDEO}"
@@ -771,7 +773,7 @@ I used the [FileDropZone component from shadcn-svelte-extras](https://www.shadcn
   }}
 />
 ```
-
+```
 The component handles web drag-and-drop, but since Whispering is a Tauri desktop app, drag-and-drop functionality didn't work on the desktop (click-to-select still worked fine). So I reached for Tauri's [onDragDropEvent](https://tauri.app/reference/javascript/api/namespacewebviewwindow/#ondragdropevent) to add native support for dragging files anywhere into the application.
 
 You can see the [full implementation here](link) (note that the code is still somewhat messy by my standards; it is slated for cleanup!).
@@ -781,20 +783,26 @@ Whispering is a large, open-source, production Svelte 5 + Tauri app: https://git
 Feel free to check it out for more patterns! If you're building Svelte 5 apps and need file uploads, definitely check out shadcn-svelte-extras. Not affiliated, it just saved me hours of implementation time.
 
 Happy to answer any questions about the implementation!
-```
+``` 
 
 ### Bad (Marketing-Focused)
-```
+
 ## The Problem
+```
 Users were asking for file upload support...
+```
 
-## The Solution  
+## The Solution
+``` 
 I implemented a beautiful drag-and-drop interface...
+```
 
 ## Key Benefits
+``` 
 - User-friendly interface
 - Supports multiple file formats
 - Lightning-fast processing
+``` 
 
 ## Why This Matters
 This transforms the user experience...
PATCH

echo "Gold patch applied."
