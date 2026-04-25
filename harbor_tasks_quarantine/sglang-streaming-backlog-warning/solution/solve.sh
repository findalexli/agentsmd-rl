#!/usr/bin/env bash
set -euo pipefail

FILE="python/sglang/srt/managers/tokenizer_manager.py"

# Idempotency: check if the warning block is already removed
if ! grep -q 'Streaming backlog: rid=%s' "$FILE"; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/python/sglang/srt/managers/tokenizer_manager.py b/python/sglang/srt/managers/tokenizer_manager.py
index d7a324afd9ad..1c1efd92592c 100644
--- a/python/sglang/srt/managers/tokenizer_manager.py
+++ b/python/sglang/srt/managers/tokenizer_manager.py
@@ -1155,14 +1155,6 @@ async def _wait_one_response(
             finished = state.finished
             state.event.clear()

-            if is_stream and len(pending) > 1:
-                logger.warning(
-                    "Streaming backlog: rid=%s, draining %d queued chunks. "
-                    "This may inflate P99 TBT for affected requests.",
-                    obj.rid,
-                    len(pending),
-                )
-
             for i, out in enumerate(pending):
                 is_last = i == len(pending) - 1

PATCH

echo "Patch applied successfully."
