#!/usr/bin/env bash
set -euo pipefail

cd /workspace/vllm

# Idempotent: skip if already applied
if grep -q '] \* self._num_ubatches' vllm/v1/worker/workspace.py 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/vllm/v1/worker/workspace.py b/vllm/v1/worker/workspace.py
index 28ba85a26248..7e21d89f7036 100644
--- a/vllm/v1/worker/workspace.py
+++ b/vllm/v1/worker/workspace.py
@@ -31,7 +31,7 @@ def _compute_bytes(shape: tuple[int, ...], dtype: torch.dtype) -> int:
 class WorkspaceManager:
     """Manager for workspace allocation.

-    Manages workspace buffers for DBO (Dual Batch Overlap) execution.
+    Manages one workspace buffer per active ubatch slot.
     Can be locked to prevent further growth during execution.
     """

@@ -39,7 +39,9 @@ def __init__(self, device: torch.device, num_ubatches: int | None = None):
         self._device = device
         # Cache num ubatches at init based on configuration (default to 1)
         self._num_ubatches = num_ubatches if num_ubatches is not None else 1
-        self._current_workspaces: list[torch.Tensor | None] = [None, None]
+        self._current_workspaces: list[torch.Tensor | None] = [
+            None
+        ] * self._num_ubatches
         self._locked: bool = False

     @staticmethod
@@ -224,7 +226,7 @@ def init_workspace_manager(

     Args:
         device: The device to allocate workspace on.
-        num_ubatches: Number of micro-batches. Defaults to 1.
+        num_ubatches: Number of workspace ubatch slots. Defaults to 1.
     """
     global _manager
     if _manager is not None:

PATCH

echo "Patch applied successfully."
