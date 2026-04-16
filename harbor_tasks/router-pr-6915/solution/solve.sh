#!/bin/bash
set -e

cd /workspace/router

# Idempotency check - skip if already patched
if grep -q "replace(/\\\\\\\\/g, '\\\\\\\\\\\\\\\\'" scripts/llms-generate.mjs 2>/dev/null; then
    echo "Patch already applied, skipping."
    exit 0
fi

# Apply the gold patch
patch -p1 <<'PATCH'
diff --git a/scripts/llms-generate.mjs b/scripts/llms-generate.mjs
index a6debd16d0c..6c25fb6acf2 100755
--- a/scripts/llms-generate.mjs
+++ b/scripts/llms-generate.mjs
@@ -86,7 +86,10 @@ function extractFrontMatter(content) {
 }

 function sanitizeMarkdown(markdownContent) {
-  return markdownContent.replace(/`/g, '\\`').replace(/\$\{/g, '\\${')
+  return markdownContent
+    .replace(/\\/g, '\\\\')
+    .replace(/`/g, '\\`')
+    .replace(/\$\{/g, '\\${')
 }

 function convertMarkdownToTypeScriptESM(markdownContent) {
PATCH

echo "Patch applied successfully."
