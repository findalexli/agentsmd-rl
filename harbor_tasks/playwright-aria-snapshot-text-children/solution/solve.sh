#!/usr/bin/env bash
set -euo pipefail

cd /workspace/playwright

# Idempotent: skip if already applied
if ! grep -q 'node.name.length > text.length' packages/injected/src/ariaSnapshot.ts 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/packages/injected/src/ariaSnapshot.ts b/packages/injected/src/ariaSnapshot.ts
index 3215c9d070fb6..08e23d585ef6a 100644
--- a/packages/injected/src/ariaSnapshot.ts
+++ b/packages/injected/src/ariaSnapshot.ts
@@ -735,9 +735,6 @@ function textContributesInfo(node: aria.AriaNode, text: string): boolean {
   if (!node.name)
     return true;

-  if (node.name.length > text.length)
-    return false;
-
   // Figure out if text adds any value. "longestCommonSubstring" is expensive, so limit strings length.
   const substr = (text.length <= 200 && node.name.length <= 200) ? longestCommonSubstring(text, node.name) : '';
   let filtered = text;

PATCH

echo "Patch applied successfully."
