#!/usr/bin/env bash
set -euo pipefail

cd /workspace/slime

# Idempotent: skip if already applied
if grep -q 'host_total_GB' slime/utils/memory_utils.py 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/slime/utils/memory_utils.py b/slime/utils/memory_utils.py
index c12f3cd0b..d4b2d8932 100644
--- a/slime/utils/memory_utils.py
+++ b/slime/utils/memory_utils.py
@@ -1,6 +1,7 @@
 import gc
 import logging

+import psutil
 import torch
 import torch.distributed as dist

@@ -18,6 +19,7 @@ def clear_memory(clear_host_memory: bool = False):
 def available_memory():
     device = torch.cuda.current_device()
     free, total = torch.cuda.mem_get_info(device)
+    vm = psutil.virtual_memory()
     return {
         "gpu": str(device),
         "total_GB": _byte_to_gb(total),
@@ -25,6 +27,10 @@ def available_memory():
         "used_GB": _byte_to_gb(total - free),
         "allocated_GB": _byte_to_gb(torch.cuda.memory_allocated(device)),
         "reserved_GB": _byte_to_gb(torch.cuda.memory_reserved(device)),
+        "host_total_GB": _byte_to_gb(vm.total),
+        "host_available_GB": _byte_to_gb(vm.available),
+        "host_used_GB": _byte_to_gb(vm.used),
+        "host_free_GB": _byte_to_gb(vm.free),
     }

PATCH

echo "Patch applied successfully."
