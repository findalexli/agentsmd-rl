#!/bin/bash
set -euo pipefail

cd /workspace/react

# Check if already applied (idempotency)
if grep -q '"\\^10.0.0"' packages/eslint-plugin-react-hooks/package.json 2>/dev/null; then
    echo "Patch already applied (ESLint v10 support exists)"
    exit 0
fi

# Apply the gold patch for ESLint v10 peer dependency support
git apply - <<'PATCH'
diff --git a/packages/eslint-plugin-react-hooks/package.json b/packages/eslint-plugin-react-hooks/package.json
index 9a8f8ac353ff..3e436421b3d3 100644
--- a/packages/eslint-plugin-react-hooks/package.json
+++ b/packages/eslint-plugin-react-hooks/package.json
@@ -36,7 +36,7 @@
   },
   "homepage": "https://react.dev/",
   "peerDependencies": {
-    "eslint": "^3.0.0 || ^4.0.0 || ^5.0.0 || ^6.0.0 || ^7.0.0 || ^8.0.0-0 || ^9.0.0"
+    "eslint": "^3.0.0 || ^4.0.0 || ^5.0.0 || ^6.0.0 || ^7.0.0 || ^8.0.0-0 || ^9.0.0 || ^10.0.0"
   },
   "dependencies": {
     "@babel/core": "^7.24.4",
PATCH

echo "Patch applied successfully"
