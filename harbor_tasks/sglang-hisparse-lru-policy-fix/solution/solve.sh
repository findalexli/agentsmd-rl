#!/usr/bin/env bash
set -euo pipefail

cd /workspace/sglang

# Idempotent: skip if already applied (check for the distinctive miss handling in the write-back)
if grep -q 'if (i < total_misses)' python/sglang/jit_kernel/csrc/hisparse.cuh 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Apply the hisparse LRU policy fix
git apply - <<'PATCH'
diff --git a/python/sglang/jit_kernel/csrc/hisparse.cuh b/python/sglang/jit_kernel/csrc/hisparse.cuh
index 661640cda356..998ce2e25d0d 100644
--- a/python/sglang/jit_kernel/csrc/hisparse.cuh
+++ b/python/sglang/jit_kernel/csrc/hisparse.cuh
@@ -281,20 +281,6 @@ __global__ void load_cache_to_device_buffer_kernel(
   }
   __syncthreads();

-  // Write back LRU order: evictables at front (LRU), hits at back (MRU).
-  {
-    const int total_evictable = HOT_BUFFER_SIZE - s_total_hits;
-    for (int i = tid; i < HOT_BUFFER_SIZE; i += BLOCK_SIZE) {
-      if (i < total_evictable) {
-        // Evictables: source at backward end, dest at LRU front
-        req_lru_slots[i] = s_lru_slots_out[HOT_BUFFER_SIZE - 1 - i];
-      } else {
-        // Hits: source at forward end, dest at MRU back
-        req_lru_slots[i] = s_lru_slots_out[i - total_evictable];
-      }
-    }
-  }
-
   // Reset offsets for the miss counting phase (only NUM_TOKEN_CHUNKS + 1 entries needed).
   for (int i = tid; i < NUM_TOKEN_CHUNKS + 1; i += BLOCK_SIZE) {
     s_chunk_offset[i] = 0;
@@ -351,6 +337,23 @@ __global__ void load_cache_to_device_buffer_kernel(
   __syncthreads();

   total_misses = NUM_TOP_K - s_total_hits - s_newest_hit;
+  // Write back LRU order: evictables at front (LRU), hits at back (MRU).
+  {
+    const int total_evictable = HOT_BUFFER_SIZE - s_total_hits;
+    for (int i = tid; i < HOT_BUFFER_SIZE; i += BLOCK_SIZE) {
+      if (i < total_misses) {
+        // Misses: just loaded from host, place right before hits
+        req_lru_slots[total_evictable - total_misses + i] = s_lru_slots_out[HOT_BUFFER_SIZE - 1 - i];
+      } else if (i < total_evictable) {
+        // Remaining evictables: truly stale, dest at LRU front
+        req_lru_slots[i - total_misses] = s_lru_slots_out[HOT_BUFFER_SIZE - 1 - i];
+      } else {
+        // Hits: source at forward end, dest at MRU back
+        req_lru_slots[i] = s_lru_slots_out[i - total_evictable];
+      }
+    }
+  }
+
   // each warp copies one miss directly, can be separated into a new kernel if parallelism is a concern
   for (int miss_idx = warp_id; miss_idx < total_misses; miss_idx += NUM_WARPS) {
     const int32_t miss_token = s_top_k_tokens[miss_idx];

PATCH

echo "Patch applied successfully."
