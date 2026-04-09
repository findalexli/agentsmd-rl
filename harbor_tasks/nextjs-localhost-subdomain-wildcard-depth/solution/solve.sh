#!/usr/bin/env bash
set -euo pipefail

cd /workspace/next.js

# Idempotent: skip if already applied
if grep -q '\*\*\.localhost' packages/next/src/server/lib/router-utils/block-cross-site-dev.ts 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/packages/next/src/server/lib/router-utils/block-cross-site-dev.ts b/packages/next/src/server/lib/router-utils/block-cross-site-dev.ts
index 51260db36bb565..2d367bb2f2bbbe 100644
--- a/packages/next/src/server/lib/router-utils/block-cross-site-dev.ts
+++ b/packages/next/src/server/lib/router-utils/block-cross-site-dev.ts
@@ -119,7 +119,7 @@ export const blockCrossSiteDEV = (
   hostname: string | undefined
 ): boolean => {
   const allowedOrigins = [
-    '*.localhost',
+    '**.localhost',
     'localhost',
     ...(allowedDevOrigins ?? []),
   ]

PATCH

echo "Patch applied successfully."
