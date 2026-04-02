#!/usr/bin/env bash
set -euo pipefail
cd /workspace/sglang

# Idempotency: check if the is_empty() guard exists specifically within pause_generation
if python3 -c "
import ast, sys
src = open('python/sglang/srt/managers/scheduler.py').read()
tree = ast.parse(src)
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == 'pause_generation':
        chunk = src.splitlines()[node.lineno-1:node.end_lineno]
        body = '\n'.join(chunk)
        if 'if not self.last_batch.is_empty()' in body:
            sys.exit(0)
sys.exit(1)
" 2>/dev/null; then
    echo "Patch already applied."; exit 0
fi

git apply - <<'PATCH'
diff --git a/python/sglang/srt/managers/scheduler.py b/python/sglang/srt/managers/scheduler.py
index 3e6924807ce1..539dff12a5b9 100644
--- a/python/sglang/srt/managers/scheduler.py
+++ b/python/sglang/srt/managers/scheduler.py
@@ -3246,7 +3246,11 @@ def pause_generation(self, recv_req: PauseGenerationReqInput):
             self.last_batch.filter_batch(
                 chunked_req_to_exclude=list(chunked_req_to_exclude)
             )
-            self.running_batch.merge_batch(self.last_batch)
+            if not self.last_batch.is_empty():
+                if self.running_batch.is_empty():
+                    self.running_batch = self.last_batch
+                else:
+                    self.running_batch.merge_batch(self.last_batch)
 
         self.last_batch = None
         self.cur_batch = None

PATCH
