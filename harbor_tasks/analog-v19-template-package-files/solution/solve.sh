#!/usr/bin/env bash
set -euo pipefail

cd /workspace/analog

# Idempotent: skip if already applied
if grep -q 'template-angular-v19' packages/create-analog/package.json 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Apply the gold patch: add template-angular-v19 to files array
git apply - <<'PATCH'
diff --git a/packages/create-analog/package.json b/packages/create-analog/package.json
index 592e17da1..28ebcf631 100644
--- a/packages/create-analog/package.json
+++ b/packages/create-analog/package.json
@@ -13,6 +13,7 @@
     "template-angular-v16",
     "template-angular-v17",
     "template-angular-v18",
+    "template-angular-v19",
     "template-blog",
     "template-latest",
     "template-minimal",

PATCH

echo "Patch applied successfully."
