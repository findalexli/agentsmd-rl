#!/usr/bin/env bash
set -euo pipefail
cd /workspace/gradio

# Idempotent: skip if already applied (check for the max(demo.blocks.keys()) pattern)
grep -q 'max(demo.blocks.keys())' gradio/utils.py && exit 0

git apply - <<'PATCH'
diff --git a/gradio/utils.py b/gradio/utils.py
index 11840bdd95..b243bf1bf8 100644
--- a/gradio/utils.py
+++ b/gradio/utils.py
@@ -401,6 +401,16 @@ def is_in_watch_dirs_and_not_sitepackages(file_path):

     Context.id = 0
     exec(no_reload_source_code, module.__dict__)
+    # After re-executing the module, ensure Context.id is higher than all
+    # existing block IDs. When child modules (e.g., pages in a multi-page app)
+    # are already imported and not re-executed, their blocks retain their
+    # original IDs. Without this adjustment, dynamically created blocks
+    # (e.g., from gr.render) may receive IDs that collide with existing blocks,
+    # causing DuplicateBlockError.
+    # See https://github.com/gradio-app/gradio/issues/12078
+    demo = getattr(module, reloader.demo_name, None)
+    if demo is not None and hasattr(demo, "blocks") and demo.blocks:
+        Context.id = max(Context.id, max(demo.blocks.keys()) + 1)
     sys.modules[reloader.watch_module_name] = module

     while reloader.should_watch():

PATCH
