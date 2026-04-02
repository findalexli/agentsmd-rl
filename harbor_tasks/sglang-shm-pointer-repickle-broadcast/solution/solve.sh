#!/usr/bin/env bash
set -euo pipefail

cd /workspace/sglang

# Idempotency check: if materialize method already exists, patch is applied
if grep -q 'def materialize' python/sglang/srt/managers/mm_utils.py 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/python/sglang/srt/managers/mm_utils.py b/python/sglang/srt/managers/mm_utils.py
index 7cc37176a40c..1549b6112504 100644
--- a/python/sglang/srt/managers/mm_utils.py
+++ b/python/sglang/srt/managers/mm_utils.py
@@ -1627,45 +1627,28 @@ class ShmPointerMMData:
     """

     def __init__(self, tensor: torch.Tensor):
-        self.cpu_tensor = tensor.cpu().contiguous()
-        self.shape = self.cpu_tensor.shape
-        self.dtype = self.cpu_tensor.dtype
-
-        nbytes = self.cpu_tensor.numel() * self.cpu_tensor.element_size()
-
-        self.shm = shared_memory.SharedMemory(create=True, size=nbytes)
-
+        if not tensor.is_cpu:
+            tensor = tensor.cpu()
+        if not tensor.is_contiguous():
+            tensor = tensor.contiguous()
+        self.shape = tensor.shape
+        self.dtype = tensor.dtype
+        nbytes = tensor.numel() * tensor.element_size()
+        shm = shared_memory.SharedMemory(create=True, size=nbytes)
         try:
-            shm_view = np.ndarray((nbytes,), dtype=np.uint8, buffer=self.shm.buf)
-
-            shm_view[:] = self.cpu_tensor.view(torch.uint8).numpy().flatten()
-        finally:
-            self.shm.close()
+            dst = torch.frombuffer(shm.buf, dtype=torch.uint8)
+            dst.copy_(tensor.view(torch.uint8).reshape(-1))
+        except BaseException:
+            shm.close()
+            shm.unlink()
+            raise
+        self.shm_name = shm.name
+        shm.close()
+        self._shm_handle = None

     def __getstate__(self):
-        if not hasattr(self, "shm") or self.shm is None:
-            tensor = getattr(self, "cpu_tensor", None)
-            if tensor is None:
-                tensor = getattr(self, "tensor", None)
-            if tensor is None:
-                raise RuntimeError(
-                    "ShmPointerMMData cannot recreate shared memory without tensor"
-                )
-
-            cpu_tensor = tensor.cpu().contiguous()
-            self.shape = cpu_tensor.shape
-            self.dtype = cpu_tensor.dtype
-
-            nbytes = cpu_tensor.numel() * cpu_tensor.element_size()
-            self.shm = shared_memory.SharedMemory(create=True, size=nbytes)
-            try:
-                shm_view = np.ndarray((nbytes,), dtype=np.uint8, buffer=self.shm.buf)
-                shm_view[:] = cpu_tensor.view(torch.uint8).numpy().flatten()
-            finally:
-                self.shm.close()
-
         return {
-            "shm_name": self.shm.name,
+            "shm_name": self.shm_name,
             "shape": self.shape,
             "dtype": self.dtype,
         }
@@ -1675,17 +1658,29 @@ def __setstate__(self, state):
         self.shape = state["shape"]
         self.dtype = state["dtype"]
         self.shm = None
+        self._shm_handle = shared_memory.SharedMemory(name=self.shm_name)
+        # Zero-copy view into shared memory (no clone, no unlink)
+        self.tensor = torch.frombuffer(self._shm_handle.buf, dtype=self.dtype).reshape(
+            self.shape
+        )

-        shm_handle = shared_memory.SharedMemory(name=self.shm_name)
-        try:
-            self.tensor = (
-                torch.frombuffer(shm_handle.buf, dtype=self.dtype)
-                .reshape(self.shape)
-                .clone()
-            )
-        finally:
-            shm_handle.close()
-            shm_handle.unlink()
+    def materialize(self) -> torch.Tensor:
+        """Clone tensor from shm to owned memory, then release shm handle."""
+        tensor = self.tensor.clone()
+        if self._shm_handle is not None:
+            self._shm_handle.close()
+            try:
+                self._shm_handle.unlink()
+            except FileNotFoundError:
+                pass  # Another rank already unlinked
+            self._shm_handle = None
+        return tensor
+
+    def __del__(self):
+        # Only close; never unlink. Unlinking is materialize()'s job.
+        if getattr(self, "_shm_handle", None) is not None:
+            self._shm_handle.close()
+            self._shm_handle = None


 def _get_is_default_transport():
@@ -1723,12 +1718,19 @@ def wrap_shm_features(obj):
 def unwrap_shm_features(obj):
     """
     Restore ShmPointerMMData wrappers back into standard torch.Tensors.
+    Handles both single requests and batch requests.
     """
     if _get_is_default_transport() or get_global_server_args().skip_tokenizer_init:
         return obj
+    # Handle batch requests
+    if hasattr(obj, "batch"):
+        for sub_obj in obj.batch:
+            unwrap_shm_features(sub_obj)
+        return obj
+    # Handle single requests
     if hasattr(obj, "mm_inputs") and obj.mm_inputs:
         mm_items = obj.mm_inputs.get("mm_items", [])
         for item in mm_items:
             if isinstance(item.feature, ShmPointerMMData):
-                item.feature = item.feature.tensor
+                item.feature = item.feature.materialize()
     return obj
diff --git a/python/sglang/srt/managers/scheduler.py b/python/sglang/srt/managers/scheduler.py
index 539dff12a5b9..2cb755d35ace 100644
--- a/python/sglang/srt/managers/scheduler.py
+++ b/python/sglang/srt/managers/scheduler.py
@@ -1424,7 +1424,6 @@ def recv_requests(
                         if self.recv_limit_reached(len(recv_reqs)):
                             break
                         recv_req = self.recv_from_tokenizer.recv_pyobj(zmq.NOBLOCK)
-                        recv_req = unwrap_shm_features(recv_req)
                     except zmq.ZMQError:
                         break
                     recv_reqs.append(recv_req)
@@ -1511,6 +1510,13 @@ def recv_requests(
                 prepare_abort(req, error_msg, status_code=status_code)
                 self.stream_output([req], req.return_logprob)

+        # Unwrap shared memory features AFTER all broadcasts complete,
+        # so that ShmPointerMMData metadata (not full tensor data) is what
+        # gets serialized during broadcast_pyobj.
+        if recv_reqs:
+            for req in recv_reqs:
+                unwrap_shm_features(req)
+
         return recv_reqs

     def _split_work_and_control_reqs(self, recv_reqs: List):

PATCH

echo "Patch applied successfully."
