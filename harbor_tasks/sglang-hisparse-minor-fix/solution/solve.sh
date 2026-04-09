#!/usr/bin/env bash
set -euo pipefail

cd /workspace/sglang

# Idempotent: skip if already applied (check for 128-bit transfer pattern)
if grep -q 'total_pairs = item_size_bytes / 16' python/sglang/jit_kernel/csrc/hisparse.cuh 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Use --whitespace=fix if patch has trailing whitespace issues
git apply - <<'PATCH'
diff --git a/python/sglang/jit_kernel/csrc/hisparse.cuh b/python/sglang/jit_kernel/csrc/hisparse.cuh
index 2919b59ba6a4..661640cda356 100644
--- a/python/sglang/jit_kernel/csrc/hisparse.cuh
+++ b/python/sglang/jit_kernel/csrc/hisparse.cuh
@@ -24,15 +24,29 @@ __device__ __forceinline__ int hash_slot(int32_t key, int hash_size) {

 __device__ __forceinline__ void
 transfer_item_warp(int32_t lane_id, const void* src_addr, void* dst_addr, int64_t item_size_bytes) {
-  const uint64_t* __restrict__ src = static_cast<const uint64_t*>(src_addr);
-  uint64_t* __restrict__ dst = static_cast<uint64_t*>(dst_addr);
-  const int total_chunks = item_size_bytes / sizeof(uint64_t);
+  // 128-bit bulk transfer via paired 64-bit loads (avoids alignment issues with uint4)
+  const int total_pairs = item_size_bytes / 16;  // number of 16-byte chunks
+  {
+    const uint64_t* __restrict__ src = static_cast<const uint64_t*>(src_addr);
+    uint64_t* __restrict__ dst = static_cast<uint64_t*>(dst_addr);
+    for (int j = lane_id; j < total_pairs; j += WARP_SIZE) {
+      uint64_t lo, hi;
+      const uint64_t* s = src + j * 2;
+      asm volatile("ld.global.nc.v2.b64 {%0,%1},[%2];" : "=l"(lo), "=l"(hi) : "l"(s) : "memory");
+      uint64_t* d = dst + j * 2;
+      asm volatile("st.global.cg.v2.b64 [%0],{%1,%2};" ::"l"(d), "l"(lo), "l"(hi) : "memory");
+    }
+  }

-#pragma unroll
-  for (int j = lane_id; j < total_chunks; j += WARP_SIZE) {
+  // Tail: 64-bit for remaining 8-byte chunk (if item_size not multiple of 16)
+  const int tail_8B = (item_size_bytes - total_pairs * 16) / 8;
+  if (tail_8B > 0 && lane_id < tail_8B) {
+    const uint64_t* __restrict__ src8 =
+        reinterpret_cast<const uint64_t*>(static_cast<const char*>(src_addr) + total_pairs * 16);
+    uint64_t* __restrict__ dst8 = reinterpret_cast<uint64_t*>(static_cast<char*>(dst_addr) + total_pairs * 16);
     uint64_t tmp;
-    asm volatile("ld.global.nc.b64 %0,[%1];" : "=l"(tmp) : "l"(src + j) : "memory");
-    asm volatile("st.global.cg.b64 [%0],%1;" ::"l"(dst + j), "l"(tmp) : "memory");
+    asm volatile("ld.global.nc.b64 %0,[%1];" : "=l"(tmp) : "l"(src8 + lane_id) : "memory");
+    asm volatile("st.global.cg.b64 [%0],%1;" ::"l"(dst8 + lane_id), "l"(tmp) : "memory");
   }
 }

diff --git a/python/sglang/srt/managers/schedule_batch.py b/python/sglang/srt/managers/schedule_batch.py
index 0b26be6c6d18..9eeab257266b 100644
--- a/python/sglang/srt/managers/schedule_batch.py
+++ b/python/sglang/srt/managers/schedule_batch.py
@@ -2021,6 +2021,9 @@ def retract_decode(
     def release_req(self, idx: int, remaing_req_count: int, server_args: ServerArgs):
         req = self.reqs[idx]

+        if self.hisparse_coordinator is not None:
+            self.hisparse_coordinator.retract_req(req)
+
         if server_args.disaggregation_mode == "decode":
             req.offload_kv_cache(
                 self.req_to_token_pool, self.token_to_kv_pool_allocator
diff --git a/python/sglang/srt/managers/scheduler.py b/python/sglang/srt/managers/scheduler.py
index 67af2d0de943..6400f588cefa 100644
--- a/python/sglang/srt/managers/scheduler.py
+++ b/python/sglang/srt/managers/scheduler.py
@@ -2204,6 +2204,8 @@ def get_next_batch_to_run(self) -> Optional[ScheduleBatch]:
                 else:
                     self.running_batch.merge_batch(new_batch)
                 self.running_batch.hisparse_coordinator = self.hisparse_coordinator
+            # Reset batch_is_full so the scheduler can schedule more prefills.
+            self.running_batch.batch_is_full = False

         if (
             not self.enable_hisparse
@@ -2606,8 +2608,6 @@ def update_running_batch(self, batch: ScheduleBatch) -> Optional[ScheduleBatch]

             for req in retracted_reqs:
                 self._add_request_to_queue(req, is_retracted=True)
-                if self.enable_hisparse:
-                    self.hisparse_coordinator.retract_req(req)
         else:
             self.new_token_ratio = max(
                 self.new_token_ratio - self.new_token_ratio_decay,

PATCH

echo "Patch applied successfully."
