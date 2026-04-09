#!/bin/bash
set -e

cd /workspace/appwrite

# Apply the gold patch for CORS headers in error responses
cat <<'PATCH' | git apply -
diff --git a/app/controllers/general.php b/app/controllers/general.php
index 3bf5f027f28..3eeeef3fae9 100644
--- a/app/controllers/general.php
+++ b/app/controllers/general.php
@@ -1493,6 +1493,19 @@ function router(Http $utopia, Database $dbForPlatform, callable $getProjectDB, S
             'type' => $type,
         ];

+        // Add CORS headers to error responses so browsers can read the error.
+        // Wrapped in try-catch: if the error itself is a DB failure, resolving
+        // the cors resource (which depends on rule -> DB) would cascade.
+        // Uses override:true to avoid duplicate headers if init() already set them.
+        try {
+            $cors = $utopia->getResource('cors');
+            foreach ($cors->headers($request->getOrigin()) as $name => $value) {
+                $response->addHeader($name, $value, override: true);
+            }
+        } catch (Throwable) {
+            // Degrade gracefully - error response without CORS is no worse than before.
+        }
+
         $response
             ->addHeader('Cache-Control', 'no-cache, no-store, must-revalidate')
             ->addHeader('Expires', '0')
PATCH

# Idempotency check - verify the distinctive line exists
grep -q "Add CORS headers to error responses so browsers can read the error" app/controllers/general.php

echo "Patch applied successfully"
