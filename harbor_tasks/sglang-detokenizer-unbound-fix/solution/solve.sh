#!/usr/bin/env bash
set -euo pipefail
cd /workspace/sglang

FILE=python/sglang/srt/managers/detokenizer_manager.py

# Idempotent: skip if already applied
grep -q '^\s*manager = None' "$FILE" && exit 0

git apply - <<'PATCH'
diff --git a/python/sglang/srt/managers/detokenizer_manager.py b/python/sglang/srt/managers/detokenizer_manager.py
index 6c78a080d93e..17972005ffed 100644
--- a/python/sglang/srt/managers/detokenizer_manager.py
+++ b/python/sglang/srt/managers/detokenizer_manager.py
@@ -435,6 +435,7 @@ def run_detokenizer_process(
     configure_logger(server_args)
     parent_process = psutil.Process().parent()

+    manager = None
     try:
         manager = detokenizer_manager_class(server_args, port_args)
         if server_args.tokenizer_worker_num == 1:
@@ -444,5 +445,6 @@ def run_detokenizer_process(
     except Exception:
         traceback = get_exception_traceback()
         logger.error(f"DetokenizerManager hit an exception: {traceback}")
-        manager.maybe_clear_socket_mapping()
+        if manager is not None:
+            manager.maybe_clear_socket_mapping()
         parent_process.send_signal(signal.SIGQUIT)

PATCH
