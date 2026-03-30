#!/usr/bin/env bash
set -euo pipefail
cd /workspace/gradio

cat > /tmp/patch.diff << 'PATCH'
diff --git a/gradio/utils.py b/gradio/utils.py
index 388e02960a..d0ce1b7eb5 100644
--- a/gradio/utils.py
+++ b/gradio/utils.py
@@ -254,11 +254,13 @@ def postrun(self, *_args, **_kwargs):
         demo = getattr(self.watch_module, self.demo_name)
         if demo is not self.running_app.blocks:
             self.swap_blocks(demo)
-            # TODO: re-assign keys?
-            # TODO: re-assign config?
             return True
         return False

+    def swap_blocks(self, demo: Blocks):
+        super().swap_blocks(demo)
+        demo.config = demo.get_config_file()
+

 class SourceFileReloader(ServerReloader):
     def __init__(
PATCH

git apply --check /tmp/patch.diff 2>/dev/null && git apply /tmp/patch.diff || echo "Patch already applied or conflicts (idempotent)"
