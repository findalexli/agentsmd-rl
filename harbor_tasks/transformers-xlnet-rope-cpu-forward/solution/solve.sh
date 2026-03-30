#!/usr/bin/env bash
set -euo pipefail
cd /workspace/transformers

cat > /tmp/patch.diff << 'PATCH'
diff --git a/src/transformers/models/xlnet/modeling_xlnet.py b/src/transformers/models/xlnet/modeling_xlnet.py
index 01486934ac37..702989331287 100755
--- a/src/transformers/models/xlnet/modeling_xlnet.py
+++ b/src/transformers/models/xlnet/modeling_xlnet.py
@@ -937,9 +937,9 @@ def positional_embedding(pos_seq, inv_freq, bsz=None):

         return pos_emb

-    def relative_positional_encoding(self, qlen, klen, bsz=None):
+    def relative_positional_encoding(self, qlen, klen, bsz=None, device=None):
         # create relative positional encoding.
-        freq_seq = torch.arange(0, self.d_model, 2.0, dtype=torch.int64).float()
+        freq_seq = torch.arange(0, self.d_model, 2.0, dtype=torch.int64, device=device).float()
         inv_freq = 1 / torch.pow(10000, (freq_seq / self.d_model))

         if self.attn_type == "bi":
@@ -952,8 +952,8 @@ def relative_positional_encoding(self, qlen, klen, bsz=None):
             raise ValueError(f"Unknown `attn_type` {self.attn_type}.")

         if self.bi_data:
-            fwd_pos_seq = torch.arange(beg, end, -1.0, dtype=torch.int64).float()
-            bwd_pos_seq = torch.arange(-beg, -end, 1.0, dtype=torch.int64).float()
+            fwd_pos_seq = torch.arange(beg, end, -1.0, dtype=torch.int64, device=device).float()
+            bwd_pos_seq = torch.arange(-beg, -end, 1.0, dtype=torch.int64, device=device).float()

             if self.clamp_len > 0:
                 fwd_pos_seq = fwd_pos_seq.clamp(-self.clamp_len, self.clamp_len)
@@ -968,7 +968,7 @@ def relative_positional_encoding(self, qlen, klen, bsz=None):

             pos_emb = torch.cat([fwd_pos_emb, bwd_pos_emb], dim=1)
         else:
-            fwd_pos_seq = torch.arange(beg, end, -1.0, dtype=torch.int64).float()
+            fwd_pos_seq = torch.arange(beg, end, -1.0, dtype=torch.int64, device=device).float()
             if self.clamp_len > 0:
                 fwd_pos_seq = fwd_pos_seq.clamp(-self.clamp_len, self.clamp_len)
             pos_emb = self.positional_embedding(fwd_pos_seq, inv_freq, bsz)
@@ -1139,8 +1139,7 @@ def forward(
             seg_mat = None

         # Positional encoding
-        pos_emb = self.relative_positional_encoding(qlen, klen, bsz=bsz)
-        pos_emb = pos_emb.to(output_h.device)
+        pos_emb = self.relative_positional_encoding(qlen, klen, bsz=bsz, device=output_h.device)
         pos_emb = self.dropout(pos_emb)

         new_mems = ()
PATCH

git apply --check /tmp/patch.diff 2>/dev/null && git apply /tmp/patch.diff || echo "Patch already applied or conflicts (idempotent)"
