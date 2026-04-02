#!/usr/bin/env bash
set -euo pipefail
cd /workspace/slime

# Idempotent: skip if already applied
if grep -q 'hasattr(server_args, "encoder_only")' slime/backends/sglang_utils/sglang_engine.py; then
    echo "Patch already applied"
    exit 0
fi

git apply - <<'PATCH'
diff --git a/slime/backends/sglang_utils/sglang_engine.py b/slime/backends/sglang_utils/sglang_engine.py
index 0c3430a54..96bbe1900 100644
--- a/slime/backends/sglang_utils/sglang_engine.py
+++ b/slime/backends/sglang_utils/sglang_engine.py
@@ -51,7 +51,7 @@ def _to_local_gpu_id(physical_gpu_id: int) -> int:


 def launch_server_process(server_args: ServerArgs) -> multiprocessing.Process:
-    if server_args.encoder_only:
+    if hasattr(server_args, "encoder_only") and server_args.encoder_only:
         from sglang.srt.disaggregation.encode_server import launch_server
     else:
         from sglang.srt.entrypoints.http_server import launch_server

PATCH
