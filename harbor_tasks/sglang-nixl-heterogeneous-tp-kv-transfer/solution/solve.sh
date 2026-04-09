#!/usr/bin/env bash
set -euo pipefail

cd /workspace/sglang

# Idempotent: skip if already applied (check for the distinctive line with engine_rank in notification)
if grep -q 'notif = f"{req.room}_kv_{chunk_id}_{int(is_last)}_{self.kv_args.engine_rank}"' python/sglang/srt/disaggregation/nixl/conn.py 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Apply the gold patch for NIXL heterogeneous TP KV transfer fix
git apply - <<'PATCH'
diff --git a/python/sglang/srt/disaggregation/nixl/conn.py b/python/sglang/srt/disaggregation/nixl/conn.py
index 38a4d15cf048..f84353f6dc12 100644
--- a/python/sglang/srt/disaggregation/nixl/conn.py
+++ b/python/sglang/srt/disaggregation/nixl/conn.py
@@ -477,25 +477,35 @@ def send_kvcache_slice(
         # Get configuration from kv_args
         local_tp_rank_in_group = self.kv_args.engine_rank % prefill_tp_size
         dst_tp_rank_in_group = decode_tp_rank % decode_tp_size
-        num_kv_heads = self.kv_args.kv_head_num
-
-        # Calculate head distribution
-        src_heads_per_rank = num_kv_heads
-        dst_heads_per_rank = num_kv_heads * prefill_tp_size // decode_tp_size

         src_kv_item_len = self.kv_args.kv_item_lens[0]
         page_size = self.kv_args.page_size

+        # Use total KV head count (not per-rank) for correct head distribution.
+        # Per-rank kv_head_num is max(1, total//tp) which loses info when total < tp.
+        total_kv_heads = getattr(self.kv_args, "total_kv_head_num", 0)
+        if total_kv_heads <= 0:
+            total_kv_heads = self.kv_args.kv_head_num * prefill_tp_size
+
+        src_heads_per_rank = max(1, total_kv_heads // prefill_tp_size)
+        dst_heads_per_rank = max(1, total_kv_heads // decode_tp_size)
+
         bytes_per_head_slice_to_send = (
             dst_kv_item_len // page_size // dst_heads_per_rank
         )

+        # GQA replication: how many prefill ranks share the same KV head
+        src_replication = max(1, prefill_tp_size // total_kv_heads)
+
         # Determine which heads to send
         if prefill_tp_size > decode_tp_size:
             # Multiple prefill ranks to one decode rank
             src_head_start_offset = 0
             num_heads_to_send = src_heads_per_rank
-            dst_head_start_offset = local_tp_rank_in_group * src_heads_per_rank
+            unique_head_idx = local_tp_rank_in_group // src_replication
+            dst_head_start_offset = (
+                unique_head_idx * src_heads_per_rank
+            ) % dst_heads_per_rank
         else:
             # Send KVCache from 1 prefill instance to multiple decode instances
             src_head_start_offset = (
@@ -748,7 +758,9 @@ def add_transfer_request(
             assert len(chunked_dst_kv_indice) == len(kv_indices)
             assert req.agent_name in self.decode_kv_args_table

-            notif = f"{req.room}_kv_{chunk_id}_{int(is_last)}_{self.kv_args.pp_rank}"
+            notif = (
+                f"{req.room}_kv_{chunk_id}_{int(is_last)}_{self.kv_args.engine_rank}"
+            )
             decode_tp_size = self.decode_kv_args_table[req.agent_name].decode_tp_size

             if self.is_mla_backend or (decode_tp_size == self.attn_tp_size):
@@ -789,7 +801,7 @@ def add_transfer_request(
                         dst_info.dst_state_data_ptrs,
                         req.dst_state_indices,
                         dst_info.gpu_id,
-                        f"{req.room}_state_{self.kv_args.pp_rank}",
+                        f"{req.room}_state_{self.kv_args.engine_rank}",
                         decode_tp_size,
                     )
                     if state_xfer_handle is not None:

PATCH

echo "Patch applied successfully."
