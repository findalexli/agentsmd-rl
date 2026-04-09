#!/usr/bin/env bash
set -euo pipefail

cd /workspace/gradio

# Idempotent: skip if already applied (check specifically in predict function context)
if grep -A2 'def predict(' gradio/routes.py | grep -q 'route_path=request.url.path'; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/gradio/routes.py b/gradio/routes.py
index 7eafed73bbe..382908db2fd 100644
--- a/gradio/routes.py
+++ b/gradio/routes.py
@@ -1320,7 +1320,7 @@ async def predict(
             )
             root_path = route_utils.get_root_url(
                 request=request,
-                route_path=f"{API_PREFIX}/api/{api_name}",
+                route_path=request.url.path,
                 root_path=app.root_path,
             )
             try:

PATCH

echo "Patch applied successfully."
