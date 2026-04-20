#!/bin/bash
set -e

cd /workspace/storybook

# Apply the gold patch to fix the hash collision bug
git apply <<'PATCH'
diff --git a/code/builders/builder-vite/src/codegen-project-annotations.ts b/code/builders/builder-vite/src/codegen-project-annotations.ts
index 50e95b0..4a7c4e5 100644
--- a/code/builders/builder-vite/src/codegen-project-annotations.ts
+++ b/code/builders/builder-vite/src/codegen-project-annotations.ts
@@ -105,6 +105,11 @@ export function generateProjectAnnotationsCodeFromPreviews(options: {
   `.trim();
 }

+/** djb2 hash — http://www.cse.yorku.ca/~oz/hash.html */
 function hash(value: string) {
-  return value.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0);
+  let acc = 5381;
+  for (let i = 0; i < value.length; i++) {
+    acc = ((acc << 5) + acc + value.charCodeAt(i)) >>> 0;
+  }
+  return acc;
 }
PATCH

# Idempotency check - verify the distinctive line from the patch is present
grep -q "acc = ((acc << 5) + acc + value.charCodeAt(i)) >>> 0" code/builders/builder-vite/src/codegen-project-annotations.ts