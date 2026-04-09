#!/usr/bin/env bash
set -euo pipefail

cd /workspace/sglang

# Idempotent: skip if already applied (check for new import in utils.py)
if grep -q 'import hashlib' python/sglang/srt/mem_cache/utils.py 2>/dev/null | head -1; then
    echo "Patch already applied."
    exit 0
fi

# Apply the gold patch
git apply - <<'PATCH'
diff --git a/python/sglang/srt/managers/cache_controller.py b/python/sglang/srt/managers/cache_controller.py
index e4f8d0b7056f..6a735a542112 100644
--- a/python/sglang/srt/managers/cache_controller.py
+++ b/python/sglang/srt/managers/cache_controller.py
@@ -430,7 +430,7 @@ def attach_storage_backend(
         # Rollback-safe init: if creation fails, keep controller state consistent
         # for future attach attempts.
         self.storage_backend_type = storage_backend
-        from sglang.srt.mem_cache.hicache_storage import get_hash_str
+        from sglang.srt.mem_cache.utils import get_hash_str

         self.get_hash_str = get_hash_str
         self.storage_config = self._generate_storage_config(
diff --git a/python/sglang/srt/mem_cache/hicache_storage.py b/python/sglang/srt/mem_cache/hicache_storage.py
index ba88c5f61b0a..f1e5520f4012 100644
--- a/python/sglang/srt/mem_cache/hicache_storage.py
+++ b/python/sglang/srt/mem_cache/hicache_storage.py
@@ -1,4 +1,3 @@
-import hashlib
 import logging
 import os
 from abc import ABC, abstractmethod
@@ -14,37 +13,6 @@
 logger = logging.getLogger(__name__)


-def get_hash_str(token_ids: List[int], prior_hash: str = None) -> str:
-    hasher = hashlib.sha256()
-
-    if prior_hash:
-        hasher.update(bytes.fromhex(prior_hash))
-
-    for t in token_ids:
-        if isinstance(t, tuple):
-            # EAGLE bigram mode: hash both elements to uniquely identify the bigram
-            for elem in t:
-                hasher.update(elem.to_bytes(4, byteorder="little", signed=False))
-        else:
-            # Regular mode: single integer token
-            hasher.update(t.to_bytes(4, byteorder="little", signed=False))
-
-    return hasher.hexdigest()
-
-
-def hash_str_to_int64(hash_str: str) -> int:
-    """Convert SHA256 hex string to signed 64-bit integer for events.
-
-    Takes first 16 hex characters (64 bits) and converts to signed int64 range.
-    """
-    # Take first 16 hex chars to get 64-bit value
-    uint64_val = int(hash_str[:16], 16)
-    # Convert to signed int64 range [-2^63, 2^63-1]
-    if uint64_val >= 2**63:
-        return uint64_val - 2**64
-    return uint64_val
-
-
 @dataclass
 class HiCacheStorageConfig:
     tp_rank: int
diff --git a/python/sglang/srt/mem_cache/radix_cache.py b/python/sglang/srt/mem_cache/radix_cache.py
index 7d1616037243..3ad6421a1323 100644
--- a/python/sglang/srt/mem_cache/radix_cache.py
+++ b/python/sglang/srt/mem_cache/radix_cache.py
@@ -62,7 +62,7 @@ from sglang.srt.mem_cache.memory_pool import (
     PriorityStrategy,
     SLRUStrategy,
 )
-from sglang.srt.mem_cache.hicache_storage import get_hash_str, hash_str_to_int64
+from sglang.srt.mem_cache.utils import get_hash_str, hash_str_to_int64

 if TYPE_CHECKING:
     from sglang.srt.managers.schedule_batch import Req
diff --git a/python/sglang/srt/mem_cache/utils.py b/python/sglang/srt/mem_cache/utils.py
index ba08819c3c63..66012c4e7d73 100644
--- a/python/sglang/srt/mem_cache/utils.py
+++ b/python/sglang/srt/mem_cache/utils.py
@@ -13,6 +13,7 @@
 # ==============================================================================
 """Common utilities."""

+import hashlib
 from typing import Any, List, Optional, Tuple

 import torch
@@ -359,3 +360,32 @@ def convert_to_bigram_key(tokens: List[int]) -> List[Tuple[int, int]]:
     if len(tokens) < 2:
         return []
     return [(tokens[i], tokens[i + 1]) for i in range(len(tokens) - 1)]
+
+
+def get_hash_str(token_ids: List[int], prior_hash: Optional[str] = None) -> str:
+    hasher = hashlib.sha256()
+
+    if prior_hash:
+        hasher.update(bytes.fromhex(prior_hash))
+
+    for t in token_ids:
+        if isinstance(t, tuple):
+            # EAGLE bigram mode: hash both elements to uniquely identify the bigram
+            for elem in t:
+                hasher.update(elem.to_bytes(4, byteorder="little", signed=False))
+        else:
+            # Regular mode: single integer token
+            hasher.update(t.to_bytes(4, byteorder="little", signed=False))
+
+    return hasher.hexdigest()
+
+
+def hash_str_to_int64(hash_str: str) -> int:
+    """Convert SHA256 hex string to signed 64-bit integer for events.
+
+    Takes first 16 hex characters (64 bits) and converts to signed int64 range.
+    """
+    uint64_val = int(hash_str[:16], 16)
+    if uint64_val >= 2**63:
+        return uint64_val - 2**64
+    return uint64_val

PATCH

echo "Patch applied successfully."
