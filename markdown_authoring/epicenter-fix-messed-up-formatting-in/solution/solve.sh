#!/usr/bin/env bash
set -euo pipefail

cd /workspace/epicenter

# Idempotency guard
if grep -qF "AGENTS.md" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -754,7 +754,7 @@ Ready to revolutionize your workflow? Try it now!
 ## Examples: Reddit Technical Posts
 
 ### Good (Focused on Implementation)
-```
+````
 Hey r/sveltejs! Just shipped a file upload feature for Whispering and wanted to share how I implemented drag-and-drop files.
 
 I used the [FileDropZone component from shadcn-svelte-extras](https://www.shadcn-svelte-extras.com/components/file-drop-zone), which provided a clean abstraction that allows users to drop and click to upload files:
@@ -781,7 +781,7 @@ Whispering is a large, open-source, production Svelte 5 + Tauri app: https://git
 Feel free to check it out for more patterns! If you're building Svelte 5 apps and need file uploads, definitely check out shadcn-svelte-extras. Not affiliated, it just saved me hours of implementation time.
 
 Happy to answer any questions about the implementation!
-``` 
+```` 
 
 ### Bad (Marketing-Focused)
 ```
@@ -943,7 +943,7 @@ To accomplish this, I wrapped the `{@render children?.()}` in a `<div class="fle
 - **Use "we" for team decisions, "I" for personal observations**
 
 #### Example PR Description:
-```
+````
 This fixes the long-standing issue with nested reactivity in state management. 
 
 First, some context: users have consistently found it cumbersome to create deeply reactive state. The current approach requires manual get/set properties, which doesn't feel sufficiently Svelte-like. Meanwhile, we want to move away from object mutation for future performance optimizations, but `obj = { ...obj, x: obj.x + 1 }` is ugly and creates overhead.
@@ -963,7 +963,7 @@ Still TODO:
 - Migration guide for existing codebases
 
 This doubles down on Svelte's philosophy of writing less, more intuitive code while setting us up for the fine-grained reactivity improvements planned for v6.
-```
+````
 
 #### What to Avoid
 - Bullet points or structured lists
PATCH

echo "Gold patch applied."
