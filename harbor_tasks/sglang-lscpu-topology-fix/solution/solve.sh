#!/usr/bin/env bash
set -euo pipefail
cd /workspace/sglang

# Idempotent: skip if already applied
grep -q 'if len(parts) != 4:' python/sglang/srt/utils/common.py && exit 0

git apply - <<'PATCH'
diff --git a/python/sglang/srt/utils/common.py b/python/sglang/srt/utils/common.py
index 53a8c6762953..ed48bd4f2e47 100644
--- a/python/sglang/srt/utils/common.py
+++ b/python/sglang/srt/utils/common.py
@@ -3378,7 +3378,12 @@ def parse_lscpu_topology():
     cpu_info = []
     for line in output.splitlines():
         if not line.startswith("#"):
-            cpu, core, socket, node = map(int, line.strip().split(","))
+            parts = line.strip().split(",")
+            if len(parts) != 4:
+                logger.warning("Skipping malformed lscpu line: %s", line.strip())
+                continue
+            cpu = int(parts[0])  # CPU id must always be present
+            core, socket, node = [int(p) if p else 0 for p in parts[1:]]
             cpu_info.append((cpu, core, socket, node))

     # [(0,0,0,0),(1,1,0,0),...,(43,43,0,1),...,(256,0,0,0),...]

PATCH
