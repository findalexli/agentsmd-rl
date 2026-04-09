#!/usr/bin/env bash
set -euo pipefail

cd /workspace/next.js

# Idempotent: skip if already applied
if grep -q "message.includes('dynamicIO')" packages/next/src/server/config.ts 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/packages/next/src/server/config.ts b/packages/next/src/server/config.ts
index cc5af712360c4e..8bd2e1716c46a0 100644
--- a/packages/next/src/server/config.ts
+++ b/packages/next/src/server/config.ts
@@ -84,6 +84,12 @@ function normalizeNextConfigZodErrors(
           "\nUse 'experimental.turbopackFileSystemCacheForDev' instead."
         message +=
           '\nLearn more: https://nextjs.org/docs/app/api-reference/config/next-config-js/turbopackFileSystemCache'
+      } else if (message.includes('dynamicIO')) {
+        shouldExit = true
+        message +=
+          '\n`experimental.dynamicIO` has been replaced by `cacheComponents`. Please update your next.config file accordingly.'
+        message +=
+          '\nLearn more: https://nextjs.org/docs/app/api-reference/config/next-config-js/cacheComponents'
       }
     }


PATCH

echo "Patch applied successfully."
