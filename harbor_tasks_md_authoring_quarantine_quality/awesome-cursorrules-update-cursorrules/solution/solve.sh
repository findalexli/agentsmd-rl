#!/usr/bin/env bash
set -euo pipefail

cd /workspace/awesome-cursorrules

# Idempotency guard
if grep -qF "rules/cursorrules-cursor-ai-nextjs-14-tailwind-seo-setup/.cursorrules" "rules/cursorrules-cursor-ai-nextjs-14-tailwind-seo-setup/.cursorrules"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/rules/cursorrules-cursor-ai-nextjs-14-tailwind-seo-setup/.cursorrules b/rules/cursorrules-cursor-ai-nextjs-14-tailwind-seo-setup/.cursorrules
@@ -119,3 +119,8 @@ You are an AI assistant specialized in generating TypeScript code for Next.js 14
    }) {
      return (
 
+
+
+    );
+  }
+  ```
PATCH

echo "Gold patch applied."
