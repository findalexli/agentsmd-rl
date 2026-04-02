#!/usr/bin/env bash
set -euo pipefail

cd /workspace/gradio

# Idempotency check: if safe_aclose_iterator is already called in cancel_event, skip
if grep -q 'safe_aclose_iterator' gradio/routes.py; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/gradio/routes.py b/gradio/routes.py
index 577714aaa3..e30873737c 100644
--- a/gradio/routes.py
+++ b/gradio/routes.py
@@ -126,6 +126,7 @@
     get_node_path,
     get_package_version,
     get_upload_folder,
+    safe_aclose_iterator,
 )

 if TYPE_CHECKING:
@@ -1454,6 +1455,10 @@ async def cancel_event(body: CancelBody):
                 ].put_nowait(message)
             if body.event_id in app.iterators:
                 async with app.lock:
+                    try:
+                        await safe_aclose_iterator(app.iterators[body.event_id])
+                    except Exception:
+                        pass
                     del app.iterators[body.event_id]
                     app.iterators_to_reset.add(body.event_id)
             return {"success": True}

PATCH

echo "Patch applied successfully."
